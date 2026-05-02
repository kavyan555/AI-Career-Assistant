Project Title
ResumeIQ AI – Resume-Based Career Assistant
________________________________________
Description

ResumeIQ AI is an AI-powered application that allows users to upload their resumes and ask questions based on the content. The system uses Retrieval-Augmented Generation to ensure responses are grounded strictly in the uploaded document.
The application consists of a FastAPI backend and a Streamlit frontend.
________________________________________
Features

•	Upload and analyze resumes

•	Ask questions based on resume content

•	Multi-user support using user ID

•	Context-aware answers using RAG

•	Fast and efficient vector search with FAISS
________________________________________
Tech Stack

•	Python

•	FastAPI

•	Streamlit

•	LangChain

•	Groq LLaMA 3
•	FAISS
•	HuggingFace Embeddings
________________________________________
Project Structure

AI-CAREER-ASSISTANT/

│── main.py          # FastAPI backend

│── frontend.py      # Streamlit frontend

│── faiss_store/     # Vector database

│── requirements.txt

│── .env
________________________________________
Prerequisites

•	Python 3.8 or above

•	Groq API key
________________________________________
Installation

pip install -r requirements.txt
________________________________________
Configuration

Create a .env file:

GROQ_API_KEY=your_api_key_here
________________________________________
Running the Application

Start Backend

uvicorn main:app --reload

Start Frontend

streamlit run frontend.py
________________________________________
Usage
1.	Enter a user ID in the sidebar

2.	Upload a resume

3.	Ask questions related to the resume

4.	Receive responses strictly based on the document
________________________________________
How It Works

•	Resume is uploaded and converted to text

•	Text is split into chunks

•	Chunks are embedded into vectors

•	Stored in FAISS with user metadata

•	Query retrieves relevant chunks

•	LLM generates answer using retrieved context
