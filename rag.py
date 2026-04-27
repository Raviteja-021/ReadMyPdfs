import os
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema import Document


class RAGSystem:
    def __init__(self):
        """Initialize the RAG system with Groq and HuggingFace"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        # LLM using ChatGroq
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=self.api_key,
            temperature=0.3
        )
        
        # Embeddings using HuggingFace (local)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None

    def setup_vectorstore(self, documents: List[Dict[str, Any]]):
        """Create vector store from documents"""
        langchain_docs = []
        for doc in documents:
            for chunk in doc["chunks"]:
                langchain_doc = Document(
                    page_content=chunk["content"],
                    metadata={
                        "filename": doc["filename"],
                        "page": chunk["page"],
                        "source": f"{doc['filename']} - Page {chunk['page']}"
                    }
                )
                langchain_docs.append(langchain_doc)

        # Create vector store
        self.vectorstore = FAISS.from_documents(
            documents=langchain_docs,
            embedding=self.embeddings
        )
        # Setup retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        # Setup QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True
        )

    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system"""
        if not self.qa_chain:
            raise ValueError("RAG system not initialized. Please setup vectorstore first.")

        # .invoke() method
        response = self.qa_chain.invoke({"query": question})
        sources = []
        for doc in response.get("source_documents", []):
            sources.append({
                "filename": doc.metadata.get("filename", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown")
            })

        return {
            "answer": response.get("result", ""),
            "sources": sources,
            "question": question
        }

    def get_similar_documents(self, query: str, k: int = 3) -> List[Document]:
        """Get similar documents for a query"""
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=k)
