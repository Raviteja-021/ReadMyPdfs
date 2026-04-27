import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
from rag import RAGSystem
from pdf_utils import extract_text_from_pdf

# Load environment
load_dotenv()

# Page config
st.set_page_config(page_title="PDF Q&A", page_icon="📚", layout="wide")

# Simple CSS
st.markdown("""
<style>
.main-header {background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
              color: white; padding: 1rem; border-radius: 10px; text-align: center;}
.chat-box {background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;}
.source-box {background: #000; color: #fff; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;}
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit app"""
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Header
    st.markdown('<div class="main-header"><h1>📚 Multi-PDF Q&A Assistant</h1><p style="margin:0;">Powered by Groq + Llama 3.3</p></div>', 
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload PDFs")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True
        )
        if uploaded_files:
            if st.button("Process Documents"):
                with st.spinner("Processing..."):
                    documents = []
                    for file in uploaded_files:
                        try:
                            # Pass the file object directly to extract_text_from_pdf
                            doc = extract_text_from_pdf(file, file.name)
                            if doc and doc.get('chunks'):
                                doc['size'] = file.size  # Store file size
                                documents.append(doc)
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {e}")
                    
                    if documents:
                        st.session_state.documents = documents
                        try:
                            rag = RAGSystem()
                            rag.setup_vectorstore(documents)
                            st.session_state.rag_system = rag
                            st.success(f"✅ Processed {len(documents)} documents.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error initializing RAG system: {e}")
                    else:
                        st.warning("No valid text extracted from uploaded files.")

        if st.session_state.documents:
            st.subheader("📋 Loaded Files")
            
            # Create a list of files to remove (to avoid modifying list while iterating)
            files_to_remove = []
            
            # Custom CSS for the file card look
            st.markdown("""
            <style>
            .file-card {
                background-color: #2b2c36;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .file-info {
                display: flex;
                flex-direction: column;
            }
            .file-name {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
            }
            .file-meta {
                font-size: 12px;
                color: #a0a0a0;
            }
            /* Target streamlit button to look more like a plain icon if possible, 
               but standard buttons rely on theme. We use a simple label. */
            </style>
            """, unsafe_allow_html=True)

            for i, doc in enumerate(st.session_state.documents):
                # Layout matching the image somewhat: Icon + Name group + Close Button
                # We use columns to simulate the row
                c1, c2 = st.columns([0.9, 0.1])
                
                with c1:
                    # Using markdown for tighter control over appearance than st.write
                    st.markdown(f"""
                    <div style="line-height: 1.2; display: flex; align-items: center;">
                        <span style="font-size: 1.2rem; margin-right: 10px;">📄</span>
                        <span style="font-weight: 500; font-size: 0.95rem;">{doc['filename']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c2:
                    # Use type="tertiary" to remove the button background/border
                    if st.button("✕", key=f"remove_{i}", help=f"Remove {doc['filename']}", type="tertiary"):
                        files_to_remove.append(i)
                
                # Add a small divider or spacer visually (optional, Streamlit adds spacing by default)
                st.markdown("---")
            
            # Processing removal
            if files_to_remove:
                for index in sorted(files_to_remove, reverse=True):
                    removed_doc = st.session_state.documents.pop(index)
                    st.toast(f"🗑️ Removed {removed_doc['filename']}")
                
                # Re-initialize RAG with remaining documents
                if st.session_state.documents:
                    with st.spinner("♻️ Updating knowledge base..."):
                        try:
                            rag = RAGSystem()
                            rag.setup_vectorstore(st.session_state.documents)
                            st.session_state.rag_system = rag
                            st.success("✅ Knowledge base updated!")
                        except Exception as e:
                            st.error(f"Error updating knowledge base: {e}")
                else:
                    st.session_state.rag_system = None
                    st.warning("⚠️ All documents removed. Please upload new files.")
                
                st.rerun()

    # Main Chat Area
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("💬 Ask Questions")
        if not st.session_state.rag_system:
            st.info("👆 Upload and process PDF files to ask questions.")
        else:
            question = st.text_input("Your question:", key="question")
            if st.button("Ask") and question:
                with st.spinner("Getting answer..."):
                    try:
                        result = st.session_state.rag_system.query(question)
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": result["answer"],
                            "sources": [s.get("source", "Unknown") for s in result.get("sources", [])],
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # Show chat history
        for chat in reversed(st.session_state.chat_history):
            st.markdown('</div>', unsafe_allow_html=True)
            st.write(f"**Q:** {chat['question']}")
            st.write(f"**A:** {chat['answer']}")
            if chat.get("sources"):
                sources = list(set(chat["sources"]))
                st.markdown(f'<div class="source-box">📚 Sources: {", ".join(sources)}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

    # Stats
    with col2:
        st.header("📊 Stats")
        st.metric("Documents", len(st.session_state.documents))
        st.metric("Questions", len(st.session_state.chat_history))
        if st.button("Clear History"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()
