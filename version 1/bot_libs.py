# Install and Import Gradio, Pandas, Altair, Matplotlib, Os, and OpenAI (put this in "bot_libs.py" file and import it in one line as "import bot_libs" )
import gradio as gr
import pandas as pd
import altair
import matplotlib as plt
import os
import openai

import os
import openai
import gradio as gr

messages = []

# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = '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'
def CustomChatGPT(user_input):
    messages.append({'role': 'user','content' : user_input})
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = messages
    )
    ChatGPT_reply = response['choices'][0]['message']['content']
    messages.append({'role':'assistant' , 'content' : ChatGPT_reply})
    return ChatGPT_reply

demo = gr.Interface(fn=CustomChatGPT, inputs = 'text', outputs = 'text', title = 'AI Tutor')

demo.launch()