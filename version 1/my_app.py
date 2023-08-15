import streamlit as st

if 'messages' not in st.session_state:
    st.session_state.messages = []



    
    st.session_state['openai_model'] = 'gpt-3.5
#Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

#react to user input
if prompt := st.chat_input('ajldj;')
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        response = 
        # Display assistant response in chat message container
        with st.chat_message('assistant'):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({'role': 'assistant', 'content': response})


    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ''
        for response in 