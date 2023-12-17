from models import RepoToolInput, Requirement, Action


from typing import Dict
import subprocess
import shutil
import os


class RepoTool:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir

    @staticmethod
    def run_command(command, cwd=None) -> (bool, str):
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, cwd=cwd
        )
        if result.returncode != 0:
            return False, result.stdout + "\n" + result.stderr

        return True, result.stdout.strip()

    def implement_changes(self, data: RepoToolInput):
        for change in data.changes:
            if change.patch:
                patch_file_path = os.path.join(self.repo_dir, "temp.patch")
                change.patch.to_patch_file(patch_file_path)
                RepoTool.run_command(f"git apply {patch_file_path}", self.repo_dir)
                RepoTool.run_command(f"git add {change.patch.file_name}", self.repo_dir)

            if change.file_action:
                file_path = os.path.join(self.repo_dir, change.file_action.file_name)
                match change.file_action.action:
                    case Action.CREATE:
                        with open(file_path, "w") as file:
                            if change.file_action.content:
                                file.write(change.file_action.content)
                        RepoTool.run_command(
                            f"git add {change.file_action.file_name}", self.repo_dir
                        )

                    case Action.DELETE:
                        os.remove(file_path)
                        RepoTool.run_command(
                            f"git rm {change.file_action.file_name}", self.repo_dir
                        )

            if change.directory_action:
                directory_path = os.path.join(
                    self.repo_dir, change.directory_action.directory_name
                )
                match change.directory_action.action:
                    case Action.CREATE:
                        os.makedirs(directory_path, exist_ok=True)
                        RepoTool.run_command(
                            f"git add {change.directory_action.directory_name}",
                            self.repo_dir,
                        )

                    case Action.DELETE:
                        if os.path.exists(directory_path):
                            shutil.rmtree(directory_path)

    def requirement_is_fulfilled(self, data: Requirement):
        current_dir = self.repo_dir  # Starting in the repo directory
        full_command = ""
        for command in data.verification_commands:
            if "mkdir" in command and "mkdir -p" not in command:
                command.replace("mkdir", "mkdir -p")

            if not full_command:
                full_command = command
            else:
                full_command += f" && {command}"

        # Combine directory change with the actual command if needed
        print(f"RUNNING FULL COMMAND: {full_command}")
        success, output = self.run_command(full_command, cwd=self.repo_dir)
        if not success:
            return False, output

        final_output = output.split("\n")[-1]

        # Check the output of the last command
        if not final_output == data.expected_output:
            return (
                False,
                f"Got unexpected output: {final_output}, expecting {data.expected_output}",
            )

        return True, "Requirement fulfilled"

    def fetch_blob_hashes(self) -> Dict[str, str]:
        blob_hashes = {}

        success, committed_output = RepoTool.run_command(
            "git ls-tree -r HEAD", cwd=self.repo_dir
        )
        if success:
            for line in committed_output.splitlines():
                _, _, blob_hash, file_path = line.split(maxsplit=3)
                blob_hashes[file_path] = blob_hash

        return blob_hashes
