from models import RepoToolInput, Requirement
from repo_tool import RepoTool
from rich import print
import requests
import json
import os


tools = [
    {
        "type": "function",
        "function": {
            "name": "implement_changes",
            "description": "Implement changes on repository described by JSON representation of RepoToolInput",
            "parameters": RepoToolInput.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_requirements",
            "description": "Checks to see if the requirement described by the given JSON representation is fulfilled. Returns a boolean `is_fulfilled` indicating success if true, and an str `output` (especially useful if unsuccessful).",
            "parameters": Requirement.model_json_schema(),
        },
    },
]


def main():
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json",
    }

    url = "https://api.openai.com/v1/chat/completions"

    dir_name = "cpp_hello"
    rt = RepoTool(dir_name)
    os.makedirs(dir_name, exist_ok=True)
    RepoTool.run_command("git init", cwd=rt.repo_dir)

    messages = [
        {
            "role": "system",
            "content": open("system.txt").read(),
        },
        {
            "role": "user",
            "content": "Requirement: build a CMake project and execute the binary named `hello` -- expected result is that it outputs `hello world` to stdout.",
        },
    ]

    payload = {
        "messages": messages,
        "model": "gpt-4-1106-preview",
        "tools": tools,
        "tool_choice": {"type": "function", "function": {"name": "check_requirements"}},
    }

    request = requests.post(url, json=payload, headers=headers)
    json_data = json.loads(request.content.decode())

    # print(json.dumps(json_data, indent=4))

    message = json_data["choices"][0]["message"]

    messages.append(message)
    tool_call = message["tool_calls"][0]
    args = tool_call["function"]["arguments"]

    requirement = Requirement.model_validate_json(args)
    print(requirement)

    is_fulfilled, output = rt.requirement_is_fulfilled(requirement)

    print(f"{is_fulfilled=}, {output=}")

    commit_counter = 1

    while True:
        if input("Generate repository changes? (y/n) ").lower() == "y":
            # add the tool call result message
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "content": f"{is_fulfilled=}, {output=}",
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": f"current blob hashes: {rt.fetch_blob_hashes()}",
                }
            )

            payload = {
                "messages": messages,
                "model": "gpt-4-1106-preview",
                "tools": tools,
                "tool_choice": {
                    "type": "function",
                    "function": {"name": "implement_changes"},
                },
            }

            response = requests.post(url, json=payload, headers=headers)
            json_data = json.loads(response.content.decode())
            message = json_data["choices"][0]["message"]
            messages.append(message)

            tool_call = message["tool_calls"][0]
            args = tool_call["function"]["arguments"]

            repo_changes = RepoToolInput.model_validate_json(args)
            print(repo_changes)
            rt.implement_changes(repo_changes)
            RepoTool.run_command(
                f"git commit -m 'commit #{commit_counter}'", cwd=rt.repo_dir
            )
            commit_counter += 1

            is_fulfilled, output = rt.requirement_is_fulfilled(requirement)
            print(f"{is_fulfilled=}, {output=}")

            if is_fulfilled:
                print("requirements fulfilled!")
                exit(0)

        else:
            print("До свидания!")
            exit(0)


if __name__ == "__main__":
    main()
