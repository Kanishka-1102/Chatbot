import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from model import handle_query
from image_scraper import AyurvedicImageScraper  # New import

# Load environment variables
load_dotenv()

def load_chat_history():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as file:
            return json.load(file)
    return []

def save_chat_history(chat_history):
    with open("chat_history.json", "w") as file:
        json.dump(chat_history, file)

def main():
    # Set up page
    st.set_page_config(
        page_title="Vedabot - Your Health Companion",
        page_icon=":books:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Add background image
    st.markdown("""
    <style>
    .stApp {
        background-image: url('https://media.istockphoto.com/id/1064689094/vector/watercolor-frame-of-gingko-biloba.jpg?s=612x612&w=0&k=20&c=87YvfpcVBlLhFvGjiPwZtWWRbVZA2SAuxa5wHARhA5E=');
        background-size: cover;
    }
    .image-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    .image-grid img {
        border-radius: 15px;
        object-fit: cover;
        width: 100%;
        height: 250px;
    }
    </style>
    """, unsafe_allow_html=True)

    chat_history = load_chat_history()
    image_scraper = AyurvedicImageScraper()

    # Layout: Two columns
    col1, col2 = st.columns([2, 1])  # Wider content on the left, images on the right

    with col1:  # Main content section
        st.title("Welcome to Vedabot :books:")
        st.markdown(
            """
            Vedabot helps you explore health solutions based on Ayurvedic knowledge. 
            Type your health-related question below and get instant insights.
            """
        )

        question = st.text_input(
            "Ask your health-related question here:",
            placeholder="e.g., What are Ayurvedic remedies for back pain?"
        )

        if st.button("Submit") and question.strip():
            with st.spinner("Finding the best Ayurvedic insights..."):
                response_data = handle_query(question)
                images = image_scraper.fetch_images(question)

            if response_data:
                formatted_response = f"""
                ### 🌿 Ayurvedic Insights
                {response_data.get('result', '')}

                ---
                **Note:** These remedies are complementary. Consult a healthcare provider for persistent issues.
                """
                st.success("Here are your results:")
                st.markdown(formatted_response, unsafe_allow_html=True)
                
                # Save the chat to history
                chat_entry = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "question": question
                }
                chat_history.append(chat_entry)
                save_chat_history(chat_history)
            else:
                st.warning("No relevant insights found. Please refine your query.")

    with col2:  # Sidebar for images
        st.markdown("### Related Ayurvedic Images")
        if question.strip():
            st.markdown('<div class="image-grid">', unsafe_allow_html=True)
            for image_url in images:
                st.markdown(f'<img src="{image_url}" class="rounded-image">', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar with chat history
    with st.sidebar:
        st.title("Vedabot")
        st.markdown("Your Ayurvedic Chatbot Assistant :herb:")
        st.image("https://t4.ftcdn.net/jpg/07/22/93/81/360_F_722938112_xunuELGTYPe4cb2JNKQRddTaghih3nfj.jpg", use_container_width=True)
       
        st.info("**Instructions:**\n- Enter your query related to health.\n- Receive Ayurvedic insights.\n- Consult a doctor if necessary.")

        if chat_history:
            st.markdown("### 💬 Chat History")
            for i, chat in enumerate(chat_history):
                st.markdown(f"**{chat['time']}** - {chat['question']}")

        if st.button("Clear Chat History"):
            os.remove("chat_history.json")
            st.success("Chat History has been cleared.")

    st.markdown("---")
    st.markdown("© 2024 Vedabot | Built with ❤️ for Ayurveda and AI.")

if __name__ == "__main__":
    main()