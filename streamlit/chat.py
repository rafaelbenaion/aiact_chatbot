import  streamlit               as     st
from    streamlit.components.v1 import html
import  requests
import  re
import  base64

# ----------------------------------------------------------------------------------------------- #
# Load your image file in binary
# ----------------------------------------------------------------------------------------------- #
with open("smiling-ai.png", "rb") as f:
    img_bytes = f.read()

# ----------------------------------------------------------------------------------------------- #
# Encode it to base64
# ----------------------------------------------------------------------------------------------- #
encoded_image = base64.b64encode(img_bytes).decode()

# ----------------------------------------------------------------------------------------------- #
# Custom CSS for styling
# ----------------------------------------------------------------------------------------------- #
custom_css = """
<style>
    #ai-compliance-agent {
        color: color(srgb 0.842 0.3721 1);
    }
    /* Main background */
    .main, body {
        background-color: #003366 !important;
    }
    
    /* Logo positioning */
    .logo-container {
        position: absolute;
        top: 0px;
        left: 10px;
        z-index: 1000;
        padding: 40px;
    }
    
    /* EU stars animation */
    @keyframes spin {
        from {transform: rotate(0deg);}
        to {transform: rotate(360deg);}
    }
    
    .stars-animation {
        animation: spin 2s linear infinite;
        width: 50px;
        height: 50px;
    }
    
    /* Loading animation replacement */
    div.stSpinner > div {
        background: url('https://europa.eu/european-union/sites/europaeu/files/docs/body/flag_rgb_0.png') no-repeat center center;
        background-size: contain;
        width: 50px !important;
        height: 50px !important;
        animation: spin 1s linear infinite;
    }
    
    /* Content container */
    .main .block-container {
        padding-top: 80px;
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        margin: 20px;
        padding: 2rem;
    }
    
    /* Footer stars */
    .eu-stars {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
</style>
"""
# ----------------------------------------------------------------------------------------------- #
# Add logo and favicon
# ----------------------------------------------------------------------------------------------- #

logo_html = f"""
<div class="logo-container">
    <img src="data:image/png;base64,{encoded_image}" height="70">
</div>

<script>
// Set favicon
document.querySelector('link[rel="shortcut icon"]').href = "smiling-ai.png";
</script>
"""

# ----------------------------------------------------------------------------------------------- #
# Add custom CSS and logo
# ----------------------------------------------------------------------------------------------- #

st.markdown(custom_css, unsafe_allow_html=True)
html(logo_html, height=80)

def detect_risk_level(text):

    # ------------------------------------------------------------------------------------------- #
    # Improved regex to capture full risk categories with spacing variations
    # ------------------------------------------------------------------------------------------- #
    pattern = r"\b(prohibited|high[- \s]+risk|limited[- \s]+risk|minimal[- \s]+risk)\b"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    
    if matches:

        # --------------------------------------------------------------------------------------- #
        # Normalize the detected risk (remove spaces, lowercase)
        # --------------------------------------------------------------------------------------- #

        detected = matches[0].lower().replace("-", " ").replace("  ", " ")
        if detected == "prohibited":
            return "Prohibited"
        elif detected == "high risk":
            return "High Risk"
        elif detected == "limited risk":
            return "Limited Risk"
        elif detected == "minimal risk":
            return "Minimal Risk"
    return "Unknown"

def risk_scale(detected_risk):

    # -------------------------------------------------------------------------------------------- #
    # Define positions and colors for the arrow
    # -------------------------------------------------------------------------------------------- #

    position_mapping = {
        "Prohibited": "12.5%",
        "High Risk": "37.5%",
        "Limited Risk": "62.5%",
        "Minimal Risk": "87.5%",
        "Unknown": "100%"
    }
    
    color_mapping = {
        "Prohibited": "#ff0000",
        "High Risk": "#ff8f00",
        "Limited Risk": "#ffe144",
        "Minimal Risk": "#008000",
        "Unknown": "#616161"
    }
    
    arrow_color     = "black"
    arrow_position  = position_mapping.get(detected_risk, "100%")
    
    return f"""
    <style>
        .risk-scale {{
            width: 100%;
            height: 20px;
            background: linear-gradient(90deg, 
                #ff0000 0% 25%, 
                #ff8f00 25% 50%, 
                #ffe144 50% 75%, 
                #008000 75% 100%);
            border-radius: 10px;
            margin: 1rem 0;
            position: relative;
        }}
        .risk-arrow {{
            position: absolute;
            left: {arrow_position};
            transform: translateX(-50%);
            width: 0; 
            height: 0; 
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 15px solid {arrow_color};
            filter: drop-shadow(0 2px 2px rgba(0,0,0,0.3));
            transition: left 0.3s ease;
        }}
        .risk-labels {{
            display: flex;
            justify-content: space-between;
            margin: 0.5rem 0 2rem 0;
            color: rgba(255, 255, 255, 0.9);
        }}
    </style>
    
    <div class="risk-scale">
        <div class="risk-arrow"></div>
    </div>
    <div class="risk-labels">
        <span>Prohibited</span>
        <span>High Risk</span>
        <span>Limited Risk</span>
        <span>Minimal Risk</span>
    </div>
    """

# ----------------------------------------------------------------------------------------------- #
# Title for the web app
# ----------------------------------------------------------------------------------------------- #
st.title("AI Compliance Agent")

