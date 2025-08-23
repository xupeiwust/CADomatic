import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

# Load GEMINI API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in .env")

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

retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

# Conversation memory
memory = ConversationBufferMemory(return_messages=True)

# Gemini 2.5 Flash (LangChain wrapper)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.2,
    api_key=GEMINI_API_KEY
)

def build_prompt(user_prompt: str) -> str:
    """Builds full prompt with RAG context and conversation history."""
    docs = retriever.invoke(user_prompt)
    context = "\n\n".join(doc.page_content for doc in docs)
    history_text = ""
    for msg in memory.chat_memory.messages:
        if isinstance(msg, HumanMessage):
            history_text += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            history_text += f"Assistant: {msg.content}\n"
    return f"""
You are a helpful assistant that writes FreeCAD Python scripts from CAD instructions.
Use the following FreeCAD wiki documentation as context: {context}

Here is the conversation so far:
{history_text}

Current instruction: {user_prompt}

Respond with valid FreeCAD 1.0.1 Python code only, no extra comments.
"""

def prompt_llm(user_prompt: str) -> str:
    """Generate FreeCAD code using Gemini 2.5 Flash."""
    final_prompt = build_prompt(user_prompt)
    try:
        response = llm.invoke(final_prompt)
        result = response.content.strip()
        # Save user and AI messages in memory
        memory.chat_memory.add_user_message(user_prompt)
        memory.chat_memory.add_ai_message(result)
        return result
    except Exception as e:
        print("❌ Error generating FreeCAD code:", e)
        return ""

def reset_memory():
    """Clear conversation history."""
    global memory
    memory = ConversationBufferMemory(return_messages=True)
