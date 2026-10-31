# Knowora- Your Knowledge. Your AI. Your Answers.

<p align="center">
  <strong>An AI-powered chatbot that combines cloud AI, local LLMs, and Retrieval-Augmented Generation (RAG) to help users interact with their own documents.</strong>
</p>

---

## 1. About the Project

**Knowora** is an AI-powered chatbot application developed using Python, FastAPI, HTML, CSS, and JavaScript.

The goal of Knowora is to provide a unified interface where users can interact with different AI providers and ask questions about their own PDF documents.

Unlike a basic chatbot that only responds using the knowledge available to its language model, Knowora also supports document-based question answering through **Retrieval-Augmented Generation (RAG)**.

Users can upload PDF documents, allow the application to process their content, and ask questions related to those documents. Knowora retrieves relevant information from the uploaded content and provides it as context to the selected AI model.

The application supports two AI providers:

- **Google Gemini:** A cloud-based AI provider that generates responses using the Gemini API.
- **Ollama:** A local AI runtime that allows users to run language models on their own computers.

The project is designed to explore practical AI engineering concepts, including API integration, local LLM inference, document processing, vector databases, semantic retrieval, and full-stack application development.

## 2. Key Features

### AI Chat
- Interactive chatbot interface.
- Conversation history maintained in the browser.
- Support for multiple AI providers.
- Separate cloud and local model options.

### Multiple AI Providers

**Google Gemini**
- Connects to Google's Gemini API.
- Generates AI responses through a cloud-based model.
- Requires a valid API key and available API quota.

**Ollama**
- Runs AI models locally.
- Uses the Ollama API.
- Currently configured to use `qwen3.5:4b`.
- Allows local inference without sending prompts to the Gemini API.

### PDF Document Upload
- Upload PDF files through the chatbot interface.
- Extract text from PDF pages.
- Preserve page numbers for source references.
- Divide extracted text into smaller chunks for retrieval.

### Retrieval-Augmented Generation (RAG)
- Convert document content into searchable representations using ChromaDB's embedding functionality.
- Store document chunks and metadata in a persistent vector database.
- Retrieve relevant chunks based on a user's question.
- Provide retrieved document content as context to the AI model.
- Display document sources and page references when available.

### Document Management
- View uploaded documents.
- Identify document page and chunk information.
- Delete a document and its associated stored chunks.

### User Interface
- Modern, responsive chatbot interface.
- Dark mode and light mode.
- Persistent theme preference.
- AI provider selection.
- PDF upload interface.
- Document list and management controls.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main backend programming language |
| FastAPI | Backend API and application server |
| HTML5 | Frontend structure |
| CSS3 | Styling and responsive interface |
| JavaScript | Frontend interactions and API communication |
| Google Gemini API | Cloud AI response generation |
| Ollama | Local LLM execution |
| Qwen 3.5 4B | Configured local language model |
| ChromaDB | Vector database and semantic retrieval |
| Sentence Transformers | Embedding-related dependency |
| PyPDF | PDF text extraction |
| Uvicorn | ASGI server |

## 4. System Architecture

Knowora follows a frontend-backend architecture.

The frontend communicates with the FastAPI backend through HTTP requests. The backend processes user messages, retrieves document information when relevant, and sends the required context to the selected AI provider.

### High-Level Architecture

```text
                 USER
                   |
                   v
          KNOWORA FRONTEND
          HTML / CSS / JS
                   |
                   v
             FASTAPI
              BACKEND
                   |
          +--------+--------+
          |                 |
          v                 v
      GEMINI API          OLLAMA
      Cloud AI            Local AI
          |                 |
          +--------+--------+
                   |
                   v
              RESPONSE
                   |
                   v
              FRONTEND
```

### Document Processing Architecture

```text
           USER UPLOADS PDF
                   |
                   v
             FASTAPI
                   |
                   v
             PDF READER
               (PyPDF)
                   |
                   v
          TEXT EXTRACTION
                   |
                   v
            TEXT CHUNKING
                   |
                   v
             CHROMADB
          Vector Database
                   |
                   v
          SEMANTIC RETRIEVAL
                   |
                   v
            RELEVANT CHUNKS
                   |
                   v
           SELECTED AI MODEL
                   |
                   v
          CONTEXTUAL ANSWER
```

