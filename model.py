# model.py
import os
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import RetrievalQA
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Constants
DB_FAISS_PATH = 'vectorstore/db_faiss'

# Template for the Ayurvedic advisor
custom_prompt_template = """
You are an Ayurveda Advisor. Use the following pieces of information to answer the user's question in detail. When discussing 
medicines and remedies, ensure to include precautions and exceptions where necessary. Don't include references section.
Create a stand-alone question from follow-up questions while retaining context from the previous exchanges.
Format the entire answer in markdown format, with bolds, italics, and pointers wherever required.
Only return the helpful answer below and nothing else. For answers exceeding 120 tokens, answer in points.
Context: {context}
Question: {question}
"""

def set_custom_prompt():
    """Create and return a custom prompt template"""
    prompt = PromptTemplate(template=custom_prompt_template, 
                          input_variables=["context", "question"])
    return prompt

def add_sources_to_answer(sources, answer):
    """Add reference sources to the answer"""
    if len(sources) > 0:
        answer += f"\n#### References\n"
        for i, source in enumerate(sources, 1):
            answer += format_source_content(source, i)
    return answer

def format_source_content(source, i):
    """Format individual source content"""
    metadata = source.metadata
    file_name = metadata["source"].split('\\')[-1].split(".pdf")[0]
    page_content = source.page_content
    formatted_content = f"##### {i}.{file_name}\n"
    formatted_content += f"Source Content: _{page_content}_\n"
    return formatted_content

def retrieval_qa_chain(llm, prompt, db):
    """Create a retrieval QA chain"""
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return qa_chain

def load_llm():
    """Load and configure the language model"""
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_ACESS_TOKEN"), 
        max_new_tokens=1024,
        temperature=0.1,
        model_kwargs={"max_length": 64} 
    )
    return llm

