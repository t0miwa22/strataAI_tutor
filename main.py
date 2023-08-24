
import os
import openai
import pandas as pd
import re
import warnings
import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from bs4 import BeautifulSoup
import time
import sqlite3

warnings.filterwarnings("ignore")

from ai_tutor_backend import tool_bot, html_scraper, ai_chat, process_url
#from db_handler import create_tables, insert_message, get_chat_history, close_connection
from ai_tutor_st import custom_query_response,respond_to_query
openai.api_key = os.getenv('OPENAI_KEY')

data = pd.read_excel(r'final_updated_cleaned_SS_questions.xlsx')
faq = pd.read_excel(r'ai_tutor_faqs.xlsx')

# Comprehensive list of Python-related programming keywords
# Python's built-in keywords

def handle_user_interaction():
    # URL input for context understanding
    url_input = st.text_input("Provide the URL of the question:", "")
    
    # Display FAQ options
    faq_options = ["Select from common questions"] + faq['FAQs'].head(7).tolist()
    dropdown_selection = st.selectbox("Select FAQ:", faq_options)

    # Get user input
    user_input = st.chat_input("Type your question or select from the dropdown.")
    
    # Checkboxes for additional info
    col1, col2, col3 = st.columns(3)
    get_walkthrough = col1.checkbox("Get Walkthrough")
    show_edge_cases = col2.checkbox("Show Edge Cases")
    explain_solution = col3.checkbox("Explain Solution")
    further_clarification = st.checkbox("Seek further clarification?")
    
    # Process checkboxes
    selected_request_types = []
    if get_walkthrough:
        selected_request_types.append("Get Walkthrough")
    if show_edge_cases:
        selected_request_types.append("Show Edge Cases")
    if explain_solution:
        selected_request_types.append("Explain Solution")
    
    # If user provides input or selects an FAQ
    if user_input or dropdown_selection != "Select from common questions":
        # Display user's input or FAQ selection
        with st.chat_message("user"):
            st.markdown(user_input if user_input else dropdown_selection)
        
        # Generate AI response based on user input, URL, FAQ selection, and checkbox selections
        context = f"URL Context: {url_input}" if url_input else "No context provided."
        response = respond_to_query(user_input if user_input else dropdown_selection, dropdown_selection, selected_request_types, further_clarification, context)
        
        # Display AI's response
        with st.chat_message("assistant"):
            st.markdown(response)


def main():
    st.title("Stratascrath Tutor")
    handle_user_interaction()

if __name__ == "__main__":
    main()



