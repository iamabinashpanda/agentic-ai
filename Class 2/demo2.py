import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv("../.env")
llm = ChatGroq(api_key=os.getenv("GROQ_API"),model=os.getenv("GROQ_MODEL"))

search_tools = DuckDuckGoSearchRun()
def search(input):
    results = search_tools.run(input["input"])
    return {"search_results": results, "topic": input}

prompt = ChatPromptTemplate.from_template(
    """
        you are a helpful research writer.
        Based on these search results: {search_results}, write a comprehensive, Professional, nicely formatted report about {topic}.
        use clear headings, bullet points and an executive summary.
    """
)

writer_agent = prompt | llm
parser = StrOutputParser()
chain = RunnablePassthrough() | search | writer_agent | parser
user_query = "Impact of Agentic AI using LLM & Prompt Engineering over Duckcreek ecosystem "
report = chain.invoke(input={"input":user_query},config={"recursion_limit":5})

with open("output_demo3.md","w",encoding="utf-8") as file:
    file.write(report)