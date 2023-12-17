from repo_tool import RepoTool
from models import Patch

import tempfile
import os


def test_patch_add_line():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create an empty file
        RepoTool.run_command("git init", cwd=tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        RepoTool.run_command(f"touch {file_name}", cwd=tmpdir)

        # Commit the empty file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", cwd=tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", cwd=tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", cwd=tmpdir)

        # Prepare the JSON input (conforming to Patch schema) for adding a line
        patch_data = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-0,0 +1",
            "changes": ["+first line added"],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(patch_data)
        patch_file = os.path.join(tmpdir, "add_line.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", cwd=tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "first line added"


def test_patch_remove_line():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create a file with initial content
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.write("line 1\nline 2 to remove\nline 3\n")

        # Commit the file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the JSON input for removing a line
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-1,3 +1,2",
            "changes": [" line 1", "-line 2 to remove", " line 3"],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "remove_line.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "line 1\nline 3"


def test_patch_modify_line():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create an empty file
        print(RepoTool.run_command("git init", tmpdir))
        print(RepoTool.run_command("pwd", tmpdir))
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.write("original line\n")

        # Commit the file to get its blob hash
        print(RepoTool.run_command(f"git add {file_name}", tmpdir))
        print(RepoTool.run_command("git commit -m 'initial commit'", tmpdir))
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)
        print(blob_hash)
        print(RepoTool.run_command("find .git/objects -type f", tmpdir))

        # Prepare the JSON input for modifying a line
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-1 +1",
            "changes": ["-original line", "+modified line"],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "modify_line.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "modified line"


def test_patch_add_multiple_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create an empty file
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        RepoTool.run_command(f"touch {file_name}", tmpdir)

        # Commit the empty file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the JSON input for adding multiple lines
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-0,0 +1,3",
            "changes": ["+first line", "+second line", "+third line"],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "add_multiple_lines.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "first line\nsecond line\nthird line"


def test_patch_remove_multiple_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create a file with initial content
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.write("line 1\nline 2\nline 3\nline 4\nline 5\n")

        # Commit the file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the JSON input for removing multiple lines
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-1,5 +1,2",
            "changes": [" line 1", "-line 2", "-line 3", " line 4", "-line 5"],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "remove_multiple_lines.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "line 1\nline 4"


def test_patch_modify_multiple_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create a file with initial content
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.write("line 1\nline 2\nline 3\n")

        # Commit the file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the JSON input for modifying multiple lines
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-1,3 +1,3",
            "changes": [
                "-line 1",
                "+modified line 1",
                "-line 2",
                "+modified line 2",
                "-line 3",
                "+modified line 3",
            ],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "modify_multiple_lines.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "modified line 1\nmodified line 2\nmodified line 3"


def test_patch_mixed_changes():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create a file with initial content
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.writelines(["line 1\n", "line 2\n", "line 3\n"])

        # Commit the file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the JSON input for mixed changes
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-1,3 +1,4",
            "changes": [
                "-line 1",
                "+modified line 1",
                " line 2",
                "-line 3",
                "+new line 3",
                "+added line 4",
            ],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "mixed_changes.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "modified line 1\nline 2\nnew line 3\nadded line 4"


def test_patch_sequential_patches():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create an empty file
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        RepoTool.run_command(f"touch {file_name}", tmpdir)

        # Commit the empty file to get its initial blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash1 = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare and apply the first patch (add lines)
        json_input1 = {
            "file_name": file_name,
            "blob_hash": blob_hash1,
            "diff_range": "-0,0 +1,2",
            "changes": ["+line 1", "+line 2"],
        }
        patch1 = Patch(**json_input1)
        patch_file1 = os.path.join(tmpdir, "add_lines.patch")
        patch1.to_patch_file(patch_file1)
        RepoTool.run_command(f"git apply {patch_file1}", tmpdir)
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'add lines'", tmpdir)
        _, blob_hash2 = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare and apply the second patch (modify and add a line)
        json_input2 = {
            "file_name": file_name,
            "blob_hash": blob_hash2,
            "diff_range": "-1,2 +1,3",
            "changes": ["-line 1", "+modified line 1", " line 2", "+added line 3"],
        }
        patch2 = Patch(**json_input2)
        patch_file2 = os.path.join(tmpdir, "modify_add_lines.patch")
        patch2.to_patch_file(patch_file2)
        RepoTool.run_command(f"git apply {patch_file2}", tmpdir)

        # Verify the file content
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "modified line 1\nline 2\nadded line 3"


def test_patch_reversible():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize git repo and create a file
        RepoTool.run_command("git init", tmpdir)
        file_name = "file.txt"
        file_path = os.path.join(tmpdir, file_name)
        with open(file_path, "w") as file:
            file.write("initial content\n")

        # Commit the file to get its blob hash
        RepoTool.run_command(f"git add {file_name}", tmpdir)
        RepoTool.run_command("git commit -m 'initial commit'", tmpdir)
        _, blob_hash = RepoTool.run_command("git rev-parse HEAD", tmpdir)

        # Prepare the JSON input for adding a new line
        json_input = {
            "file_name": file_name,
            "blob_hash": blob_hash,
            "diff_range": "-1 +1,2",
            "changes": [" initial content", "+new line"],
        }

        # Generate and apply the patch
        patch = Patch.model_validate(json_input)
        patch_file = os.path.join(tmpdir, "add_new_line.patch")
        patch.to_patch_file(patch_file)
        RepoTool.run_command(f"git apply {patch_file}", tmpdir)

        # Apply reverse patch
        RepoTool.run_command(f"git apply --reverse {patch_file}", tmpdir)

        # Verify the file content has returned to original
        with open(file_path, "r") as file:
            content = file.read().strip()
            assert content == "initial content"
