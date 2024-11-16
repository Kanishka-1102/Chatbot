import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DATA_PATH = 'data/'

def create_vector_db():
    try:
        # Load PDFs from the data folder
        loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
        documents = loader.load()
        if not documents:
            st.warning("No documents were loaded from the PDFs.")
            return

        # Split the documents into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        # Initialize embeddings using HuggingFace
        embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2', 
            model_kwargs={'device': 'cpu'}
        )

        # Define path to store the FAISS vector database
        DB_FAISS_PATH = 'vectorstore/db_faiss'
        if not os.path.exists(DB_FAISS_PATH):
            os.makedirs(DB_FAISS_PATH)

        # Create FAISS vector database from documents
        db = FAISS.from_documents(texts, embeddings)
        
        # Save the FAISS vector database locally
        db.save_local(DB_FAISS_PATH)

        st.success("Vector database created and saved successfully!")

    except Exception as e:
        st.error(f"An error occurred while creating the vector database: {e}")

def main():
    load_dotenv()

    st.set_page_config(page_title="Vedabot", page_icon=":books:")
    st.header("Chat with Vedabot :books:")

    question = st.text_input("Ask A Question About health or Problem:")

    create_vector_db()

if __name__ == '__main__':
    main()
