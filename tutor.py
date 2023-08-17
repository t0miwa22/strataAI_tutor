import streamlit as st
import openai
import os
import pandas as pd
import pandasql as ps  # Ensure you have this library installed

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_KEY')

experience_levels = {
    'Easy': '0-1 year',
    'Medium': '1-3 years',
    'Hard': '3-5 years'
}

# Initialize chat history and other session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "experience_level" not in st.session_state:
    st.session_state.experience_level = 'Easy'
if "hints_given" not in st.session_state:
    st.session_state.hints_given = 0
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 1. Upload Dataset
uploaded_file = st.file_uploader("Upload your dataset (.csv)", type="csv")
if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"An error occurred while reading the CSV: {e}")

# 2. Integrate Data Querying
def get_solution_type(question):
    # Mock function to determine solution type. Adjust as needed.
    if "sql" in question.lower():
        return "SQL"
    elif "pandas" in question.lower():
        return "pandas"
    else:
        return None

def execute_sql_solution(solution_code, data):
    try:
        result = ps.sqldf(solution_code, locals())
        return result
    except Exception as e:
        st.error(f"SQL Error: {e}")

def execute_pandas_solution(solution_code, data):
    try:
        local_dict = {'data': data}
        exec(solution_code, globals(), local_dict)
        return local_dict.get('result')
    except Exception as e:
        st.error(f"Pandas Error: {e}")

# Accept user input
if prompt := st.chat_input("How can I help?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 4. Modify the OpenAI Prompt
    dataset_note = "The user provided a dataset. " if st.session_state.uploaded_data is not None else ""
    ai_context = f"""
    {dataset_note}
    ## Hints
    ...
    For each user query, provide a series of clear and concise hints in the following format:

Hint #1: Start with a high-level overview of the problem, describing the main objective and the core concepts involved.

Hint #2: Dive deeper into the solution, offering a more detailed explanation and, if applicable, a relevant code snippet that addresses part of the user's query.

Hint #3: Conclude with a comprehensive solution, ensuring it's clear and concise, and provide the complete code or explanation that fully addresses the user's query.

Always adapt your responses based on the user's proficiency in data science, which can range from beginner (0-1 year), intermediate (1-3 years), to advanced (3-5 years).

Your primary objective: Guide users progressively towards a solution using a series of hints, ensuring each hint builds upon the last and culminates in a comprehensive answer.

Remember, the essence is progression. Each hint should naturally lead to the next, culminating in a holistic solution. And always be mindful of the user's data science expertise level, tailoring your hints from beginner stages to advanced intricacies.

The user with {experience_levels[st.session_state.experience_level]} experience asked: {prompt}

## Walkthroughs
---
Given a data science or programming challenge, provide a detailed walkthrough that breaks down the solution step by step. Begin with a clear understanding of the problem statement, followed by a logical progression of steps to tackle the challenge. For each step, offer a concise explanation of its purpose and relevance. If the solution involves coding or specific algorithms, integrate relevant code snippets within the explanations to provide a practical perspective. Ensure that the walkthrough is comprehensive, guiding the reader from the initial understanding of the problem to the final solution, and conclude with an interpretation or summary of the results.

When presented with a data science or programming challenge, provide a comprehensive solution that follows a structured approach. Begin by clearly restating the problem for clarity. Then, break down the solution into a series of logical steps, ensuring each step is explained in detail. If the solution involves coding, algorithms, or specific techniques, integrate relevant code snippets or examples within the explanations, ensuring they are clear and directly address the step in question. Conclude with an interpretation or summary of the results, highlighting the significance of the solution. The goal is to offer a solution that is both detailed and easy to follow, allowing readers to understand the logic and methodology behind each step.

## Edge Cases
---
When presented with a data science or programming challenge, identify and elaborate on potential edge cases that could affect the solution or its interpretation. For each edge case:

1. **Title the Edge Case**: Provide a concise title that summarizes the nature of the edge case.
2. **Detailed Explanation**: Offer a clear and detailed explanation of the edge case, highlighting its significance and potential impact on the solution.
3. **Solution Implications**: If applicable, describe how the edge case might affect the proposed solution, and any considerations or adjustments that might be needed to address it.

The goal is to provide a comprehensive understanding of the nuances and intricacies of the problem, ensuring that the solution is robust and accounts for all potential scenarios.
"""
    
    # Construct the messages for OpenAI
    system_message = {
        "role": "system",
        "content": ai_context
    }
    user_message = {
        "role": "user",
        "content": prompt
    }
    conversation_history = st.session_state.messages + [system_message, user_message]

    # Generate assistant response using OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            temperature=0.3,
            max_tokens=500
        )
        assistant_response = response.choices[0].message['content']

        # Execute data querying based on response and display results
        solution_type = get_solution_type(prompt)
        if solution_type == "SQL":
            result = execute_sql_solution(assistant_response, st.session_state.uploaded_data)
            st.write(result)
        elif solution_type == "pandas":
            result = execute_pandas_solution(assistant_response, st.session_state.uploaded_data)
            st.write(result)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        st.error(f"OpenAI API Error: {e}")