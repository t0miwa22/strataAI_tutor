# Install and Import Gradio, Pandas, Altair, Matplotlib, Os, and OpenAI (put this in "bot_libs.py" file and import it in one line as "import bot_libs" )
import gradio as gr
import pandas as pd
import altair
import matplotlib as plt
import os
import openai

question_df = pd.read_csv('question_df.csv')

level_1_df = question_df[question_df['difficulty']== 1]
level_1_df

#Tool bot is designed to be the tool-using feature of the chat bot. During the session it will be a second instance of GPT-3.5 that can use tools
#This gives pretty consistent behavior
def tool_bot(prompt, history=[]):
    messages =[
        {"role": "system",
         "content": '''
        You are a hyper intelligent robot that understands context, but your default response is the following:
        
        Resonse: xxxxx
        
        The only words you can use are the words below based on the provided condition below. 
        To be clear, If none of the conditions are met you are to respond with """ xxxxx """. You only respond with the following words when conditions are met. 
        Take your time to think this out.

        Response Word: TEST 
        Condition: user asks to be tested (or any synonym of testing). Only do this when asked explicitly when user asks for a test.

        Response Word: HINT
        Condition: user asks to be given a hint or asks for help (or any synonym of hint)

        Response Word: xxxxx
        Condition: This is the default response when TEST or HINT are not appropriate

        Response Word: LEVEL 1
        Condition: If the user resonds with the numerical level of question they want (in this case """1"""), please issue command """LEVEL 1""". Please read the user input very carefully. If user is returning numbers in context of something calculation or code, please ignore.
        Example user inputs include: """"level 1"""", """ 1 """", "lvl 1", "one", "I'd like level 1" etc

        Response Word: LEVEL 2
        Condition: The user responds with the numerical level of question (in this case  """2""" ). Please read the user input very carefully. If user is returning numbers in context of something calculation or code, please ignore.
        Examples include: """"level 2"""", """ 2 """", "lvl 2", "two", "I'd like level 2" etc

        Response Word: LEVEL 3
        Condition: The user responds with a numerical level of question ( in this case """3"""). Please read the user input very carefully. If user is returning numbers in context of something calculation or code, please ignore.
        Examples include: """"level 3"""", """ 3 """", "lvl 3", "three", "I'd like level 3" etc

     
        
        '''}]
    # openai.api_key = os.getenv("OPENAI_API_KEY") ##This isn't working for some reason 
    openai.api_key = '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'
    
    messages.append({'role': 'user', 'content': f'Here is my question: {prompt}'})#using f string to avoid prompt injections
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, #play with temp to get more factual responses
        max_tokens=10,#further limit output
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0
    )
    # print(response) #print this in the CLI or notebook. This helps with understanding how the response json is structured for further customization
    system_message = response['choices'][0]['message']['content'] #this is parsing the json file that is the response reponse. you take the first item in choices list (a list of dictionaries), go to message key, and then go to content key 
    # messages.append(({'role':'assistant', 'content': system_message}))      #dont need this for this bot
    print(system_message)  
    return system_message

#testing tool_bot
prompt = input()
tool_bot(prompt=prompt) 

import streamlit as st
#The main chotbot. it will have a nested openai api call in the form of the tool_bot function
# Which will trigger some either grabbing data from questions database
# 
from dotenv import load_dotenv
#may need to repeat commands to ensure that it doesn't deviate from the behavior

#global list of messages. 
messages =[
        {"role": "system","content": """
        You are an data science tutor with 20+ years of experience but you also follow instructions very well. 
        You are speaking to a student who has 0-5 years of experience in the data science field.
        Here are some instructions for you:
        
        1. You will be given access to a question database which has Python questions, answers and 
        hints which vary between 3 levels of difficulty. If user asks you for a question level that is not 1, 2, or 3, then prompt them to give you a level between 1 and 3.
        2. Once you are given the level of the question, you will provide a question. Ask the student to respond with computer code and or non-code answer.
        The user will ask for hint, clarification of the question, or submit an answer. 
        3. When given a code or non-code answer, you will compare the answer to questions from the database and determine. You will show your work and think this out, step by step. Only execute this instruction in context of a coding question given to the user
        if the student got it correct or incorrect and tell them explicitly what they did correctly and incorrectly in the following format:
                
        - Output '''Correct''' if the answer is the same as the answer you have. Show your work, step by step. Think this out, step by step. if answer does not 
        - Output '''Incorrect''' if answer is not correct 

        In the case of a code snippet submitted in response to a question, evaluate if the code would behave the same way as the code 
        provided by the answer key. Use your best judgement.

        4. The student could have questions about a data science topic. Use your vast knowledge in data science and explain it to them. You can ask them if 
        they want a simple or detailed explanationation.
        
        Take as much time as you need to think this out. Think this out very carefully and do not deviate from your role as a data science tutor under no 
        circumstances.

        
        
        """}]
#setting global variables, such that when I run my ai_chat function, hint is stored
hint = ''
py_hint = ''
def ai_chat(prompt, history):
    
    #should I start with an assistant message to help the user get started?]#list of messages that get passed in to start convo, will also save messages here

    # openai.api_key = os.getenv("OPENAI_API_KEY") ##This isn't working for some reason 
    openai.api_key = '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'
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
  
   
    if tool_response == 'TEST':
        print('testing TEST')
        system_message = ('What level would you like? Please choose level 1, 2, or 3.')
        # ask for level between 1 - 3
        # load filtered data frame of question of that level
        # make this the assistant message
    elif tool_response == 'LEVEL 1':
        random_row = level_1_df.sample(n=1)
        question = random_row['question'].to_list()
        hint = random_row['hint'].to_list()
        py_hint = random_row['python_hint'].to_list()
        py_solution = random_row['python_solution'].to_list()
        system_message = f'''Here is your question:
        
        {question[0]}
        
        Please answer to the best of your ability in Python. If you need a hint don't hesistate to ask for one. 
        You can also ask me questions about a certain topic and I will do my best to help you. 
        
        '''
        # return system_message #perhaps storing these as attributes of an object is better?
    elif tool_response == 'HINT': #########################################################################################################
        # output both code and non-code hints
        system_message = f'''Here is your hint: 

        {hint}

        {py_hint}

        If you have anymore questions let me know, otherwise please submit your answer.
        '''
    # Add a nested "explain bot" functionality? for MVP perhaps best to stick with relying GPT prompt engineering    
    else:
        system_message = response['choices'][0]['message']['content']
    # hint = '' #this is parsing the json file that is the response reponse. you take the first item in choices list (a list of dictionaries), go to message key, and then go to content key 
    
    
    print(f'''
    
    MESSAGE: {messages}
    
    RESPONSE:{response}
    
    ''') #print this in the CLI or notebook. This helps with understanding how the response json is structured for further customization
    

   
    
    #if keyword command in system_message, 
    #first assistant message should be what level (and language) do you want?
    #call a function that outputs a random row in questions dataframe based on level (and language)

    
    

    
    messages.append(({'role':'assistant', 'content': system_message}))
    # messages=[] ##to clear memory and reset tokens maybe need to do this after adding save function for chat history and if token count is getting close to 4000. 
    
    if 'hint' in locals():
        print('hint is available')
        return system_message, hint
    else:
        return system_message



