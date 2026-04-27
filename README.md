# 📚 Multi‑PDF Q&A Assistant

A powerful Streamlit application that enables you to chat with multiple PDF documents simultaneously. It uses **Groq** for high-speed LLM inference and **HuggingFace** for local embeddings, ensuring a fast and private RAG (Retrieval-Augmented Generation) experience.

---

## ⚡️ Key Features

- **📄 Multi-PDF Support**: Upload and process multiple PDF files at once.
- **🔍 Advanced RAG**: Uses vector embeddings to retrieve precise context for your questions.
- **🚀 High-Speed Inference**: Powered by **Groq** (Llama 3 70B) for near-instant responses.
- **🔒 Local Embeddings**: Uses `sentence-transformers` locally—no external API costs for embeddings.
- **🗑️ Document Management**: Manually remove processed files to update the knowledge base instantly.
- **💬 Chat History**: Maintains context of your conversation.
- **✨ Sources Cited**: Shows exactly which document and page the answer came from.

---

## 🧠 How It Works

The application follows a standard RAG (Retrieval-Augmented Generation) pipeline:

```mermaid
graph LR
    A["Upload PDF"] --> B["Extract Text"]
    B --> C["Split into Chunks"]
    C --> D["Generate Embeddings<br/>(HuggingFace)"]
    D --> E["Store in Vector DB<br/>(FAISS)"]
    
    F["User Question"] --> G["Embed Question"]
    G --> H["Retrieve Relevant<br/>Chunks"]
    E -.-> H
    H --> I["Send to LLM<br/>(Groq Llama 3)"]
    I --> J["Generate Answer"]
```

1.  **PDF Loading**: The app reads your uploaded PDF files and extracts the text.
2.  **Chunking**: The text is split into smaller, manageable chunks to fit into the AI's context window.
3.  **Embedding**: Each chunk is converted into a numerical vector using a local embedding model (**HuggingFace**).
4.  **Vector Store**: These vectors are stored in a local FAISS index for fast searching.
5.  **Retrieval**: When you ask a question, the system finds the most relevant chunks from the vector store.
6.  **Generation**: The relevant chunks + your question are sent to **Groq** (Llama 3), which generates a precise answer based on the context.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM Provider**: [Groq](https://groq.com/) (Llama 3)
- **Embeddings**: [HuggingFace](https://huggingface.co/) (`all-MiniLM-L6-v2`)
- **Vector Store**: [FAISS](https://github.com/facebookresearch/faiss)
- **Framework**: [LangChain](https://www.langchain.com/)

---

## 📋 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/Multi-PDF-QNA.git
cd Multi-PDF-QNA
```

### 2️⃣ Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up API Keys
1.  Get your free API Key from [Groq Console](https://console.groq.com/).
2.  Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=gsk_your_actual_api_key_here
    ```

---

## 🚀 Running the App

```bash
streamlit run scripts/app.py
```
The app will open in your browser at `http://localhost:8501`.

---

## 💡 How to Use

1.  **Sidebar**: Use the sidebar to upload your PDF files.
2.  **Process**: Click "Process Documents" to analyze the text and build the knowledge base.
3.  **Chat**: Type your question in the main chat area.
    - The AI will answer based *only* on the content of your PDFs.
    - Check the "Sources" expander to see where the information was found.
4.  **Manage**: Click the **✕** button next to a file in the sidebar to remove it from the knowledge base.

---

## 📂 Project Structure

```
Multi-PDF-QNA/
├── scripts/
│   ├── app.py          # Main Streamlit application
│   ├── pdf_utils.py    # PDF text extraction logic
│   └── rag.py          # RAG system (Embeddings + Vector Store + LLM)
├── requirements.txt    # Project dependencies
├── .env                # Environment variables (API Keys)
└── README.md           # Documentation
```

