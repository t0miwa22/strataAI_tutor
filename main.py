import openai
import streamlit as st
import pandas as pd
import os
from pathlib import Path #read in txt files for clean bot
import re
import warnings

from ai_tutor_backend import tool_bot, html_scraper, ai_chat
from ai_tutor_st import get_completion_from_chat, get_initial_response, custom_query_response,contains_comprehensive_python_keyword_refined,respond_to_query
openai.api_key = os.environ.get('API_KEY')

data = {"question": ["Sample Question 1", "Sample Question 2"]}

# Title
def main():st.title("AI Tutor Chatbot")


# Streamlit interface setup
user_input = st.text_input("Type Your Question", "Type your question or select from the dropdown.")
dropdown_selection = st.selectbox("Or Select a Question", ["Select from common questions"] + data['question'])
request_type = st.radio("Request Type", ["Get Walkthrough", "Show Edge Cases", "Explain Solution"])
further_clarification = st.checkbox("Seek further clarification?")

# Setup for multiple buttons
submit_button, clear_button = st.columns(2)

if submit_button.button('Submit'):
    response = respond_to_query(user_input, dropdown_selection, request_type, further_clarification)
    st.write(response)

# Placeholder for clear button functionality
if clear_button.button('Clear'):
    st.write("Cleared!")

if __name__ == "__main__":
    main()