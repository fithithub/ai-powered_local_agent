# conda activate agent_env
# cd d:\rag y langchain\02_langchain\streamlit_propio
# streamlit run app.py

# import os
import random
from langchain_experimental.tools import PythonREPLTool
import streamlit as st
# from langchain_openai import AzureChatOpenAI
# from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage # , AIMessage, HumanMessage 
from langchain_community.chat_message_histories import StreamlitChatMessageHistory# , ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.prompts.chat import MessagesPlaceholder

from tools import *
from tools import llm_35, llm_4, llm_4o

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


# id for the session
session_id = str(random.randint(0, 1e30))

# system context
context = """
Speak in a posh accent. You are an expert in teas and you show disdain to those \
who do not know the difference between a Darjeeling and an Assam.
You are a tea connoisseur and you are the assistant of a tea shop clerk.
Speak in the same language as the user.
"""

# reset chat history
def clear_chat_history() -> None:
    msgs.clear()
    msgs.add_message(
        SystemMessage(content=context, additional_kwargs={"name":"system"})
    )
    msgs.add_ai_message("Chat with me to manage stocks, orders and more.")
    st.session_state.steps = {}

st.session_state.steps = {}

msgs = StreamlitChatMessageHistory()


prompt = hub.pull("hwchase17/openai-functions-agent")

# set of tools that the agent can use
tools = [table_retriever,order_update,stock_update,PythonREPLTool(),do_analysis, get_weather,mail_sender,ee_tool]

# agent = create_openai_functions_agent(llm_35, tools, prompt)
agent = create_openai_functions_agent(llm_4, tools, prompt)

# Agent executor and tools
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True, 
    return_intermediate_steps=True,
    kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")]
    })


agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: msgs,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Interface:
st.title('Fantasy Tea ERP')

# Delete history/memory
st.button(
    label="Clear chat history",
    on_click=clear_chat_history
)

if len(msgs.messages) == 0:
    clear_chat_history()

avatars = {"human": "user", "ai": "assistant", "system":"hide"}


# Show chat history
for idx, msg in enumerate(msgs.messages):
    if "name" in msg.additional_kwargs and msg.additional_kwargs["name"] == "system":
        continue
    with st.chat_message(avatars[msg.type]):
        st.write(msg.content)

# Chat input
if prompt := st.chat_input(placeholder="Hello. How can I help you?"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
        response = agent_with_chat_history.invoke({
            "input":prompt
        }, config={
            "configurable":{
                "session_id":session_id
            },
            "callbacks":[st_cb]
        })
        st.write(response['output'])
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]