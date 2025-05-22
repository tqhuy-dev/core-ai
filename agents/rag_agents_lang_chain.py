from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from langchain_core.tools import tool
class SearchInternalDocuments(BaseModel):
    """Search for internal documents"""
    query: str = Field(..., description="The query to search for internal documents")


class RAGAgentLangChainOpenAI(object):
    def __init__(self, memory: ConversationBufferMemory, vector_store: Chroma, prompt_template: str, llm:ChatOpenAI,
                 callbacks=None):
        if callbacks is None:
            callbacks = [StdOutCallbackHandler()]
        self.memory = memory
        self.vector_store = vector_store
        self.prompt_template = prompt_template
        self.llm = llm
        self.callbacks = callbacks
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vector_store.as_retriever(),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self.prompt_template},
            callbacks=self.callbacks
        )

    def invoke(self, input_text: str):
        return self.conversation_chain.invoke({"question": input_text})


def rag_search_internal_documents(ragAgents: RAGAgentLangChainOpenAI):
    @tool("search_internal_documents", args_schema=SearchInternalDocuments)
    def search_internal_documents_tool(query: str) -> str:
        result = ragAgents.invoke(query)
        return result["answer"]

    return search_internal_documents_tool
