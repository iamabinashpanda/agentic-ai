# for the MCP github agent to work, ensure that Nodejs is installed. npx is used to connect using MCP
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv

load_dotenv("./.env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

github_assistant = LlmAgent(
    model='gemini-3.5-flash',
    name='github_expert',
    instruction='You are an assistant that helps manage GitHub repositories. Let the user use only tools provided by GitHub that will list down the repositories names only.',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-github@latest"
                    ],
                    env={
                        "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN
                    }
                )
            )
        )
    ]
)

root_agent = github_assistant