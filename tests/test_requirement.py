from models import Requirement
from repo_tool import RepoTool

import tempfile
import os


def test_requirement_is_fulfilled():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize a git repository
        RepoTool.run_command("git init", tmpdir)

        # Setup RepoTool
        repo_tool = RepoTool(repo_dir=tmpdir)

        # Create a requirement instance
        requirement = Requirement(
            description="a C++ binary named `hello` that outputs `hello world` to stdout",
            verification_commands=[
                f"cmake {tmpdir}",
                f"cmake --build {tmpdir}",
                os.path.join(tmpdir, "build", "hello"),
            ],
            expected_output="hello world",
        )

        # Initially, the requirement should not be fulfilled
        fulfilled, output = repo_tool.requirement_is_fulfilled(requirement)
        print(output)
        assert not fulfilled

        # Setup files necessary for the requirement
        cmake_content = "cmake_minimum_required(VERSION 3.0)\nproject(HelloWorld)\nadd_executable(hello main.cpp)"
        main_cpp_content = '#include <iostream>\nint main() { std::cout << "hello world" << std::endl; return 0; }'

        # Create CMakeLists.txt and main.cpp
        with open(os.path.join(tmpdir, "CMakeLists.txt"), "w") as file:
            file.write(cmake_content)
        with open(os.path.join(tmpdir, "main.cpp"), "w") as file:
            file.write(main_cpp_content)

        # Commit the changes to the repository
        RepoTool.run_command("git add .", tmpdir)
        RepoTool.run_command("git commit -m 'Add cmake and main files'", tmpdir)

        # Now, the requirement should still not be fulfilled since we haven't built the project
        fulfilled, output = repo_tool.requirement_is_fulfilled(requirement)
        print(output)
        assert not fulfilled
