# Install and Import Gradio, Pandas, Altair, Matplotlib, Os, and OpenAI (put this in "bot_libs.py" file and import it in one line as "import bot_libs" )
import gradio as gr
import pandas as pd
import os
import openai
from pathlib import Path #read in txt files for clean bot 
from dotenv import load_dotenv

# Load Question DF
question_df = pd.read_csv('question_df.csv')

# Tool bot is designed to be the tool-using feature of the chat bot. 
# During the session it will be a second instance of GPT-3.5 that can use tools
# This gives pretty consistent behavior
with open('tool bot sys content.txt', 'r') as file:
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
    GECKODRIVER_PATH = 'geckodriver.exe'
    
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
    
    # # Parse HTML content with Beautiful Soup...used to get all tags and explore data
    # soup = BeautifulSoup(html_content, 'html.parser')
    # for tag in soup.find_all(True):
    #     print(f"Tag: {tag.name}")
    #     print(f"Attributes: {tag.attrs}")
    #     content = str(tag.contents).strip()
    #     print(f"Content: {content[:100]}...") if len(content) > 100 else print(f"Content: {content}")
    #     print("-" * 50) # Separator line
    # ... (other code)
    
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

url = input('url')
question_short = html_scraper(url)
print(question_short)

#----------------------------------------------------------------------------------

# Pulling out the question row
question_row = question_df.loc[question_df['question_short'] == question_short]
# print(question_row)

# convert DataFrame to numpy array to list in order to extract the string objects contained inside
hint = question_row['hint'].values.tolist()
py_hint = question_row['python_hint'].values.tolist()
question = question_row['question'].values.tolist()
py_solution = question_row['solution'].values.tolist()

print(f'''{question[0]}

{hint[0]}

{py_hint[0]}

{py_solution[0]}
''')

#----------------------------------------------------------------------------------
# The AI Tutor Backend. It has a nested tool_bot function
# Which will trigger grabbing data from questions database
with open('ai tutor sys content.txt', 'r') as file:
    ai_tutor_sys_content = file.read()


# # we store the 0 index with an placeholder '' string so that we don't get index error for index being out of range. 

# hint = ['']
# py_hint = ['']
# question = ['']
# py_solution = ['']

# Global messages list. The memory of the conversation is stored in this list
messages =[{"role": "system","content": ai_tutor_sys_content + f'''
Here is the context to consider as you help the student:
Question: 
{question[0]}

Hint: 
{hint[0]}

Python Hint (code snippet):
{py_hint[0]}

Solution: 
{py_solution[0]} '''}]

#track index of conversation:
i = [0]

load_dotenv()
def ai_chat(prompt, history):
    # calling messages variable inside the function
    global messages
    
    # Introduction message
    
    #should I start with an assistant message to help the user get started?]#list of messages that get passed in to start convo, will also save messages here

    openai.api_key = os.getenv("OPENAI_API_KEY") ##This isn't working for some reason 
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

    tool_response = tool_bot(prompt) #this is another instance of OpenAI (basically another agent) to issue commands
    #initating empty variables for use later:


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

    # Saving content to a text file
    # Open a file in write mode, 'a' argument serves as appending to
    with open('saved_chat.txt', 'a') as file:
        file.write(format_str)

    #add token counter and a way to handle hitting token limit.  
    # Prob summarizing previous assistant/student info into 2-4 sentences, 3000 tokens is safe place to start summary
    token_count = response['usage']['total_tokens']
    if token_count >= 3000:
        # Reload message history text for summarization. Better formatted than parsing the response JSON
        # content_txt = Path('saved_chat.txt').read_text() 
        # summary_str[0] = summarize_bot_saved(content_txt)
        messages = [messages[0]] # basically erase the memory except the system message and kept it as a list
        # print(f'This is the `messages` memory: {summary_str}')
    
    messages.append(({'role':'assistant', 'content': assistant_content}))
    absolute_path = os.path.abspath('matt/Most Profitable Companies faq.html')
    print(absolute_path)

    if i[0] == 0:
        # assistant_content = f'''<a href="{absolute_path}" target="_blank">Click here</a>'''
        assistant_content = "Hi there! I am your AI Tutor. Please click the FAQ button to download a list of FAQs for this particular question"
        i[0] += 1
   
    
    return assistant_content

demo = gr.ChatInterface(
    fn=ai_chat, 
    submit_btn = 'Submit', 
    retry_btn = 'Retry',
    clear_btn = 'Clear',
    title = 'AI Tutor V1',
    #add a save convo button that can create html file that can then be printed like a pdf later
    )

demo.launch()