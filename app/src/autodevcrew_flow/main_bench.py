from pathlib import Path
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from autodevcrew_flow.crews.bench_crew.bench_crew import BenchCrew
from utils import get_swe_task_list
from autodevcrew_flow.prompt_utils import SwePrompts
from autodevcrew_flow.model_parser import OutputParser, Edit
from autodevcrew_flow.tasks import SweTask, BenchParser


# Constants
TASK_INFO_FILE = f"{str(Path.cwd().parent)}/bench_files/SWE-bench.json"
TASK_LIST_FILE = f"{str(Path.cwd().parent)}/bench_files/tasks.txt"
OUTPUT_FILE = f"{str(Path.cwd())}/output/patch.md"
DIFF_FILE = f"{str(Path.cwd())}/output/"


# Define our flow state
class BenchState(BaseModel):
    run_mode: str = ""
    task_list: list[SweTask] = []


class BenchFlow(Flow[BenchState]):
    """Flow for running SWE-bench-lite"""

    @start()
    def get_run_mode(self):
        self.state.run_mode = "swe-bench"
        self.state.task_list = get_swe_task_list(TASK_LIST_FILE, TASK_INFO_FILE)
        return

    @listen(get_run_mode)
    def run_mode(self, state):
        if self.state.run_mode == "swe-bench":
            """Create a structured outline for the guide using a direct LLM call"""
            for task in self.state.task_list:
                task_info = BenchParser(task.task_id, TASK_INFO_FILE)
                prompts = SwePrompts()
                result = (
                    BenchCrew()
                    .crew()
                    .kickoff(
                        inputs={
                            "task": task.oracle_text,
                            "bug_file_contents": task_info.bug_file_contents,
                            "problem_statement": task.problem_statement,
                            "code": task_info.bug_file_contents,
                            "stacktrace_helper": prompts.stacktrace_function,
                        }
                    )
                )
                parsed_output = OutputParser(OUTPUT_FILE)

                edits = parsed_output.get_edits()
                parsed_output.file_to_change
                parsed_output.get_diff()

                # there could be no edit
                if edits is not None:
                    print(parsed_output.apply_edit(edits, "test/L031.py"))
        else:
            raise ValueError("Run mode must be either project or swe-bench")


def kickoff():
    """Run the guide creator flow"""
    BenchFlow().kickoff()
    print("\n=== Flow Complete ===")
    print("Your comprehensive guide is ready in the output directory.")
    print("Open output/complete_guide.md to view it.")
    return "pog"


def plot():
    """Generate a visualization of the flow"""
    flow = BenchFlow()
    flow.plot("guide_creator_flow")
    print("Flow visualization saved to guide_creator_flow.html")


if __name__ == "__main__":
    kickoff()
