from enum import Enum


class Action(str, Enum):
    ASK_QUESTION = "ask_question"
    SUMMARIZE = "summarize"
    GENERATE_IDEA = "generate_idea"
    FOLLOWUP = "followup"
