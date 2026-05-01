import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from io import BytesIO
from docx import Document
import PyPDF2

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="ResumeIQ AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# LLaMA 3 via Groq
# -----------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=GROQ_API_KEY
)

# -----------------------------
# Embeddings (FREE)
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

DB_PATH = "faiss_store"

# -----------------------------
# Vector Store
# -----------------------------
def load_vectorstore():
    if os.path.exists(DB_PATH):
        return FAISS.load_local(
            DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return None

def save_vectorstore(vs):
    vs.save_local(DB_PATH)

def store_resume(user_id: str, text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)
    metadatas = [{"user_id": user_id} for _ in chunks]

    vs = load_vectorstore()

    if vs is None:
        vs = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)
    else:
        vs.add_texts(chunks, metadatas=metadatas)

    save_vectorstore(vs)

def retrieve_context(user_id: str, query: str, k: int = 4):
    vs = load_vectorstore()
    if not vs:
        return ""

    docs = vs.similarity_search(query, k=k)

    filtered = [
        d.page_content for d in docs
        if d.metadata.get("user_id") == user_id
    ]

    return "\n".join(filtered)

def generate_answer(user_id: str, question: str):
    context = retrieve_context(user_id, question)

    if not context:
        return "⚠️ Please upload a resume first."

    prompt = ChatPromptTemplate.from_template("""
You are a strict AI Career Coach.

Rules:
- Answer ONLY using the resume
- If information is not present → say "Not found in resume"
- Do NOT assume anything
- Keep answers clear and professional

Resume:
{context}

Question:
{question}
""")

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return response.content

# -----------------------------
# File Parsing
# -----------------------------
def extract_text(file: UploadFile) -> str:
    filename = file.filename.lower()
    content = file.file.read()

    if filename.endswith(".txt"):
        return content.decode("utf-8")

    elif filename.endswith(".docx"):
        doc = Document(BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])

    elif filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type (.pdf, .docx, .txt only)"
        )

# -----------------------------
# API Models
# -----------------------------
class Question(BaseModel):
    user_id: str
    question: str

# -----------------------------
# Routes
# -----------------------------
@app.post("/upload")
async def upload_resume(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        text = extract_text(file)

        if not text.strip():
            raise HTTPException(400, "Empty or unreadable file")

        store_resume(user_id, text)

        return {
            "status": "success",
            "message": "Resume uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/ask")
async def ask_question(request: Question):
    try:
        answer = generate_answer(
            request.user_id,
            request.question
        )

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/")
def root():
    return {"message": "ResumeIQ AI running 🚀"}