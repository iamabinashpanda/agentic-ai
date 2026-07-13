from google.adk.agents.llm_agent import Agent
import requests


def get_weather(city:str)->str:
    """
    retrive the current weather from the city
    """
    try:
        header = {'accept': 'application/json; charset=utf-8; profile="https://mediawiki.org"','User-Agent': 'MyCityApp/1.0 (contact@example.com)'}
        link = f"https://wttr.in/{city}?format=j1"
        response = requests.get(link,headers=header)
        response.raise_for_status()
        data =response.json()
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
        header = {'accept': 'application/json; charset=utf-8; profile="https://mediawiki.org"','User-Agent': 'MyCityApp/1.0 (contact@example.com)'}
        link = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city}"
        response = requests.get(url=link, headers=header)
        data = response.json()
        response.raise_for_status()
        return f"facts about {city} : {data.get('extract','No summary available')}"
    except Exception as e:
        return f"we could not fetch {city} information. Error - {str(e)}"


root_agent = Agent(
    model="gemini-3.5-flash",
    name="root_agent",
    description="A helpful assistant for user questions.",
    instruction="""
        you are a helpful live travel assistance.
        your goal is to provide accurate, real time information to traveller.
        whenever user mention a city your job is to use the tools and find the interesting facts and current weather of that location and
        help them if they should visit that location or not. summarize your finding in a friendly, conversational tone.
        """,
    tools=[get_city_info, get_weather],
)