# ----------------------------------------------------------------------------------------------- #
# Description of the application
# ----------------------------------------------------------------------------------------------- #
st.markdown("""
This agent provides insights and compliance information for AI-powered projects. 
You can input your project description, and the agent will analyze it and provide key functionalities, compliance guidance, and risk assessment.
""")

# ----------------------------------------------------------------------------------------------- #
# Input area for the user to provide project details
# ----------------------------------------------------------------------------------------------- #
project_description = st.text_area("Enter your project description:")

if st.button("Analyze"):
    if project_description.strip():

        # --------------------------------------------------------------------------------------- #
        # Make API request to the agent
        # --------------------------------------------------------------------------------------- #

        payload = {
            "project_description": project_description,
            "max_length": 100000,
        }

        try:

            # ----------------------------------------------------------------------------------- #
            # Replace with your API endpoint
            # ----------------------------------------------------------------------------------- #

            api_endpoint    = "http://0.0.0.0:8000/chat/aiact"
            response        = requests.post(api_endpoint, json=payload)
            response_data   = response.json()

            # ----------------------------------------------------------------------------------- #
            # Display sections
            # ----------------------------------------------------------------------------------- #

            st.subheader("Key Functionalities")
            st.markdown(response_data.get("key_functionalities", "No data available."))

            # ----------------------------------------------------------------------------------- #
            # Risk Level Section
            # ----------------------------------------------------------------------------------- #

            st.subheader("Risk Level")
            
            # ----------------------------------------------------------------------------------- #
            # Add the risk scale
            # ----------------------------------------------------------------------------------- #

            risk_text       = response_data.get("risk_level", "No data available.")
            detected_risk   = detect_risk_level(risk_text)

            st.markdown(risk_scale(detected_risk), unsafe_allow_html=True)

            # ----------------------------------------------------------------------------------- #
            # Define color mapping with RGBA transparency
            # ----------------------------------------------------------------------------------- # 

            color_mapping = {
                "Prohibited": "rgba(255, 0, 0, 0.5)",
                "High Risk": "rgba(255, 143, 0, 0.5)",
                "Limited Risk": "rgba(255, 225, 68, 0.5)",
                "Minimal Risk": "rgba(0, 128, 0, 0.5)",
                "Unknown": "rgba(0, 0, 0, 0.3)"
            }

            # ----------------------------------------------------------------------------------- #
            # Create styled banner
            # ----------------------------------------------------------------------------------- #

            color   = color_mapping.get(detected_risk, "rgba(0, 0, 0, 0.3)")
            banner  = f"""
            <div style="background-color: {color};
                        padding: 1rem;
                        border-radius: 8px;
                        border-left: 6px solid {color.replace('0.5', '1.0')};
                        margin: 1rem 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="margin:0; font-size: 1.1rem; color: white;">{risk_text}</p>
            </div>
            """
            st.markdown(banner, unsafe_allow_html=True)

            # ----------------------------------------------------------------------------------- #
            # Add disclaimer with icon and link
            # ----------------------------------------------------------------------------------- #

            disclaimer = """
            <div style="display: flex;
                        align-items: center;
                        padding: 1rem;
                        background-color: rgba(255, 134, 134, 0.1);
                        border-radius: 8px;
                        border: 1px solid red;
                        margin: 1rem 0;
                        gap: 12px;">
                <div style="font-size: 1.5rem; color: white">❗</div>
                <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.61);">
                    This assessment is automated and preliminary, it was done using Open AI services. For official compliance verification, consult the <a href="https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/" 
                    target="_blank" style="color: #red; text-decoration: none;">AI Act Compliance Checker</a>.
                </div>
            </div>
            """
            st.markdown(disclaimer, unsafe_allow_html=True)

            # ----------------------------------------------------------------------------------- #
            # Compliance Guide with article links
            # ----------------------------------------------------------------------------------- #

            st.subheader("Compliance Guide")
            compliance_text = response_data.get("compliance_guide", "No data available.")
            
            # ----------------------------------------------------------------------------------- #
            # Add hyperlinks to article numbers
            # ----------------------------------------------------------------------------------- #

            compliance_text = re.sub(
                r'\(Article (\d+)\)',
                lambda m: f'<a href="https://artificialintelligenceact.eu/article/{m.group(1)}/" target="_blank" style="color: rgb(150, 182, 247);text-decoration: none;background-color: rgb(0, 51, 153);border: 1px solid rgb(150, 182, 247);border-radius: 18px;padding: 1px;">Article {m.group(1)}</a>', 
                compliance_text
            )
            
            st.markdown(compliance_text, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a project description to analyze.")

# ----------------------------------------------------------------------------------------------- #
# Footer with EU stars
# ----------------------------------------------------------------------------------------------- #

st.markdown("---")
st.markdown("""
<div class="eu-stars">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/European_stars.svg/2048px-European_stars.svg.png" 
         alt="EU Flag" 
         style="width: 100px; margin: 20px;">
</div>
<div style="text-align: center; color: white;">
            Developed by <a href="https://github.com/rafaelbenaion/aiact_chatbot" target="_blank">Smiling AI</a> <br>
    This tool is not an official platform from the European Union
</div>
""", unsafe_allow_html=True)

