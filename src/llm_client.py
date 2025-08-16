import os
from pathlib import Path
from huggingface_hub import hf_hub_download, InferenceClient
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load HF token from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing in .env")

# FAISS vectorstore setup
REPO_ID = "Yas1n/CADomatic_vectorstore"
FILENAME_FAISS = "index_oss120b.faiss"
FILENAME_PKL = "index_oss120b.pkl"

faiss_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME_FAISS)
pkl_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME_PKL)
download_dir = Path(faiss_path).parent

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    str(download_dir),
    embeddings=embedding,
    allow_dangerous_deserialization=True,
    index_name="index_oss120b"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 40})

# Initialize HF InferenceClient
client = InferenceClient(provider="fireworks-ai", api_key=HF_TOKEN)
MODEL_NAME = "openai/gpt-oss-120b"

# Prompt function
def prompt_llm(user_prompt: str) -> str:
    # Retrieve context from FAISS
    docs = retriever.invoke(user_prompt)
    context = "\n\n".join(doc.page_content for doc in docs)

    final_prompt = f"""
You are a helpful assistant that writes FreeCAD Python scripts from CAD instructions.
Use the following FreeCAD wiki documentation as context:

{context}

Instruction:
{user_prompt}

Respond with valid FreeCAD 1.0.1 Python code only, no extra comments.
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": final_prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("❌ Error in HF response:", e)
        return ""

# Main CLI
if __name__ == "__main__":
    prompt = input("Describe your FreeCAD part: ")
    code = prompt_llm(prompt)

    # Save generated code
    output_path = Path("generated/result_script.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Code generated and written to {output_path}")
