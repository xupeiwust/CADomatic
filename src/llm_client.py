import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Set up Hugging Face repo and files
REPO_ID = "Yas1n/CADomatic_vectorstore"
FILENAME_FAISS = "index.faiss"
FILENAME_PKL = "index.pkl"

# Download once (uses HF cache internally)
faiss_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME_FAISS)
pkl_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME_PKL)

# Use same folder for both files
download_dir = Path(faiss_path).parent

# Load vectorstore
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.load_local(str(download_dir), embeddings=embedding, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 40})

# Gemini 2.5 Flash
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=1.2)

def prompt_llm(user_prompt: str) -> str:
    docs = retriever.invoke(user_prompt)
    context = "\n\n".join(doc.page_content for doc in docs)

    final_prompt = f"""
You are a helpful assistant that writes FreeCAD Python scripts from CAD instructions.
Use the following FreeCAD wiki documentation as context:

{context}

Instruction:
{user_prompt}

Respond with valid FreeCAD Python code only, no extra commentary.
"""

    try:
        response = llm.invoke(final_prompt)
        return response.content
    except Exception as e:
        print("❌ Error generating FreeCAD code:", e)
        return ""
