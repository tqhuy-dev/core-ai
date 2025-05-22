from langchain_core.messages import  ToolMessage

class LangFunctionTool:
    def __init__(self, function_name: str, content: str):
        self.function_name = function_name
        self.content = content


class ToolMessageLangHandle:
    def __init__(self, message: ToolMessage):
        self.message = message

    def get_function_tools(self) -> LangFunctionTool:
        return LangFunctionTool(self.message.name, self.message.content)

