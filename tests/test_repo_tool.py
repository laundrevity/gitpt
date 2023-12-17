from models import (
    RepoToolInput,
    Patch,
    RepoChange,
    FileAction,
    Action,
    DirectoryAction,
)
from repo_tool import RepoTool
import os
import tempfile


def test_repo_tool_with_patch():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup: Initialize git repo and create a file
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.write("original line\n")
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the RepoToolInput for a Patch
        patch = Patch(
            file_name=file_name,
            blob_hash=blob_hash,
            diff_range="-1 +1",
            changes=["-original line", "+modified line"],
        )
        repo_tool_input = RepoToolInput(changes=[RepoChange(patch=patch)])

        # Apply the change
        repo_tool = RepoTool(tmpdir)
        repo_tool.implement_changes(repo_tool_input)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "modified line"


def test_repo_tool_with_file_action():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup: Initialize git repo
        RepoTool.run_command("git init", tmpdir)
        file_name = "new_file.txt"
        file_path = os.path.join(tmpdir, file_name)

        # Prepare the RepoToolInput for FileAction (Create)
        file_action_create = FileAction(
            action=Action.CREATE, file_name=file_name, content="Hello World"
        )
        repo_tool_input_create = RepoToolInput(
            changes=[RepoChange(file_action=file_action_create)]
        )

        # Apply the create action
        repo_tool = RepoTool(tmpdir)
        repo_tool.implement_changes(repo_tool_input_create)

        # Verify the file was created with correct content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "Hello World"

        # Prepare the RepoToolInput for FileAction (Delete)
        file_action_delete = FileAction(action=Action.DELETE, file_name=file_name)
        repo_tool_input_delete = RepoToolInput(
            changes=[RepoChange(file_action=file_action_delete)]
        )

        # Apply the delete action
        repo_tool.implement_changes(repo_tool_input_delete)

        # Verify the file was deleted
        assert not os.path.exists(file_path)


def test_repo_tool_with_directory_action():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup: Initialize git repo
        RepoTool.run_command("git init", tmpdir)
        dir_name = "new_dir"
        dir_path = os.path.join(tmpdir, dir_name)

        # Prepare the RepoToolInput for DirectoryAction (Create)
        dir_action_create = DirectoryAction(
            action=Action.CREATE, directory_name=dir_name
        )
        repo_tool_input_create = RepoToolInput(
            changes=[RepoChange(directory_action=dir_action_create)]
        )

        # Apply the create action
        repo_tool = RepoTool(tmpdir)
        repo_tool.implement_changes(repo_tool_input_create)

        # Verify the directory was created
        assert os.path.isdir(dir_path)

        # Prepare the RepoToolInput for DirectoryAction (Delete)
        dir_action_delete = DirectoryAction(
            action=Action.DELETE, directory_name=dir_name
        )
        repo_tool_input_delete = RepoToolInput(
            changes=[RepoChange(directory_action=dir_action_delete)]
        )

        # Apply the delete action
        repo_tool.implement_changes(repo_tool_input_delete)

        # Verify the directory was deleted
        assert not os.path.exists(dir_path)
