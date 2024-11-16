import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from model import handle_query

def load_chat_history():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as file:
            return json.load(file)
    return []

def save_chat_history(chat_history):
    with open("chat_history.json", "w") as file:
        json.dump(chat_history, file)

def format_response(response_data):
    """
    Formats the response with headings, markdown, and removes unnecessary references.
    """
    # Extracting the main response
    result = response_data.get('result', '')
    # Formatting the response
    formatted_result = f"""
    ### 🌿 Ayurvedic Insights
    {result}

    ---
    **Note:** These remedies are complementary. Consult a healthcare provider for persistent issues.
    """
    return formatted_result

def clear_chat_history():
    if os.path.exists("chat_history.json"):
        os.remove("chat_history.json")

def load_css(file_name):
    """Function to load CSS from a file and inject into the app"""
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
        initial_sidebar_state="expanded",
    )
    load_css("style.css")

    chat_history = load_chat_history()

    with st.sidebar:
        st.title("Vedabot")
        st.markdown("Your Ayurvedic Chatbot Assistant :herb:")
        st.image("https://t4.ftcdn.net/jpg/07/22/93/81/360_F_722938112_xunuELGTYPe4cb2JNKQRddTaghih3nfj.jpg", use_container_width=True)  # Replace with your logo URL or local image
        st.info("Created By Kiet")
        st.markdown("**Instructions:**\n- Enter your query related to health.\n- Receive Ayurvedic insights.")

        if chat_history:
            st.markdown("### 💬 Chat History")
            for i, chat in enumerate(chat_history):
                st.markdown(f"**{chat['time']}** - {chat['question']}")

        if st.button("Clear Chat History"):
            clear_chat_history()
            st.success("Chat History has been cleared.")

    st.title("Welcome to Vedabot :books:")
    st.markdown(
        """
        Vedabot helps you explore health solutions based on Ayurvedic knowledge. 
        Type your health-related question below and get instant insights.
        """
    )

    question = st.text_input(
        "Ask your health-related question here:",
        placeholder="e.g., What are Ayurvedic remedies for cold?"
    )

    if st.button("Submit") and question.strip():
        with st.spinner("Finding the best Ayurvedic insights..."):
            response_data = handle_query(question)
        
        if response_data:
            formatted_response = format_response(response_data)
            st.success("Here are your results:")
            st.markdown(formatted_response, unsafe_allow_html=True)
            chat_entry = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "question": question
            }
            chat_history.append(chat_entry)
            save_chat_history(chat_history) 

        else:
            st.warning("No relevant insights found. Please refine your query.")
    if st.button("Consult Nearest Doctor"):
        st.markdown("[Click here to consult doctors](https://www.example.com/consult-doctors)", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("© 2024 Vedabot | Built with ❤️ for Ayurveda and AI.")

if __name__ == "__main__":
    main()
