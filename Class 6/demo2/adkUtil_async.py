from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService,Session
from google.adk.runners import Runner
from google.genai.types import Content,Part

async def run_agent_query(agent:Agent,session_service:InMemorySessionService,session:Session,query:str,user_id:str):
    runner = Runner(app_name=agent.name,agent=agent,session_service=session_service)
    content = Content(role="user",parts=[Part(text=query)])
    event_stream = runner.run_async(user_id=user_id,new_message=content,session_id=session.id)
    final_text_chunks=list()
    try:
        async for events in event_stream:
            if events.content and events.content.parts:
                for part in events.content.parts:
                    if hasattr(part, 'thought') and part.thought:
                        print(f"[Thought]: {part.text}")
                    elif hasattr(part, 'function_call') and part.function_call:
                        print(f"[Action]: {part.function_call.name}({part.function_call.args})")
                    elif hasattr(part,'function_response') and part.function_response:
                        print(f"[Observation - {part.function_response.name}]: {part.function_response.response}")
                    elif part.text:
                        final_text_chunks.append(part.text)
        final_response_text = "".join(final_text_chunks).strip()
        if not final_response_text:
            history = await session_service.get_session_history(session_id=session.id)
            if history and len(history) > 0:
                final_response_text = history[-1].text 

        print(f"🎉 FINAL RESPONSE:\n{final_response_text}")
        return final_response_text


    except Exception as e:
        final_response = f"An error occurred: {e}"
    return final_response

