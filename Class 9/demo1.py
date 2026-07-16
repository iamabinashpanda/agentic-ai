import os, uuid
import streamlit as st
from datetime import datetime
import traceback
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langsmith import Client, traceable

load_dotenv("../.env")

if not os.getenv("GROQ_API"):
    st.error("Please set your Groq API Key in a .env file")
    st.stop()
if not os.getenv("LANGCHAIN_API"):
    st.error("Please set your Langchain API Key in a .env file")
    st.stop()

LANGCHAIN_PROJECT = "Resume-Screening"

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API")
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

langsmith_client = Client()


@traceable(name="extract_resume_text")
def extract_text_from_resume(file):
    temp_file_path = f"temp_{file.name}"
    try:
        with open(temp_file_path, "wb") as f:
            f.write(file.getbuffer())
        documents = PyPDFLoader(temp_file_path).load()
        text = " ".join([doc.page_content for doc in documents])
        return text
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@traceable(name="analyze_resume_with_langsmith")
def analyze_resume_with_langsmith(job_requirements, resume_text):
    llm = ChatGroq(api_key=os.getenv("GROQ_API"), model=os.getenv("GROQ_MODEL"))
    prompt_text = f"""
        You are an expert HR and recruitment specialist. Analyze the resume below against the job requirements.

    Job Requirements:
    {job_requirements}

    Resume:
    {resume_text}

    Provide a comprehensive structured analysis covering:
    1. **Skills Match**: How well candidate's skills align with requirements
    2. **Experience Relevance**: Relevant work experience analysis  
    3. **Education & Certifications**: Educational background assessment
    4. **Strengths**: Key strengths of the candidate
    5. **Areas for Improvement**: What's missing or could be better
    6. **Overall Assessment**: Summary recommendation

    At the end, clearly state a "Suitability Score" as a percentage (0-100%) based on how well the resume aligns with the job.
    Format: Suitability Score: XX%
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()
    analysis = chain.invoke({})
    return analysis

def main():
    st.set_page_config(
        page_title="Resume Screening with Langsmith",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("AI Resume Screening with Langsmith Observability")
    st.markdown(
        f"**[View Live Traces in Langsmith Dashboard →] (https://api.smith.langchain.com/projects/{LANGCHAIN_PROJECT})**"
    )
    with st.sidebar:

        st.header("Langsmith Observability")
        st.info(f"**PROJECT** : {LANGCHAIN_PROJECT}")

        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())[:8]

        st.metric("Session ID", st.session_state.session_id)
        st.metric("Timestamp", datetime.now().strftime("%H:%M"))

        if "analysis_count" not in st.session_state:
            st.session_state.analysis_count = 0

        st.metric("Analysis Completed", st.session_state.analysis_count)

    col1, col2 = st.columns(2)

    with col1:
        st.header("Job Requirements")
        job_requirements = st.text_area(
            "Enter the job requirements and qualifications",
            height=300,
            placeholder="e.g., Required: Python, Machine Learning, 3+ years experience",
        )

    with col2:
        st.header("Upload Resume")
        uploaded_file = st.file_uploader("Upload candidate's resume",type=["pdf"],help="Support formats: PDF")
    
    if st.button("Analyze Resume",type="primary") and job_requirements and uploaded_file:
        with st.spinner("Processing with LangSmith Tracing..."):
            try:
                resume_text = extract_text_from_resume(uploaded_file)
                with st.expander("View Extracted Resume Text"):
                    st.text_area("Resume COntent",resume_text,height=400)
                analysis = analyze_resume_with_langsmith(job_requirements,resume_text)
                st.header("AI Analysis Results")
                st.markdown(analysis)
                
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="Download Analysis",
                        data=analysis,
                        file_name=f"analysis_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

                with col2:
                    with col2:
                        st.markdown(f"**[🔍 View Detailed Traces →](https://smith.langchain.com/projects/{LANGCHAIN_PROJECT})**")
                    st.session_state.analysis_count += 1
                    st.info("Analysis complete! Check LangSmith dashboard for detailed observability traces.")

            except Exception as e:
                 st.error(f"**Error occurred**: {str(e)}")
                 with st.expander("Debug Information"):
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
