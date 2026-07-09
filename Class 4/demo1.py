import gradio as gr
import uuid
import os
from typing import Optional, TypedDict, Dict
from langgraph.graph import StateGraph
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
import string

load_dotenv("../.env")

#llm = ChatGroq(api_key=os.getenv("GROQ_API"), model=os.getenv("GROQ_MODEL"))
llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API"), model=os.getenv("GOOGLE_MODEL"))


class ProfileExtractor(BaseModel):
    user_profile: dict = Field(
        default="",
        description="The updated user profile JSON containing accumulated data."
    )
    missing_info_question: Optional[str] = Field(
        default="None",
        description="If any info (age, income, goal, risk) is missing, provide a friendly question to ask the user. If all info is present, leave this empty Done string.",
    )


class FinanceState(TypedDict):
    user_input: str
    intent: Optional[str]
    user_profile: Optional[Dict[str, any]]
    hitl_flag: Optional[bool]
    data: Optional[Dict]


def human_in_the_loop(state: FinanceState) -> Dict:
    return {
        "data": {
            "response": f"The query '{state['user_input']}' has been flagged as high-risk. Please wait for expert input before proceeding."
        }
    }


def fallback(state: FinanceState):
    return {"data": {"response": "🤔 Try asking about stocks or budgets."}}


def budget_summary(state: FinanceState) -> Dict:
    user_profile = state.get("user_profile", {})
    print(user_profile)
    prompt = ChatPromptTemplate.from_template(
        "Mock a budget summary for this profile: {user_profile}. Be empathetic. and output in 50 to 80 words total."
    )
    chain = RunnablePassthrough() | prompt | llm | StrOutputParser()
    response = chain.invoke(input={"user_profile": user_profile})
    return {"data": {"response": response}}


def collect_user_data(state: FinanceState)->Dict:
    user_input = state["user_input"]
    user_profile = dict(state.get("user_profile", {}))

    prompt = ChatPromptTemplate([

        ("system", (
            "Extract user profile from the user input and merge/update it cleanly the current profile. as key value pair under user_profile section.\n"
            "Current profile: {user_profile}\n"
            "If info is missing, ask an empathetic question to get the rest. If everything is gathered, leave missing_info_question as Done asking questions."
        )),
        ("user", "{user_input}")
    ])
    chain = (RunnablePassthrough() | prompt | llm.with_structured_output(ProfileExtractor))
    response = chain.invoke(input={"user_input": user_input, "user_profile": user_profile})
    print(response)
    if response.missing_info_question:
        return {
            "user_profile": response.user_profile,
            "data": {"response": response.missing_info_question},
        }

def intent_detection(state: FinanceState) -> Dict:
    user_input = state["user_input"]
    prompt = ChatPromptTemplate(
        [
            (
                "system",
                "Classify the user's intent into one of: ['profile', 'stock', 'budget', 'unknown'] only. in one word.",
            ),
            ("user", "User input: {user_input}."),
        ]
    )
    chain = RunnablePassthrough() | prompt | llm | StrOutputParser()
    result = chain.invoke(input={"user_input": user_input})

    high_risk_keywords = [
        "liquidate",
        "retirement",
        "all my savings",
        "entire portfolio",
    ]
    hitl_flag = any(keyword in user_input.lower() for keyword in high_risk_keywords)
    return {"intent": result, "hitl_flag": hitl_flag}

def get_node(state: FinanceState) -> str:
    if state.get("hitl_flag"):
        return "hitl"
    valid = ["profile","stock", "budget"]
    return state["intent"] if state["intent"] in valid else "fallback"


workflow = StateGraph(FinanceState)

workflow.add_node("INTENT_DETECTION", intent_detection)
workflow.add_node("COLLECT_USER_DATA", collect_user_data)
workflow.add_node("HUMAN_IN_THE_LOOP", human_in_the_loop)
workflow.add_node("FALLBACK", fallback)
workflow.add_node("BUDGET", budget_summary)

workflow.set_entry_point("INTENT_DETECTION")
workflow.add_conditional_edges(
    source="INTENT_DETECTION",
    path=get_node,
    path_map={
        "profile": "COLLECT_USER_DATA",
        "budget": "BUDGET",
        "hitl": "HUMAN_IN_THE_LOOP",
        "fallback": "FALLBACK",
    },
)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

graphBytes = app.get_graph().draw_mermaid_png()
with open('./designPractice.png','wb') as file:
    file.write(graphBytes)


def chat_with_graph(msg: str, history: list, thread_id: str):
    result = app.invoke(
        input={"user_input": msg}, config={"configurable": {"thread_id": thread_id}}
    )
    return result["data"]["response"]


session_id = gr.State(value=str(uuid.uuid4()))
gr.ChatInterface(
    fn=chat_with_graph,
    chatbot=gr.Chatbot(height=600),
    additional_inputs=[session_id],
    title="Financial Advisor",
    description="App developed using LangGraph Persistence(Memorysaver)",
).launch(share=True,debug=True)
