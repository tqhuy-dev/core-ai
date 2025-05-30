from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import core
from agents.dto import BaseResponseAgentDto


class AgentsOpenAIWithTools:
    def __init__(self, model='openai:gpt-4o-mini', tools=None, thread_id = 'thread_default', prompt_templates=''):
        if tools is None:
            tools = []
        self.model = model
        self.tools = tools
        self.prompt_templates = prompt_templates
        self.memory = MemorySaver()
        self.agent = create_react_agent(init_chat_model(model) ,tools ,checkpointer=self.memory,prompt=prompt_templates)
        self.config:RunnableConfig = {"configurable": {"thread_id": thread_id}}

    def invoke(self , input_text: str) -> BaseResponseAgentDto:
        content = ''
        response:BaseResponseAgentDto = BaseResponseAgentDto(question=input_text,
                                                             role='user', response=content,
                                                             function_tools=[])
        response.function_tools = []
        for step in self.agent.stream({"messages": [HumanMessage(content=input_text)]},self.config,
                stream_mode="values",
        ):
            if isinstance(step["messages"][-1] , ToolMessage):
                tool_message_data = core.ToolMessageLangHandle(step["messages"][-1])
                tool_data = tool_message_data.get_function_tools()
                if len(response.function_tools) == 0:
                    response.function_tools.append(tool_data)
                else:
                    for index , value in enumerate(response.function_tools):
                        if response.function_tools[index].name == tool_data.function_name:
                            response.function_tools[index] = tool_data
                        else:
                            response.function_tools.append(tool_data)
            content = step["messages"][-1].content

        response.response = content
        print(response)
        return response
