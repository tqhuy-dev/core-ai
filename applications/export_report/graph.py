from typing import TypedDict, List, Optional

from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import create_retriever_tool, Tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END
class AgentState(TypedDict):
    excel_file: Optional[bytes]  # Raw uploaded Excel file
    documents: Optional[List[Document]]
    vectorstore: Optional[any]
    tool: Optional[Tool]
    prompt: Optional[str]
    json_template: Optional[dict]
    analysis_result: Optional[dict]

def load_excel_and_convert_to_documents(state: AgentState):
    df = pd.read_excel(state["excel_file"])

    chunks = []
    for idx, row in df.iterrows():
        row_text = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        chunks.append(row_text)

    docs = [Document(page_content=chunk) for chunk in chunks]
    state['documents'] = docs
    return {"documents": docs}

def vectorize_documents(state: AgentState):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(state["documents"])
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(split_docs, embedding=embeddings)
    return {"vectorstore": vectorstore}

# retriever_tool = create_retriever_tool(
#     retriever,
#     "retrieve_blog_posts",
#     "Search and return information about Lilian Weng blog posts.",
# )

def get_tool(state: AgentState):
    retriever = state["vectorstore"].as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_documents",
        "Search and return information documents",
    )
    return {"tool": retriever_tool}

def generate_query_or_respond(state: AgentState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    llm = ChatOpenAI(temperature=0, model='gpt-4')
    response = (
        llm
        .bind_tools([state['tool']]).invoke(state["prompt"])
    )
    return {"analysis_result": [response]}

# def query_vectorstore(state: AgentState):
#     retriever = state["vectorstore"].as_retriever()
#     llm = ChatOpenAI(temperature=0, model='gpt-4')
#
#     custom_prompt = ChatPromptTemplate.from_template(
#         """You acting as a professional data analyst.
#         Based on the provided data set, perform in-depth analysis and evaluation.
#         Focus on making valuable comparisons, important statistics (such as min, max, average),
#         and potential relationships between elements in the data.
#         The goal is to help readers understand the big picture, detect trends, anomalies,
#         or actionable insights, and suggest appropriate visual charts to effectively present the information.
#
#         {context}
#
#         Question: {question}
#         """
#     )
#     conversation_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
#         combine_docs_chain_kwargs=custom_prompt,
#     )
#     result = conversation_chain.invoke({"question": state["prompt"]})
#     return {"analysis_result": result['answer']}

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node('load_excel_and_convert_to_documents', load_excel_and_convert_to_documents)
    workflow.add_node('vectorize_documents', vectorize_documents)
    workflow.add_node('get_tool', get_tool)
    workflow.add_node('generate_query_or_respond', generate_query_or_respond)

    workflow.set_entry_point("load_excel_and_convert_to_documents")
    workflow.add_edge('load_excel_and_convert_to_documents', 'vectorize_documents')
    workflow.add_edge('vectorize_documents', 'get_tool')
    workflow.add_edge('get_tool', 'generate_query_or_respond')
    workflow.add_edge('generate_query_or_respond', END)

    return workflow.compile(name="Report Analysis Workflow",)