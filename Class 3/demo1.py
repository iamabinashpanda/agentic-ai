import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader

load_dotenv("../.env")

llm = ChatGroq(api_key=os.getenv("GROQ_API"),model=os.getenv("GROQ_MODEL"))

def extract_text_from_resume(file):
    loader = PyPDFLoader(file)
    document = loader.load()
    return " ".join([doc.page_content for doc in document ])

def suitability_score(text):
        import re
        match = re.search("Suitability Score: (\d{1,3})%",text)
        if match:
              return int(match.group(1))
        return None 

job_requirements = input("Enter Job Requirements: ")

file_path = "D:\\repositories\\Agentic ai\\class 3\\Abinash Panda Resume.pdf"

resume_text = extract_text_from_resume(file_path)

prompt = ChatPromptTemplate.from_template(
    """
        You are an expert in HR and specialist now analyse the resume and job text mentioned below and 
        find out the possibilities of matches the candidate is able to perform for the particular rule or 
        I could say for the particular shop inputs.
        job requirements : {job_requirements}
        resume: {resume_text}
        Provide a detailed report of the resume as per the job requirement also and at the end,
        Based on the matching of the resume provided give the suitability score from 0 to 100 in Format : Suitability Score: XX%
    """
)
chain = RunnablePassthrough() | prompt | llm | StrOutputParser()

retrieval = chain.invoke(input={"job_requirements":job_requirements,"resume_text":resume_text},config={"recursion_limit":5})

with open("output.md","w",encoding="utf-8") as file:
    file.write(retrieval)

print(suitability_score(retrieval))