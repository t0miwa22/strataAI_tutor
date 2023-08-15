# Install and Import Gradio, Pandas, Altair, Matplotlib, Os, and OpenAI (put this in "bot_libs.py" file and import it in one line as "import bot_libs" )

import pandas as pd
import os
import openai
from pathlib import Path #read in txt files for clean bot 
from dotenv import load_dotenv

load_dotenv()

question_df = pd.read_excel('SS questions.xlsx')
openai.api_key = os.getenv("OPENAI_API_KEY") ##This isn't working for some reason
result = load_dotenv()
print(result)
# # Cleaning df (removing rows with #NAME?)
# question_df = question_df[(question_df != '#NAME?').all(axis=1)]
# Use GPT-3.5 to clean the data

def column_clean_bot(prompt, system_content):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY") ##This isn't working for some reason
    messages = [{'role': 'system', 'content': system_content }]
    messages.append({'role': 'user', 'content': prompt})
    

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1, #play with temp to get more factual responses. max of 2
        max_tokens=25,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    print(response) #print this in the CLI or notebook. This helps with understanding how the response json is structured for further customization
    system_message = response['choices'][0]['message']['content'] #this is parsing the json file that is the response reponse. you take the first item in choices list (a list of dictionaries), go to message key, and then go to content key 
    return system_message
    
# Cleaning question column
system_content = Path('question clean prompt.txt').read_text()

for index in range(len(question_df['question'])):
    entry = question_df['question'][index]
    
    if entry == '#NAME?':
        # at the index pick out the question short and python hint, save as variables
        question = question_df['question'][index]  
        hint = question_df['hint'][index]  
        py_solution = question_df['python_solution'][index]
        py_hint = question_df['python_hint'][index]

        # insert those variables into multiline string that inserts variables into the string. save this multiline string as a variable
        prompt = f'''
        QUESTION:

        
        HINT:
        {hint}
        
        PYTHON SOLUTION:
        {py_solution}

        PYTHON HINT:
        {py_hint}

        '''

        # insert multiline string variable into prompt of column_clean_bot
        cleaned_entry = column_clean_bot(prompt, system_content)

        # save clean bot's guess as the new entry at this index
        question_df['question'][index] = cleaned_entry

# save output
question_df.to_csv('question_df.csv', index=False)