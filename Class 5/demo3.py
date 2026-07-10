import cohere, os
from dotenv import load_dotenv
import gradio as gr

load_dotenv("../.env")
co = cohere.ClientV2(api_key=os.getenv("COHERE_API"))


def market_research_agent(query):
    response = co.chat(messages=[{"role": "user", "content": query}], model="command-a-plus-05-2026")
    return response.message.content[1].text


with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown("# Market Research Agent")
        gr.Markdown("This agent uses Cohere's built-in web connector for real-time market research.")
        input_box = gr.Textbox(label="Enter Your Market Research Query")
        output_box = gr.Markdown(label="Agent Response")
    btn = gr.Button("Submit")
    btn.click(fn=market_research_agent, inputs=input_box, outputs=output_box)
demo.launch(share=True)