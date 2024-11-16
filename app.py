import streamlit as st
import os
from dotenv import load_dotenv
from model import handle_query

def main():
    load_dotenv()

    # Set up the page
    st.set_page_config(
        page_title="Vedabot - Your Health Companion",
        page_icon=":books:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar
    with st.sidebar:
        st.title("Vedabot")
        st.markdown("Your Ayurvedic Chatbot Assistant :herb:")
        st.image("https://t4.ftcdn.net/jpg/07/22/93/81/360_F_722938112_xunuELGTYPe4cb2JNKQRddTaghih3nfj.jpg", use_container_width =True)  # Replace with your logo URL or local image
        st.info("Powered by advanced AI embeddings and Ayurvedic wisdom.")
        st.markdown("**Instructions:**\n- Enter your query related to health.\n- Receive Ayurvedic insights.")

    # Main content
    st.title("Welcome to Vedabot :books:")
    st.markdown(
        """
        Vedabot helps you explore health solutions based on Ayurvedic knowledge. 
        Type your health-related question below and get instant insights.
        """
    )
    
    # User query input
    question = st.text_input(
        "Ask your health-related question here:",
        placeholder="e.g., What are Ayurvedic remedies for cold?",
    )

    # Query handling
    if st.button("Submit") and question:
        with st.spinner("Finding the best Ayurvedic insights..."):
            response = handle_query(question) 
        
        if response:
            st.success("Here are your results:")
            st.markdown(response)
        else:
            st.warning("No relevant insights found. Please refine your query.")

    # Footer
    st.markdown("---")
    st.markdown("© 2024 Vedabot | Built with ❤️ for Ayurveda and AI.")

if __name__ == "__main__":
    main()
