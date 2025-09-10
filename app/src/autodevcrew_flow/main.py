import os
from dotenv import load_dotenv
import panel as pn
import threading
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
import time
from autodevcrew_flow.crews.project_crew.project_crew import (
    ProjectCrew,
    HitlProjectCrew,
    chat_interface,
    checkbox,
)
from autodevcrew_flow.main_bench import kickoff

load_dotenv()

pn.extension(design="material", sizing_mode="stretch_width")


def custom_ask_human_input(self, final_answer: dict) -> str:
    global user_input
    chat_interface.send(final_answer, user="Assistant", respond=False)

    prompt = "Provide feedback on the agent's outputs "
    chat_interface.send(prompt, user="System", respond=False)

    while user_input == None:
        time.sleep(1)

    human_agent_input = user_input
    user_input = None

    return human_agent_input


CrewAgentExecutorMixin._ask_human_input = custom_ask_human_input

user_input = None
crew_started = False


def initiate_chat(message):
    global crew_started
    crew_started = True

    try:
        inputs = {"project": message}
        if checkbox.value:
            crew = HitlProjectCrew().crew()
        else:
            crew = ProjectCrew().crew()
        result = crew.kickoff(inputs=inputs)

    except Exception as e:
        chat_interface.send(f"An error occurred: {e}", user="Assistant", respond=False)
    crew_started = False


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global crew_started
    global user_input

    if not crew_started:
        thread = threading.Thread(target=initiate_chat, args=(contents,))
        thread.start()
    else:
        user_input = contents


chat_interface.callback = callback

chat_interface.send(
    "Hello, I'm the Manager of AutoDevCrew. What project would you like us to work on today?",
    user="Assistant",
    respond=False,
)

# chat_interface.servable()

pn.template.MaterialTemplate(
    site="AutoDevCrew",
    title="Interactive Chat",
    main=[chat_interface, checkbox],
).servable()