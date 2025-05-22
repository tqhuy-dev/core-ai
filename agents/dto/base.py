from core import LangFunctionTool


class BaseResponseAgentDto:
    def __init__(self, response: str,question: str, role: str, function_tools: list[LangFunctionTool]):
        self.response = response
        self.role = role
        self.function_tools = function_tools
        self.question = question

    def to_dict(self):
        return {
            "response": self.response,
            "role": self.role,
            "function_tools": [{"name": t.function_name , "content": t.content} for t in self.function_tools] if self.function_tools else [],
            "question": self.question
        }