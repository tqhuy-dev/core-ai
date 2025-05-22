from core import LangFunctionTool


class BaseResponseAgentDto:
    def __init__(self, response: str,question: str, role: str, function_tools: LangFunctionTool | None):
        self.response = response
        self.role = role
        self.function_tools = function_tools
        self.question = question

    def to_dict(self):
        return {
            "response": self.response,
            "role": self.role,
            "function_tools": self.function_tools.__dict__ if self.function_tools else None,
            "question": self.question
        }