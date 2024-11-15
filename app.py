import streamlit as st
from dotenv import load_dotenv



def main():
    load_dotenv()
    st.set_page_config(page_title="Vedabot",page_icon=":books:")
    st.header("Chat with Vedabot :books:")

    st.text_input("Ask A Question About health or Problem :")

    

if __name__=='__main__':
    main()