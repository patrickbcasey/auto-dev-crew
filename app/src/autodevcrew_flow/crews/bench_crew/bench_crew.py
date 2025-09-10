from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from dotenv import load_dotenv
from os import getenv
from crewai.cli.constants import ENV_VARS


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# from crewai.cli.constants import ENV_VARS
load_dotenv()

# # # Override the key name dynamically
# for entry in ENV_VARS.get("ollama", []):
#     if "API_BASE" in entry:
#         entry["BASE_URL"] = entry.pop("API_BASE")  # Rename the key


# llm = LLM(
#     model=getenv("MODEL_NAME"),  # call model by provider/model_name
#     temperature=0.8,
#     max_tokens=150,
#     top_p=0.9,
#     frequency_penalty=0.1,
#     presence_penalty=0.1,
#     stop=["END"],
#     seed=42,
# )

# Tool instantiation


@CrewBase
class BenchCrew:
    """Bench crew"""

    # Configuration files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Manager Agent
    manager = Agent(
        role="Engineering Product Manager",
        goal="Efficiently manage the software engineering team and ensure high-quality task completion.",
        backstory="You're an experienced engineering project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
        LLM="gpt-4o",
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
            output_file="output/requirements.md",
        )

    @task
    def code_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_planning_task"],
            output_file="output/code_plan.md",
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config["coding_task"], output_file="output/patch.md"
        )

    @task
    def test_write_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_write_task"],
            output_file="output/bug_reproduce.py",
        )

    # @task
    # def patch_correctness_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["patch_correctness_task"],
    #         # context=
    #     )

    # @task
    # def pull_review_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["pull_review_task"],
    #     )

    # Crews
    @crew
    def crew(self) -> Crew:
        """Creates the Bench crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            manager_agent=self.manager,
            # manager_llm="gpt-4o",
            process=Process.hierarchical,
            verbose=True,
        )
