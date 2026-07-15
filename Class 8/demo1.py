from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
import os, sys, subprocess
import streamlit as st
from io import BytesIO
from fpdf import FPDF

load_dotenv("../.env")

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "coding", "use_docker": False},
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
)

assistant = AssistantAgent(
    name="assistant",
    system_message="you are a helpful assistant",
    llm_config=[
        {
            "model": os.getenv("GROQ_MODEL"),
            "api_key": os.getenv("GROQ_API"),
            "api_type": "groq",
        }
    ],
    max_consecutive_auto_reply=3,
)


def custom_receive(self, message, sender, request_reply, silent):
    content = message.get("content", "") if isinstance(message, dict) else message
    st.session_state.assistant_messages.append(content)


user_proxy.receive = custom_receive.__get__(user_proxy)

st.set_page_config(page_title="Autogen Research Agent", layout="wide")
st.title("Research Agent")

if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = []

topic = st.text_input("Enter your question or topic:")

if st.button("Ask"):
    if not topic.strip():
        st.warning("Please enter a question or topic.")
    else:
        st.session_state.assistant_messages = []
        user_proxy.initiate_chat(message=topic, recipient=assistant)

if st.button("Generate Subtopics"):
    if not st.session_state.assistant_messages:
        st.warning("Please ask a question first.")
    else:
        last_response = st.session_state.assistant_messages[-1]
        print(last_response)
        subtopic_prompt = (
            "Please generate a list of subtopics or themes based on the following text.\n\n"
            f"{last_response}\n\n"
            "List them in bullet points."
        )
        st.session_state.assistant_messages = []
        user_proxy.initiate_chat(assistant, message=subtopic_prompt)

if st.button("Summarise"):
    if not st.session_state.assistant_messages:
        st.warning("Please ask a question first.")
    else:
        last_response = st.session_state.assistant_messages[-1]
        summarise_prompt = (
            f"Please summarise the following text concisely:\n\n{last_response}"
        )
        st.session_state.assistant_messages = []
        user_proxy.initiate_chat(assistant, message=summarise_prompt)

if st.session_state.assistant_messages:
    st.markdown("### Assistant Response:")
    for msg in st.session_state.assistant_messages:
        st.markdown(msg)

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=12)

for msg in st.session_state.assistant_messages:
    pdf.multi_cell(0, 10, txt=msg)

pdf_bytes = pdf.output(dest="S").encode("latin-1")
pdf_io = BytesIO(pdf_bytes)

st.download_button(
    label="Download PDF",
    data=pdf_io,
    file_name="assistant_response.pdf",
    mime="application/pdf",
)

if __name__ == "__main__":
    if not st.runtime.exists():
        subprocess.run(["streamlit", "run", sys.argv[0]])