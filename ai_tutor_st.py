import os
import openai
import pandas as pd
import re
import warnings

warnings.filterwarnings("ignore")
import streamlit as st


data = pd.read_excel(r'final_updated_cleaned_SS_questions.xlsx')


# Function to interact with OpenAI's GPT using chat models
def get_completion_from_chat(prompt,
                             model="gpt-3.5-turbo",
                             temperature=0,
                             presence_penalty=1,
                             frequency_penalty=1
                            ):
    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}]
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        max_tokens=500
    )
    
    return response.choices[0].message["content"].strip()

# Function to fetch initial response from dataset
def get_initial_response(query, request_type, known_question_data=None):
    if not known_question_data:
        return "Sorry, I couldn't find the requested information in the dataset."
    if request_type == "Get Walkthrough":
        return known_question_data['python_solution']
    elif request_type == "Show Edge Cases":#
        return "Sorry, edge cases are not explicitly mentioned in the dataset. Would you like to get potential edge cases based on the problem?"
    elif request_type == "Explain Solution":
        return known_question_data['python_solution']
    else:
        return "Unknown request."

# Function to generate detailed response based on user input and context
def custom_query_response(query, request_type, known_question_data=None):
    prompt = ""  # Initialize the prompt
    
    if known_question_data:
        # Craft prompt based on known data
        if request_type == "Get Walkthrough":
            prompt = (f"Please elaborate on the solution for the following problem. Provide steps of walkthroughs and include an example of code in each step: "
                      f"{known_question_data['question']}. Solution: {known_question_data['python_solution']}. "
                      f"Can you provide a step-by-step walkthrough?")
        elif request_type == "Show Edge Cases":
            prompt = (f"For the problem: {known_question_data['question']} and its hint: "
                      f"{known_question_data['python_hint']}, what are potential edge cases to consider? Provide the list of edge cases that the solution might have. Provide some code examples.")
        elif request_type == "Explain Solution":
            prompt = (f"Please provide a more detailed explanation for the solution of the problem. Provide full code function for the solution. Please put some comments in the code for clarification.: "
                      f"{known_question_data['question']}. Solution: {known_question_data['python_solution']}.")
    
    
    # If no data is found, handle general queries
    if not prompt:  # If the prompt hasn't been set yet
        if request_type == "Get Walkthrough":
            prompt = f"Provide a step-by-step walkthrough for the general programming problem: {query}"
        elif request_type == "Show Edge Cases":
            prompt = f"What are potential edge cases for the general programming problem: {query}?"
        elif request_type == "Explain Solution":
            prompt = f"Provide a detailed explanation for the general programming problem: {query}"
        else:
            prompt = f"Can you provide assistance for the general programming problem or topic: {query}?"

    response = get_completion_from_chat(prompt)
    return response

# Comprehensive list of Python-related programming keywords
# Python's built-in keywords
python_keywords = [
    "False", "None", "True", "and", "as", "assert", "async", "await", 
    "break", "class", "continue", "def", "del", "elif", "else", "except", 
    "finally", "for", "from", "global", "if", "import", "in", "is", 
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", 
    "try", "while", "with", "yield"
]

# Common built-in functions
python_functions = [
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
    "callable", "chr", "classmethod", "compile", "complex", "delattr",
    "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter", 
    "float", "format", "frozenset", "getattr", "globals", "hasattr", 
    "hash", "help", "hex", "id", "input", "int", "isinstance", "issubclass", 
    "iter", "len", "list", "locals", "map", "max", "memoryview", "min", 
    "next", "object", "oct", "open", "ord", "pow", "print", "property", 
    "range", "repr", "reversed", "round", "set", "setattr", "slice", 
    "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", 
    "vars", "zip"
]

# Common terms related to Python data structures and operations
python_data_structures = [
    "array", "cast", "copy", "deepcopy", "delete", "deque", "dictionary", 
    "element", "extend", "index", "insert", "item", "key", "last", "list",
    "mapping", "order", "pop", "prepend", "push", "queue", "remove", "reverse",
    "sequence", "slice", "stack", "string", "tuple", "value", "variable"
]

# Other commonly used terms in the Python community
python_common_terms = [
    "algorithm", "API", "argument", "attribute", "byte", "bytecode", "decorator", 
    "docstring", "exception", "expression", "framework", "function", "generator", 
    "inheritance", "interpreter", "iterator", "library", "loop", "method", 
    "module", "operator", "parameter", "pointer", "recursion", "reference", 
    "regular expression", "script", "statement", "syntax", "thread", "type"
]

# Combine all the lists
comprehensive_python_keywords = python_keywords + python_functions + python_data_structures + python_common_terms

def contains_comprehensive_python_keyword_refined(query):
    """Refined check if the query contains any of the comprehensive Python-related programming keywords."""
    query = query.lower()
    return any(keyword in query for keyword in map(str.lower, comprehensive_python_keywords))

def respond_to_query(input_text, dropdown_selection, request_types, further_clarification, context):
    if input_text and input_text != "Type your question or select from the dropdown.":
        input_query = input_text
    else:
        input_query = dropdown_selection
    
    # If the query exists in the database
    if input_query in data['question'].values:
        question_data = data[data['question'] == input_query].iloc[0].to_dict()
        
        # If further clarification is not sought, get the initial response
        if not further_clarification:
            response = get_initial_response(input_query, request_types, known_question_data=question_data)
        # If further clarification is sought, get a custom response based on the data
        else:
            response = custom_query_response(input_query, request_types, known_question_data=question_data)
    # If the query doesn't exist in the database
    else:
        # Check if the query contains any Python-related keyword
        if contains_comprehensive_python_keyword_refined(input_query):
            response = custom_query_response(input_query, request_types)
        else:
            response = f"The question doesn't seem to be related to Python programming. Please provide a more specific Python-related question or choose from the provided options."
    # Return response formatted in markdown for code
    return f"```{response}```"



