# Install and Import Gradio, Pandas, Altair, Matplotlib, Os, and OpenAI (put this in "bot_libs.py" file and import it in one line as "import bot_libs" )
import pandas as pd
import os
import openai
from pathlib import Path #read in txt files for clean bot 


# Load Question DF
question_df = pd.read_excel('final_updated_cleaned_SS_questions.xlsx')

# Tool bot is designed to be the tool-using feature of the chat bot. 
# During the session it will be a second instance of GPT-3.5 that can use tools
# This gives pretty consistent behavior
with open('tool_bot_sys_content.txt', 'r') as file:
    tool_bot_sys_content = file.read()
#----------------------------------------------------------------------------------
def tool_bot(prompt, history=[]):
    messages =[
        {"role": "system", "content": tool_bot_sys_content}
    ]
       
    messages.append({'role': 'user', 'content': f'Here is my question or statement: {prompt}'}) # using f string to avoid prompt injections
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, #play with temp to get more factual responses
        max_tokens=10,#further limit output
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0
    )


    # saving the message we want to show to the user
    assistant_content = response['choices'][0]['message']['content']

    # Visual check for testing purposes
    print(response) 

    return assistant_content

#----------------------------------------------------------------------------------
#html parser bot
# bot should take url, grab certain data from the website
# should also be able to see if you failed the question and see what you submitted
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from bs4 import BeautifulSoup
import time

# Function that takes url as input
def html_scraper(url):

    # Path to the GeckoDriver executable
    GECKODRIVER_PATH = 'geckodriver'
    # Initialize the WebDriver
    options = webdriver.FirefoxOptions()
    service = FirefoxService(executable_path=GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    
    # Open a web page
    # url = input('url')
    driver.get(url)
    
    # Wait for JavaScript to load content (adjust time as needed)
    time.sleep(5)  # Wait for 5 seconds
    
    # Get HTML content
    html_content = driver.page_source
    
    # Get HTML content
    html_content = driver.page_source
    
    # Parse HTML content with Beautiful Soup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the first h1 tag
    h1_tag = soup.find('h1')
    
    # Print the content if the h1 tag exists
    if h1_tag:
        print("Content of the h1 tag:", h1_tag.text)
    else:
        print("No h1 tag found on the page.")
    
    # Close the browser
    driver.quit()
    return h1_tag.text
#url = input('url')
#question_short = html_scraper(url)
#print(question_short)

def extract_question_details(url):
    question_short = html_scraper(url)
    print(question_short)
    
    # Pulling out the question row
    question_row = question_df[question_df['question_short'] == question_short]

    # Convert DataFrame to numpy array to list to extract the string objects contained inside
    # Extract details from the filtered row
    hint = question_row['hint'].values[0]
    py_hint = question_row['python_hint'].values[0]
    question = question_row['question'].values[0]
    py_solution = question_row['python_solution'].values[0]

    # Return the extracted details as a dictionary
    return {
        "question": question,
        "hint": hint,
        "py_hint": py_hint,
        "py_solution": py_solution
    }

# Assuming you call the function somewhere and get the values
# For example: 
# question, hint, py_hint, py_solution = process_url("some_url_here")
with open('ai_tutor_sys_content.txt', 'r') as file:
        ai_tutor_sys_content = file.read()
# The AI Tutor Backend. It has a nested tool_bot function
# Which will trigger grabbing data from questions database
def construct_messages(question, hint, py_hint, py_solution,ai_tutor_sys_content):# Global messages list. The memory of the conversation is stored in this list
    nemessages = [{
        "role": "system",
        "content": ai_tutor_sys_content + f'''
        Here is the context to consider as you help the student:
        Question: 
        {question[0]}
        
        Hint: 
        {hint[0]}
        
        Python Hint (code snippet):
        {py_hint[0]}
        
        Solution: 
        {py_solution[0]}
        '''
    }]
    return construct_messages

#track index of conversation:
i = [0]
#denial_messages = messages #creating a separate history 

def ai_chat(prompt):
    messages =[]
    # calling messages variable inside the function
   
    global denial_messages
            
    tool_response = tool_bot(prompt) #this is another instance of OpenAI (basically another agent) to issue commands
    print(f'TOOL RESPONSE: {tool_response}')
    
    # Using tool_bot to analyze conversation and to respond accordingly. 
    # tool_response is
    if tool_response == 'OFF TOPIC' or tool_response == 'CAREER ADVICE':
        print("DENIAL LOGIC ACTIVATED")
        denial_messages.append({'role': 'user', 'content': f'''This is my prompt:
        
        Prompt: """ {prompt} """
        
        Kindly tell me to stay on the topic of python and data science and/or to avoid questions about career advice
        explain to me why my previous prompt was off topic in a sentence or 2.'''})
        response = openai.ChatCompletion.create(
             model="gpt-3.5-turbo",
             messages=denial_messages, #using this message histroy because I don't want to save this to convo history
             temperature=1, #play with temp to get more factual responses
             max_tokens=100,
             top_p=1,
             frequency_penalty=0,
             presence_penalty=0
         )
        token_count = response['usage']['total_tokens']
        if token_count >= 3000:
            denial_messages = [denial_messages[0]]
        assistant_content = response['choices'][0]['message']['content']
        # not appending message history
        #return assistant_content 
        
        
 

    messages.append({'role': 'user', 'content': f'{prompt}'}) #f string to avoid prompt injection errors from user
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1, #play with temp to get more factual responses
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )


    assistant_content = response['choices'][0]['message']['content']
    # hint = '' #this is parsing the json file that is the response reponse. you take the first item in choices list (a list of dictionaries), go to message key, and then go to content key 
    
    #print this in the CLI or notebook. This helps with understanding how the response json is structured for further customization
    print(f'''
    
    MESSAGE: {messages}
    
    RESPONSE:{response}
    
    ''')
    
    # Saving as variable to store the conversation history
    format_str = f'''
    User: {prompt}
    
    Response: {assistant_content}
    
    '''

   
    return assistant_content