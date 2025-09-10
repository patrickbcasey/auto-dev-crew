from pydantic import BaseModel
import json
import re


class SweTask(BaseModel):
    task_id: str
    problem_statement: str
    repo: str
    base_commit: str
    repo_version: str
    test_patch: str
    test_passing: str
    test_failing: str
    oracle_text: str | None

    def to_dict(self) -> dict:
        {
            "task_id": self.task_id,
            "problem_statement": self.problem_statement,
            "repo": self.repo,
            "base_commit": self.base_commit,
            "repo_version": self.repo_version,
            "test_patch": self.test_patch,
            "test_passing": self.test_passing,
            "test_failing": self.test_failing,
            "oracle_text": self.oracle_text,
        }


class SweTaskInfo:
    task_id: str
    task_info: dict

    def __init__(self, task_id: str, task_info: dict):
        self.task_id = task_id
        self.task_info = task_info
        self.problem_statement = task_info["problem_statement"]
        self.repo = task_info["repo"]
        self.base_commit = task_info["base_commit"]
        self.repo_version = task_info["version"]
        self.test_patch = task_info["test_patch"]
        self.test_passing = task_info["PASS_TO_PASS"]
        self.test_failing = task_info["FAIL_TO_PASS"]
        self.oracle_text = task_info["text"]

    def to_task(self) -> SweTask:
        task_id = self.task_id
        task_info = self.task_info
        return SweTask(
            task_id=task_id,
            problem_statement=task_info["problem_statement"],
            repo=task_info["repo"],
            base_commit=task_info["base_commit"],
            repo_version=task_info["version"],
            test_patch=task_info["test_patch"],
            test_passing=task_info["PASS_TO_PASS"],
            test_failing=task_info["FAIL_TO_PASS"],
            oracle_text=task_info["text"],
        )


class BenchParser:
    def __init__(self, instance_id: str, path_to_swe_bench_json: str):

        swe_info = self.parse_swe_bench_json(instance_id, path_to_swe_bench_json)

        self.instance_id = instance_id
        self.file_path = path_to_swe_bench_json
        self.problem_statement = swe_info["problem_statement"]
        self.bug_file_contents = swe_info["bug_file_contents"]
        self.full_text = swe_info["oracle_contents"]

    def parse_swe_bench_json(self, instance_id, file_path) -> dict[str, str]:
        swe_info = {}
        with open(file_path, "r") as file:
            data = json.load(file)
            data_ptr = data[instance_id]
            swe_info["problem_statement"] = data_ptr["problem_statement"]
            swe_info["repo"] = data_ptr["repo"]
            swe_info["oracle_contents"] = data_ptr["text"]
            swe_info["bug_file_contents"] = self.parse_code_from_oracle(
                swe_info["oracle_contents"]
            )

        return swe_info

    def parse_code_from_oracle(self, oracle_text: str) -> str:

        start_pattern = r"<code>"
        end_pattern = r"</code"

        code_pattern = re.compile(f"{start_pattern}(.*?){end_pattern}", re.DOTALL)
        code = "\n".join(code_pattern.findall(oracle_text))
        return code