## 5. Understanding the RAG Pipeline

Retrieval-Augmented Generation is a technique that allows an AI model to answer questions using information retrieved from external documents.

Knowora uses this approach to make document-based question answering possible.

### Step 1: Document Upload

The user uploads a PDF through the frontend.

The frontend sends the file to the FastAPI backend, where the application receives and processes it.

### Step 2: Text Extraction

The application uses PyPDF to extract text from the uploaded document.

The extracted content retains its original page numbers so that retrieved information can be associated with its source page.

### Step 3: Text Chunking

Large documents are divided into smaller text sections called chunks.

The current chunking configuration uses:

- Chunk size: 1,000 characters.
- Chunk overlap: 200 characters.

Chunk overlap helps preserve context between neighboring sections.

### Step 4: Vector Storage

The extracted chunks and their metadata are stored in ChromaDB.

ChromaDB supports embedding-based similarity search, allowing the application to retrieve text that is semantically related to a user's question.

### Step 5: Semantic Retrieval

When a user asks a question, the backend searches the vector database for relevant document chunks.

The retrieved content is selected as contextual information for generating the response.

### Step 6: AI Response Generation

The retrieved context is included with the user's question and sent to the selected AI provider.

The provider generates a response using the supplied document information and conversation context.

### Step 7: Displaying the Answer

The backend returns the generated answer and available source information to the frontend.

The frontend displays the response in the chatbot interface.

## 6. Project Structure

## 6. Project Structure

```text
AI-Chatbot/
|
|-- static/
|   |-- index.html
|
|-- uploads/
|   |-- Uploaded PDF files
|
|-- chroma_db/
|   |-- Persistent vector database
|
|-- main.py
|   |-- FastAPI application and API endpoints
|
|-- document_processor.py
|   |-- PDF text extraction and chunking
|
|-- vector_store.py
|   |-- ChromaDB storage and retrieval functions
|
|-- requirements.txt
|   |-- Python dependencies
|
|-- .env
|   |-- Private environment variables
|
|-- .gitignore
|   |-- Files excluded from Git
|
|-- README.md
    |-- Project documentation
```

**Note:** `uploads/`, `chroma_db/`, and `.env` are local runtime resources. They should not be committed to the public repository. The exact folders are created or populated as the application runs.

## 7. Installation and Setup

Follow these steps to run Knowora on your local machine.

### Prerequisites

Install the following:

1. Python 3.12 recommended for the current development environment.
2. Git.
3. Visual Studio Code (recommended).
4. Ollama, if you want to use local AI.
5. A Google Gemini API key, if you want to use Gemini.

### Step 1: Clone the Repository

Replace the placeholders with your actual GitHub username and repository name.

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Move into the project directory:

```bash
cd YOUR_REPOSITORY
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

A virtual environment keeps the project's Python dependencies separate from other Python projects on your computer.

### Step 3: Activate the Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

For macOS or Linux:

```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs the libraries required by the application.

## 8. Configure Google Gemini

To use Gemini, you need an API key.

### Get an API Key

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Create an API key.
4. Copy the key securely.

### Create the Environment File

Create a file named `.env` in the root project directory.

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your actual API key.

**Security warning:** Never upload your `.env` file, API key, or other credentials to GitHub.

Gemini API usage is subject to the applicable model availability, account quota, and rate limits.

## 9. Configure Ollama

Ollama allows Knowora to communicate with locally running language models.

### Step 1: Install Ollama

Download and install Ollama:

https://ollama.com/

### Step 2: Download the Configured Model

Open PowerShell and execute:

```powershell
ollama pull qwen3.5:4b
```

This downloads the configured local model.

### Step 3: Verify the Model

```powershell
ollama list
```

Make sure `qwen3.5:4b` appears in the list.

### Step 4: Start Ollama

Ollama should be running locally.

Its API is available at:

