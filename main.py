
import os
import shutil
import traceback
import uuid
import requests

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from document_processor import (
    extract_pages_from_pdf,
    split_text_into_chunks
)

from vector_store import (
    store_chunks,
    search_chunks_with_metadata,
    list_documents,
    delete_document
)


# Load environment variables
load_dotenv()


# Create FastAPI application
app = FastAPI(title="My AI Chatbot")


# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# Ollama local AI configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen3.5:4b"


# Generate response using Ollama
def generate_ollama_response(contents):

    messages = []

    for item in contents:

        role = (
            "assistant"
            if item.role == "model"
            else item.role
        )
        text_parts = [
            part.text
            for part in item.parts
            if part.text
        ]

        message_text = "\n".join(text_parts)

        messages.append({
            "role": role,
            "content": message_text
        })

    print("Ollama messages:", len(messages), flush=True)
    print(
        "Ollama prompt characters:",
        sum(len(m["content"]) for m in messages),
        flush=True
    )
    print("Sending request to Ollama...", flush=True)
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "think":False,
            "stream": False
        },
        timeout=300
    )
    print("Ollama response received!", flush=True)

    response.raise_for_status()

    data = response.json()

    reply = data.get("message", {}).get("content", "")

    if not reply.strip():
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return reply


# Chat request model
class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = Field(default_factory=list)
    provider: str = "gemini"


# PDF upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Home route
@app.get("/")
def home():
    return FileResponse("static/index.html")


# Chat endpoint with RAG and provider selection
@app.post("/chat")
def chat(request: ChatRequest):

    try:

        contents = []

        # Retrieve relevant chunks from ChromaDB
        retrieved_chunks = search_chunks_with_metadata(
            request.message,
            n_results=3
        )

        # Prepare document context and sources
        context_parts = []
        sources = []

        for item in retrieved_chunks:

            text = item["text"]
            metadata = item["metadata"]

            context_parts.append(text)

            source = {
                "filename": metadata.get("filename", "Unknown"),
                "document_id": metadata.get("document_id", "Unknown"),
                "page_number": metadata.get("page_number", 0)
            }

            if source not in sources:
                sources.append(source)

        # Add previous conversation messages
        for item in request.history:

            role = item.get("role")
            text = item.get("content", item.get("text", ""))

            if role in ("user", "model") and text.strip():

                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=text)]
                    )
                )

        # Prepare current user message
        if context_parts:

            context = "\n\n".join(context_parts)

            current_message = f"""
Use the following retrieved document context to answer
the user's question.

Instructions:
- Prioritize information from the provided context.
- Do not invent facts that are not present in the context.
- If the answer is not available in the context, say so.
- Give a clear and helpful answer.

Retrieved document context:

{context}

User's question:

{request.message}
"""

        else:

            current_message = request.message

        # Add current message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=current_message)]
            )
        )

        # Generate AI response using selected provider

        if request.provider == "gemini":

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            reply = response.text

        elif request.provider == "ollama":

            reply = generate_ollama_response(contents)

        else:

            raise HTTPException(
                status_code=400,
                detail="Invalid AI provider. Choose gemini or ollama."
            )

        # Return final response
        return {
            "user_message": request.message,
            "reply": reply,
            "sources": sources
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"Chat API error: {type(e).__name__}: {e}",
            flush=True
        )
        print("Full error details:", repr(e), flush=True)

        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="The AI service could not complete the request."
        )


# Delete a document from ChromaDB
@app.delete("/documents/{document_id}")
def remove_document(document_id: str):

    try:

        deleted_chunks = delete_document(document_id)

        if deleted_chunks == 0:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        return {
            "message": "Document deleted successfully.",
            "document_id": document_id,
            "deleted_chunks": deleted_chunks
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"Document deletion error: {e}",
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail="Could not delete document."
        )


# List uploaded documents
@app.get("/documents")
def get_documents():

    try:

        documents = list_documents()

        return {
            "total_documents": len(documents),
            "documents": documents
        }

    except Exception as e:

        print(
            f"Document listing error: {e}",
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve documents."
        )


# Upload and process PDF
@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):

    if (
        not file.filename
        or not file.filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    file_path = UPLOAD_DIR / Path(file.filename).name

    try:

        # Save uploaded PDF
        with file_path.open("wb") as saved_file:
            shutil.copyfileobj(file.file, saved_file)

        # Extract text page by page
        pages = extract_pages_from_pdf(str(file_path))

        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in this PDF."
            )

        # Generate unique document ID
        document_id = str(uuid.uuid4())

        all_chunks = []
        all_metadatas = []

        # Split each page into chunks
        for page in pages:

            chunks = split_text_into_chunks(page["text"])

            for chunk in chunks:

                all_chunks.append(chunk)

                all_metadatas.append({
                    "filename": file_path.name,
                    "document_id": document_id,
                    "page_number": page["page_number"]
                })

        if not all_chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks could be created."
            )

        # Store chunks in ChromaDB
        store_chunks(
            all_chunks,
            all_metadatas
        )

        return {
            "message": "PDF uploaded and processed successfully.",
            "filename": file_path.name,
            "document_id": document_id,
            "chunks_stored": len(all_chunks),
            "pages_processed": len(pages)
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"PDF processing error: {type(e).__name__}: {e}",
            flush=True
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Could not process the PDF."
        )

    finally:
        file.file.close()
