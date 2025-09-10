from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv
from crewai.cli.constants import ENV_VARS
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
import time
from crewai.tasks.task_output import TaskOutput
import panel as pn

pn.extension("perspective")
chat_interface = pn.chat.ChatInterface(
    renderers=pn.pane.Perspective,
    show_rerun=False,
    show_undo=False,
    # show_clear=False,
    show_button_name=False,
)

checkbox = pn.widgets.Checkbox(name="Human-in-the-Loop mode")


def print_output(output: TaskOutput):
    message = output.raw
    chat_interface.send(message, user=output.agent, respond=False)


load_dotenv()

# # # Override the key name dynamically
for entry in ENV_VARS.get("ollama", []):
    if "API_BASE" in entry:
        entry["BASE_URL"] = entry.pop("API_BASE")  # Rename the key


# Tool instantiation


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


@CrewBase
class ProjectCrew:
    """Bench crew"""

    hitl_enabled = False

    # Configuration files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Manager Agent
    manager = Agent(
        role="Engineering Product Manager",
        goal="Efficiently manage the software engineering team and ensure high-quality task completion.",
        backstory="You're an experienced engineering project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
        # LLM="gpt-4"
    )

    # Agents
    @agent
    def design_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["design_agent"],
            verbose=True,
            # llm="gpt-4",
        )

    @agent
    def test_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["test_agent"],
            verbose=True,
            # llm="gpt-4",
        )

    @agent
    def coding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["coding_agent"],
            verbose=True,
            # llm="gpt-4",
        )

    # Tasks
    @task
    def requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config["requirements_task"],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def code_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_planning_task"],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def test_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_planning_task"],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config["coding_task"],
            context=[self.code_planning_task(), self.requirements_task()],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def test_run_task(self) -> Task:
        return Task(
            config=self.tasks_config["testing_task"],
            context=[self.coding_task(), self.test_planning_task()],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    # Crews
    @crew
    def crew(self) -> Crew:
        print(self.tasks)
        """Creates the Bench crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            manager_agent=self.manager,
            process=Process.hierarchical,
            verbose=True,
        )


@CrewBase
class HitlProjectCrew:
    """Bench crew"""

    hitl_enabled = True

    # Configuration files
    agents_config = "config/agents.yaml"
    tasks_config = "config/hitl_tasks.yaml"

    @after_kickoff
    def notify_end(self, result):
        chat_interface.send(
            f"The generation is complete, please choose another program to build",
            user="system",
            respond=False,
        )
        return

    # Manager Agent
    manager = Agent(
        role="Engineering Product Manager",
        goal="Efficiently manage the software engineering team and ensure high-quality task completion.",
        backstory="You're an experienced engineering project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
        # LLM="gpt-4"
    )

    # Agents
    @agent
    def design_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["design_agent"],
            verbose=True,
            # llm="gpt-4",
        )

    @agent
    def test_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["test_agent"],
            verbose=True,
            # llm="gpt-4",
        )

    @agent
    def coding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["coding_agent"],
            verbose=True,
            # llm="gpt-4",
        )

    # Tasks
    @task
    def requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config["requirements_task"],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def code_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_planning_task"],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def test_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_planning_task"],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config["coding_task"],
            context=[self.code_planning_task(), self.requirements_task()],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    @task
    def test_run_task(self) -> Task:
        return Task(
            config=self.tasks_config["testing_task"],
            context=[self.coding_task(), self.test_planning_task()],
            callback=print_output,
            human_input=self.hitl_enabled,
        )

    # Crews
    @crew
    def crew(self) -> Crew:
        print(self.tasks)
        """Creates the Bench crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            manager_agent=self.manager,
            process=Process.hierarchical,
            verbose=True,
        )
