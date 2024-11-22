import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from model import handle_query


# Previous functions remain the same
def load_chat_history():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as file:
            return json.load(file)
    return []

def save_chat_history(chat_history):
    with open("chat_history.json", "w") as file:
        json.dump(chat_history, file)

def format_response(response_data):
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
    if os.path.exists("chat_history.json"):
        os.remove("chat_history.json")

def load_css(file_name):
    with open("style.css", "r") as f:
        if os.path.exists(file_name):
            with open(file_name) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.warning(f"CSS file '{file_name}' not found. Default styles applied.")

def main():
    load_dotenv()
    st.set_page_config(
        page_title="Vedabot - Your Health Companion",
        page_icon=":books:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    load_css("style.css")

    chat_history = load_chat_history()

    # Modified Header with enhanced styling
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
                <p>Explore health solutions based on Ayurvedic knowledge</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar content remains the same
    with st.sidebar:
        st.title("Vedabot")
        st.markdown("Your Ayurvedic Chatbot Assistant :herb:")
        st.image("https://t4.ftcdn.net/jpg/07/22/93/81/360_F_722938112_xunuELGTYPe4cb2JNKQRddTaghih3nfj.jpg", use_container_width=True)
        
        st.info("**Instructions:**\n- Enter your query related to health.\n- Receive Ayurvedic insights.\n- In case of severe problem consult the Doctor")

        if chat_history:
            st.markdown("### 💬 Chat History")
            for i, chat in enumerate(chat_history):
                time_display = chat.get('time', 'Time Not Available')
                question_display = chat.get('question', 'Question Not Available')
                st.markdown(f"**{time_display}** - {question_display}")

            if st.button("Clear Chat History"):
                clear_chat_history()
                st.success("Chat History has been cleared.")

    # Main content layout with modified image grid
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
        
        st.markdown('<div class="image-grid">', unsafe_allow_html=True)
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
            
        # Row 2: Two images
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
            
        # Row 3: Two images
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

    # Footer section remains the same
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