import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import Settings,VectorStoreIndex,SimpleDirectoryReader,StorageContext,load_index_from_storage
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.agent.workflow import AgentStream
import asyncio

load_dotenv("../.env")

lyft_store_db_file_path = "./store/lyft"
uber_store_db_file_path = "./store/uber"

lyft_file_path = Path("./lyft_2021.pdf")
uber_file_path = Path("./uber_2021.pdf")
lyft_store_db = Path(lyft_store_db_file_path)
uber_store_db = Path(uber_store_db_file_path)


def set_environment():
    Settings.llm = Groq(api_key=os.getenv("GROQ_API"), model=os.getenv("GROQ_MODEL"))
    Settings.embed_model = HuggingFaceEmbedding(model_name=os.getenv("HUGGINGFACEHUB_MODEL"))
    return


def get_or_create_index():
    if lyft_store_db.exists():
        storage_context = StorageContext.from_defaults(persist_dir=lyft_store_db)
        lyft_index = load_index_from_storage(storage_context)
    else:
        lyft_documents = SimpleDirectoryReader(input_files=[lyft_file_path]).load_data()
        lyft_index = VectorStoreIndex.from_documents(lyft_documents)
        lyft_index.storage_context.persist(persist_dir=lyft_store_db_file_path)

    if uber_store_db.exists():
        storage_context = StorageContext.from_defaults(persist_dir=uber_store_db)
        uber_index = load_index_from_storage(storage_context)
    else:
        uber_documents = SimpleDirectoryReader(input_files=[uber_file_path]).load_data()
        uber_index = VectorStoreIndex.from_documents(uber_documents)
        uber_index.storage_context.persist(persist_dir=uber_store_db_file_path)

    return lyft_index, uber_index


def create_agent():
    set_environment()
    lyft_index, uber_index = get_or_create_index()
    lyft_engine = lyft_index.as_query_engine(similarity_top_=3)
    uber_engine = uber_index.as_query_engine(similarity_top_=3)
    query_engine_tools = [
        QueryEngineTool.from_defaults(
            query_engine=lyft_engine,
            name="lyft_10k",
            description="Provides information from lyft financials for year 2021",
        ),
        QueryEngineTool.from_defaults(
            query_engine=uber_engine,
            name="iber_10k",
            description="Provides information from uber financials for year 2021",
        ),
    ]
    return ReActAgent(tools=query_engine_tools, llm=Settings.llm, verbose=True)

async def main():
    agent = create_agent()
    while True:
        user_query = input("Query: ").strip()        
        if not user_query: continue
        if user_query.lower() == "exit": break
        try:
            handler = agent.run(user_query)
            async for ev in handler.stream_events():
                if isinstance(ev, AgentStream):
                    print(ev.delta, end="", flush=True)
            response = await handler
            print(response)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    asyncio.run(main())

# what is the financial crisis in covid for lyft and uber