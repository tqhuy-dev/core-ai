from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI


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
