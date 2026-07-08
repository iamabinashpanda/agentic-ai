import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from fastapi import FastAPI
from langserve import add_routes

load_dotenv("../.env")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API"),
    model=os.getenv("GROQ_MODEL"),
    verbose=True,
    max_retries=0,
)

system_prompt = "you are a joke assistance in hinglish who provides short jokes."
user_prompt = "provide a short joke on this {topic}"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", user_prompt)]
)

parser = StrOutputParser()

chain = prompt_template | llm | parser

app = FastAPI(
    description="simple demo app using langchain and langserve to generate jokes about a given topic",
    title="Joke Generator API",
    version="1.0",
)
@app.get("/")
def root():
    return {
        "message": "Welcome to the joke generator",
        "endpoints": {"joke_generator": "/joke-generator", "docs": "/docs"},
    }

add_routes(app, chain, path="/jokes-generator")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8085)
