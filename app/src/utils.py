import os
import shutil
import json
import subprocess
import contextlib
from subprocess import CalledProcessError
from os.path import join
from pathlib import Path
from autodevcrew_flow.tasks import SweTask, SweTaskInfo


@contextlib.contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def run_sh_command(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    try:
        cp = subprocess.run(cmd, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        raise e
    return cp


def create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def clone_repo(clone_link: str, dest_dir: str, cloned_name: str):
    clone_cmd = ["git", "clone", clone_link, cloned_name]
    create_dir(dest_dir)
    with cd(dest_dir):
        run_sh_command(clone_cmd)
    cloned_dir = join(dest_dir, cloned_name)
    return cloned_dir


def get_latest_commit_hash():
    command = ["git", "rev-parse", "HEAD"]
    cp = subprocess.run(command, text=True, capture_output=True)
    try:
        cp.check_returncode()
        return cp.stdout.strip()
    except CalledProcessError as e:
        raise RuntimeError(f"Failed to commit hash: {cp.stderr}") from e


def swe_file_parser(filepath: str):
    with open(filepath) as f:
        task_id = f.readlines()
    return [x.strip() for x in task_id]


def get_swe_task_list(task_file: str | None, task_info_file: str) -> list[SweTask]:
    task_info_map = []

    with open(task_info_file) as f:
        task_info_map = json.load(f)

    task_list = []

    if task_file is not None:
        task_list = swe_file_parser(task_file)
    elif len(task_list) == 0:
        raise ValueError("Task list cannot be empty")

    task_with_info = []
    for task in task_list:
        task_info = task_info_map[task]
        swe_task = SweTaskInfo(
            task,
            task_info,
        )

        task_with_info.append(swe_task.to_task())

        # task_with_info.append((task, task_info))

    return task_with_info


def dir_cleanup(target_dir: str):
    if os.path.exists(target_dir) and "/clones/" in target_dir:
        try:
            shutil.rmtree(target_dir)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
