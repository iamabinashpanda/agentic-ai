from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types
import requests, asyncio
from google.adk.sessions import InMemorySessionService
from adkUtil_async import run_agent_query
from dotenv import load_dotenv

load_dotenv("./.env")


def get_weather(city: str) -> str:
    """
    retrive the current weather from the city
    """
    try:
        header = {
            "accept": 'application/json; charset=utf-8; profile="https://mediawiki.org"',
            "User-Agent": "MyCityApp/1.0 (contact@example.com)",
        }
        link = f"https://wttr.in/{city}?format=j1"
        response = requests.get(link, headers=header)
        response.raise_for_status()
        data = response.json()
        curr = data["current_condition"]
        temp = curr["temp_C"]
        desc = curr["weatherDesc"][0]["value"]
        return f"the current weather in {city} is {desc} with a temperature of {temp}℃."
    except Exception as e:
        return f"we could not fetch weather for {city} : Error - {str(e)}"


def get_city_info(city) -> str:
    """
    retrieves the real time information of city from wikipedia.
    """
    try:
        header = {
            "accept": 'application/json; charset=utf-8; profile="https://mediawiki.org"',
            "User-Agent": "MyCityApp/1.0 (contact@example.com)",
        }
        link = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}"
        response = requests.get(url=link, headers=header)
        data = response.json()
        response.raise_for_status()
        return f"facts about {city} : {data.get('extract','No summary available')}"
    except Exception as e:
        return f"we could not fetch {city} information. Error - {str(e)}"


concierge_agent = Agent(
    name="conceirge_agent",
    model="gemini-3.5-flash",
    description="provides current weather and information about the city",
    instruction="""
            you are a helpful live travel assistance.
            your goal is to provide accurate, real time information to traveller.
            whenever user mention a city your job is to use the tools and find the interesting facts and current weather of that location and
            help them if they should visit that location or not. summarize your finding in a friendly, conversational tone.
        """,
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(thinking_budget=124, include_thoughts=True)
    ),
    tools=[get_city_info,get_weather]
)

async def run_concierge(agent:Agent, query:str,id:str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=agent.name,user_id=id)
    await run_agent_query(agent,session_service,session,query,id)


if __name__=="__main__":
    user_id="iamabinashpanda"
    user_query = "i am planning to visit bangalore and mysore in one day. help me decide which day would be best to visit as per city and weather."
    print(f"Query: '{user_query}'")
    asyncio.run(run_concierge(agent=concierge_agent,query=user_query,id=user_id))