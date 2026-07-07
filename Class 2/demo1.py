from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.messages import HumanMessage

load_dotenv("../.env")
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]
llm = ChatGroq(
    api_key=os.getenv("GROQ_API"), model=os.getenv("GROQ_MODEL"), max_tokens=500
)
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="you are helpful assistance and use duck duck go search tool to fetch the result and write the result in bullet points.",
)
result = agent.invoke(
    {"messages": [HumanMessage(content="how to learn LLM for free ?")]},
    config={"recursion_limit": 10},
)
with open("output.md", "w", encoding="utf-8") as file:
    file.write(result["messages"][-1].content)