def create_chat_bot_chain():
    """Create the complete chatbot chain"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)    
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa_chain = retrieval_qa_chain(llm, qa_prompt, db)
    return qa_chain

def handle_query(question):
    """Handle user queries"""
    qa_chain = create_chat_bot_chain()
    try:
        response = qa_chain({'query': question})
        return response
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        return {"result": "I apologize, but I encountered an error processing your question. Please try again."}

# app.py
import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from model import handle_query

def load_chat_history():
    """Load chat history from JSON file"""
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as file:
            return json.load(file)
    return []

def save_chat_history(chat_history):
    """Save chat history to JSON file"""
    with open("chat_history.json", "w") as file:
        json.dump(chat_history, file)

def format_response(response_data):
    """Format the response with Ayurvedic styling"""
    result = response_data.get('result', '')
    formatted_result = f"""
    <div class="response-container">
    ### 🌿 Ayurvedic Insights
    {result}

    ---
    **Note:** These remedies are complementary. Consult a healthcare provider for persistent issues.
    </div>
    """
    return formatted_result

def clear_chat_history():
    """Clear the chat history file"""
    if os.path.exists("chat_history.json"):
        os.remove("chat_history.json")

def load_css(file_name):
    """Load custom CSS styles"""
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file '{file_name}' not found. Default styles applied.")

def main():
    """Main application function"""
    # Load environment variables
    load_dotenv()
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="Vedabot - Your Health Companion",
        page_icon=":books:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Load custom CSS
    load_css("style.css")
    
    # Load chat history
    chat_history = load_chat_history()

    # Header section
    st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="logo-container">
                <img src="https://www.pngarts.com/files/12/Ayurveda-Logo-PNG-Photo.png" 
                     class="circular-logo">
            </div>
            <div class="title-container">
                <h1>Welcome to Vedabot</h1>
                <h2>Your Home Remedies Buddy</h2>
                <p class="explore-text">Explore health solutions based on Ayurvedic knowledge</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar content
    with st.sidebar:
        st.title("Vedabot")
        st.markdown("Your Ayurvedic Chatbot Assistant :herb:")
        st.image("https://t4.ftcdn.net/jpg/07/22/93/81/360_F_722938112_xunuELGTYPe4cb2JNKQRddTaghih3nfj.jpg", 
                use_container_width=True)
        
        st.info("""**Instructions:**
        - Enter your query related to health.
        - Receive Ayurvedic insights.
        - In case of severe problem consult the Doctor""")

        if chat_history:
            st.markdown("### 💬 Chat History")
            for chat in chat_history:
                time_display = chat.get('time', 'Time Not Available')
                question_display = chat.get('question', 'Question Not Available')
                st.markdown(f"**{time_display}** - {question_display}")

            if st.button("Clear Chat History"):
                clear_chat_history()
                st.success("Chat History has been cleared.")

    # Main content layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        question = st.text_input(
            "Ask your health-related question here:",
            placeholder="e.g., What are Ayurvedic remedies for cold?"
        )

        if st.button("Submit", key="submit_button", help="Click to get Ayurvedic insights") and question.strip():
            with st.spinner("Finding the best Ayurvedic insights..."):
                response_data = handle_query(question)
                
            if response_data:
                formatted_response = format_response(response_data)
                st.markdown(formatted_response, unsafe_allow_html=True)
                
                chat_entry = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "question": question
                }
                chat_history.append(chat_entry)
                save_chat_history(chat_history)
            else:
                st.warning("No relevant insights found. Please refine your query.")
    
    with col2:
        # Image grid
        st.markdown('<div class="image-grid">', unsafe_allow_html=True)
        
        # Row 1
        cols = st.columns(2)
        with cols[0]:
            st.markdown("""
            <div class="image-container">
                <img src="https://media.istockphoto.com/id/697860312/photo/indian-ayurvedic-dietary-supplement-called-chyawanprash-chyavanaprasha-is-a-cooked-mixture-of.jpg?s=612x612&w=0&k=20&c=outabsxtvdSSt4aCkRdjtKrVtv7qko4N6AMA6qVtWmo=" class="square-image">
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown("""
            <div class="image-container">
                <img src="https://t3.ftcdn.net/jpg/05/68/27/22/360_F_568272234_QctXAHNIczaboEphLMQJ9fJ6c5WoSH9x.jpg" class="circular-image">
            </div>
            """, unsafe_allow_html=True)
        
        # Row 2
        cols = st.columns(2)
        with cols[0]:
            st.markdown("""
            <div class="image-container">
                <img src="https://cdn.pixabay.com/photo/2024/03/20/04/00/ai-generated-8644565_640.jpg" class="circular-image">
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown("""
            <div class="image-container">
                <img src="https://t4.ftcdn.net/jpg/07/41/35/67/360_F_741356771_4d4HPQpxdSOKW6E1hfTgPMtWzUIX5C7K.jpg" class="square-image">
            </div>
            """, unsafe_allow_html=True)
        
        # Row 3
        cols = st.columns(2)
        with cols[0]:
            st.markdown("""
            <div class="image-container">
                <img src="https://media.istockphoto.com/id/697805638/photo/indian-ayurvedic-dietary-supplement-called-chyawanprash-chyavanaprasha-is-a-cooked-mixture-of.jpg?s=1024x1024&w=is&k=20&c=eAhrqvy3fsDyIQS1mWpOF1BC-wZGQg6Ea3NwxHO68OE=" class="square-image">
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown("""
            <div class="image-container">
                <img src="https://media.istockphoto.com/id/946765682/photo/herb-and-spice-abstract-border.jpg?s=1024x1024&w=is&k=20&c=1fJoLGsDyutAwIbA2Ng4fZIKUEzzRqQY6PB8FvUh0Og=" class="circular-image">
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer section
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    if st.button("Consult Nearest Doctor", key="consult_button"):
        st.markdown("[Click here to consult doctors](https://www.example.com/consult-doctors)", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #000000;'>
        © 2024 Vedabot | Built with ❤️ for Ayurveda and AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()