```text
http://127.0.0.1:11434
```

Knowora uses the local Ollama API to send prompts and receive generated responses.

**Note:** Local model performance depends on your computer's hardware, available RAM, and model requirements.

## 10. Running the Application

After installing the dependencies and configuring the required environment variables, start the FastAPI server.

```powershell
python -m uvicorn main:app --reload
```

When the server starts successfully, open the following address in your browser:

### Knowora Application

http://127.0.0.1:8000/

### FastAPI Interactive Documentation

http://127.0.0.1:8000/docs

The interactive API documentation allows developers to inspect and test the backend endpoints.

## 11. How to Use Knowora

1. Start the FastAPI backend.
2. Open Knowora in your browser.
3. Select the preferred AI provider: Gemini or Ollama.
4. Enter a message in the chat input.
5. Submit the message and view the generated response.
6. Upload a PDF document using the document upload interface.
7. Wait for the document to be processed.
8. Ask questions about the uploaded document.
9. Review the answer and available document sources.
10. Use the document management interface when you want to view or remove uploaded documents.

For Gemini, ensure your API key and quota are valid. For Ollama, ensure the local service and configured model are available.

## 12. Backend API Overview

The FastAPI backend provides endpoints for interacting with the application.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves the Knowora frontend |
| `/chat` | POST | Processes chat messages |
| `/upload-pdf` | POST | Uploads and processes PDF files |
| `/documents` | GET | Lists stored documents |
| `/documents/{document_id}` | DELETE | Deletes a stored document |

Developers can inspect the request and response formats through the Swagger documentation at `/docs`.

## 13. Security and Privacy Considerations

Knowora uses both cloud-based and local AI providers.

- Gemini requests are sent to Google's API.
- Ollama requests are sent to the local Ollama service.
- API credentials are stored in environment variables.
- `.env` should remain excluded from Git.
- Uploaded documents and the local vector database should not be committed to the public repository.
- Do not upload confidential documents unless you understand how the selected provider processes the supplied content.

**Important:** Local AI inference does not automatically make the entire application secure. Uploaded file handling, access controls, API protection, and deployment security require additional work before public production use.

## 14. Current Project Status

Knowora is an actively developed learning and engineering project.

### Implemented

- FastAPI backend.
- Interactive chatbot frontend.
- Gemini API integration.
- Ollama integration.
- AI provider selection.
- PDF text extraction.
- Text chunking with overlap.
- ChromaDB persistent storage.
- Document-based retrieval.
- Source metadata and page references.
- Document listing and deletion.
- Dark and light themes.

### Planned Improvements

- Streaming AI responses.
- More robust document validation and processing.
- Improved retrieval quality and RAG evaluation.
- User authentication and access control.
- Conversation management and persistent chat storage.
- Better error handling and monitoring.
- Deployment and production configuration.
- Additional AI model integrations.

## 15. Learning Outcomes

Building Knowora provides practical experience with:

- Developing REST APIs using FastAPI.
- Connecting frontend applications to Python backends.
- Integrating cloud-based AI services.
- Running local Large Language Models.
- Processing PDF documents programmatically.
- Implementing a basic RAG pipeline.
- Using vector databases for semantic retrieval.
- Managing Python dependencies and environment variables.
- Organizing a multi-file software project.
- Using Git and GitHub for version control.

## 16. Future Vision

The long-term vision for Knowora is to develop it into a more capable personal knowledge assistant.

Potential future capabilities include support for additional document formats, improved retrieval and evaluation, conversation memory, user accounts, and more AI model providers.

The focus is to keep improving the application through practical engineering, testing, and real-world use cases.

## 17. Author

**Abhinav Sah**

B.Tech Computer Science Engineering Student
Aspiring AI Engineer | Interested in LLMs, RAG, and AI Application Development

GitHub: https://github.com/abhi-csengineer

---

## License

This project is currently shared for learning and development purposes. A formal open-source license can be added to the repository when selected.

---

<p align="center">
  <strong>Knowora â€” Your Knowledge. Your AI. Your Answers.</strong>
</p>
