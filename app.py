from openai import OpenAI
from pymongo import MongoClient
from typing_extensions import override
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
import os
import streamlit as st
import json
assistant_id =  os.environ.get("ASSISTANT_ID") 

client = MongoClient(os.environ.get("MONGODB_ATLAS_URI"))
db = client['schema_design_db']


auth_collection=db['api_keys']

def auth_form():
    
    st.write("Please enter the API code to access the application.")
    api_code = st.text_input("API Code", type="password")
    if st.button("Submit"):
        st.toast("Authenticating...", icon="⚠️")
        db_api_key=auth_collection.find_one({"api_key":api_code})
        if db_api_key:
            st.session_state.authenticated = True
            st.session_state.api_code = api_code
            st.success("Authentication successful.")
            st.rerun()  # Re-run the script to remove the auth form
        else:
            st.error("Authentication failed. Please try again.")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def save_to_mongodb(thread_id, messages):
    thread_collection=db['threads']
    thread_collection.update_one({"_id": thread_id}, {"$set": {"messages": messages}},upsert=True)


def ai_chat(prompt, messages):
    
    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=prompt
        )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread.id,
        assistant_id=assistant_id)


    while not run.status == "completed":
        
        run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread.id,
        assistant_id=assistant_id)


    resp_messages = client.beta.threads.messages.list(
    thread_id=st.session_state.thread.id,
)
    for current_part in resp_messages.data[0].content:
        if current_part.type == "text":
            messages.code(current_part.text.value)
            


    st.session_state.messages.append({"role": "assistant", "content": resp_messages.data[0].content[0].text.value})
    st.rerun()

if not st.session_state.authenticated:
    auth_form()
else:
    
    client = OpenAI()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'thread' not in st.session_state:
        st.session_state.thread = client.beta.threads.create()







    st.markdown('## Chat with data generator')
    st.markdown("This assistant can generate meaningful data for MongoDB applications. Ask me !")
    if st.button("New Chat"):
            st.session_state.messages=[]
            
            st.session_state.thread = client.beta.threads.create()
            st.rerun()
    messages = st.container(height=500)

 

    for message in st.session_state.messages:
        with messages.chat_message(message["role"]):
            if message["role"] == "user":
                messages.markdown(message["content"])
            else:

                messages.code(message["content"])
                
                # save_to_mongodb(st.session_state.thread.id, resp_messages.data)
               
                        
                

    # Accept user input
    
    if len(st.session_state.messages) > 0:

        generated_message = st.session_state.messages[-1]
        if st.button("Generate Data from last message") and 'data' in generated_message["content"]:
            if generated_message is not None:
                generated_data = json.loads(generated_message["content"])
                for entity in generated_data['data']:
                
                    st.sidebar.expander(entity['entity']).code(f"""db.{entity['entity']}.insertMany({entity['documents']});""")
            else:
                st.warning("No data to generate. Please ask for data.")
            ## disable generate button    
    if prompt := st.chat_input("Be creative, lets design great MongoDB applications together..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with messages.chat_message("user"):
            messages.markdown(prompt)
            
        with messages.chat_message("assistant"):
            with st.spinner("I'm thinking..."):
                response = ai_chat(prompt, messages)
                
