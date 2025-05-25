from typing import TypedDict, Optional, Literal

from langchain.chat_models import init_chat_model
from langchain_core.tools import Tool
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )
def init_graph_agent(toolNode: Tool) -> CompiledStateGraph:
    ll_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    grade_prompt = (
        "Use the information below to answer the user's question. "
        "If you can't find a suitable answer, just say you don't know. "
        "Don't give wrong or incorrect answers. "
        "{context} "
        "Question: {question} "
    )
    def generate_query_or_respond(state: MessagesState):
        """Call the model to generate a response based on the current state. Given
        the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
        """
        response = (
            ll_model
            .bind_tools([toolNode]).invoke(state["messages"])
        )
        return {"messages": [response]}

    def grade_documents(
            state: MessagesState,
    ) -> Literal["generate_answer", "rewrite_question"]:
        """Determine whether the retrieved documents are relevant to the question."""
        question = state["messages"][0].content
        context = state["messages"][-1].content

        prompt = grade_prompt.format(question=question, context=context)
        response = (
            ll_model
            .with_structured_output(GradeDocuments).invoke(
                [{"role": "user", "content": prompt}]
            )
        )
        score = response.binary_score

        if score == "yes":
            return "generate_answer"
        else:
            return "rewrite_question"

    def rewrite_question(state: MessagesState):
        rewrite_prompt = (
            "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
            "Here is the initial question:"
            "\n ------- \n"
            "{question}"
            "\n ------- \n"
            "Formulate an improved question:"
        )

        """Rewrite the original user question."""
        messages = state["messages"]
        question = messages[0].content
        prompt = rewrite_prompt.format(question=question)
        response = ll_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [{"role": "user", "content": response.content}]}

    def generate_answer(state: MessagesState):
        GENERATE_PROMPT = (
            """You acting as a professional data analyst.
                   Based on the provided data set, perform in-depth analysis and evaluation.
                   Focus on making valuable comparisons, important statistics (such as min, max, average),
                   and potential relationships between elements in the data.
                   The goal is to help readers understand the big picture, detect trends, anomalies,
                   or actionable insights, and suggest appropriate visual charts to effectively present the information.

                   {context}

                   Question: {question}
                   """
        )
        """Generate an answer."""
        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = ll_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}

    workflow = StateGraph(MessagesState)

    workflow.add_node(generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([toolNode]))
    workflow.add_node(rewrite_question)
    workflow.add_node(generate_answer)

    workflow.add_edge(START, "generate_query_or_respond")

    workflow.add_conditional_edges(
        "generate_query_or_respond",
        # Assess LLM decision (call `retriever_tool` tool or respond to the user)
        tools_condition,
        {
            # Translate the condition outputs to nodes in our graph
            "tools": "retrieve",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "retrieve",
        # Assess agent decision
        grade_documents,
    )
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")
    graph = workflow.compile(name="rag_lang_graph")
    print("Init Graph success")
    return graph