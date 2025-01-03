import  fitz  
from    transformers import AutoTokenizer, AutoModel
import  torch
import  json

# ----------------------------------------------------------------------------------------------- #
# Extract text from each page of the PDF and store each page's text as one chunk (string).
# ----------------------------------------------------------------------------------------------- #

def extract_pages_as_chunks(file_path):

    pdf_document    = fitz.open(file_path)
    page_chunks     = []

    for page_number in range(len(pdf_document)):

        page        = pdf_document[page_number]
        page_text   = page.get_text()

        # Strip leading/trailing whitespace just in case

        page_text = page_text.strip()

        # Only append if the page has some text

        if page_text:
            page_chunks.append(page_text)

    pdf_document.close()
    return page_chunks

# ----------------------------------------------------------------------------------------------- #
# Generate embeddings for each chunk (page) using Hugging Face Transformers.
# ----------------------------------------------------------------------------------------------- #

def generate_embedding(text, tokenizer, model):

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    
    return embedding

# ----------------------------------------------------------------------------------------------- #
# Create embeddings for each chunk (page).
# ----------------------------------------------------------------------------------------------- #

def create_embeddings_for_chunks(chunks, tokenizer, model):

    embeddings = []

    for i, chunk in enumerate(chunks):
        
        preview = chunk[:60].replace('\n', ' ')
        print(f"Processing chunk (page) {i + 1}/{len(chunks)}: {preview}...")
        embedding = generate_embedding(chunk, tokenizer, model)

        embeddings.append({
            "chunk_index":  i,
            "text":         chunk,
            "embedding":    embedding.tolist()  # Convert to list for JSON serialization
        })
    return embeddings

# ----------------------------------------------------------------------------------------------- #
# Load the Hugging Face model and tokenizer
# ----------------------------------------------------------------------------------------------- #

tokenizer   = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model       = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# ----------------------------------------------------------------------------------------------- #
# Path to the uploaded PDF
# ----------------------------------------------------------------------------------------------- #

file_path = 'app/tools/aiact.pdf'

# ----------------------------------------------------------------------------------------------- #
# Step 1: Extract each page's text as one chunk
# ----------------------------------------------------------------------------------------------- #

page_chunks = extract_pages_as_chunks(file_path)

# ----------------------------------------------------------------------------------------------- #
# Step 2: Generate embeddings for each chunk
# ----------------------------------------------------------------------------------------------- #

embeddings = create_embeddings_for_chunks(page_chunks, tokenizer, model)

# ----------------------------------------------------------------------------------------------- #
# Step 3: Save embeddings to a JSON file
# ----------------------------------------------------------------------------------------------- #

output_file = "app/tools/page_embeddings.json"
with open(output_file, "w") as f:
    json.dump(embeddings, f)

print(f"Embeddings saved to {output_file}")
