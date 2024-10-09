import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from master import Master

# app config
st.set_page_config(page_title="Chat with Multi Agents", page_icon="🤖")
st.title("Welcome to Multi Agent Chat")

if "master_instance" not in st.session_state:
    st.session_state.master_instance = Master()
    print("******* Instance initiated *******")

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]

user_query = st.chat_input("Type your message here...")

if user_query is not None and user_query != "":
        model = st.session_state.master_instance
        #model.chatHistory = st.session_state.chat_history
        response = model.invoke([HumanMessage(content=user_query)],{"configurable": {"thread_id": 42}})
        #print(sources)
        #response = f"{response}  \n\n  {''}"

        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)