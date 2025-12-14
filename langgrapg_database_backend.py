from langgraph.graph import StateGraph , START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3



import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyBduupIajbMOAu43Vt0ic0cZ1R_zsw2ui0"

# Initialize the model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",   # or "gemini-1.5-pro"
    temperature=0
)

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


class ChatState(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]
    
    
def chat_node(state: ChatState):
    
    # taeke user quary from state
    messages = state['messages'] 
    
    #  send the llm
    response = llm.invoke(messages)
    
    # response store state
    return {'messages':[response]}

conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)

# checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

# add node
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)



def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        
    return list(all_threads)