from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class Action(str, Enum):
    CREATE = "create"
    DELETE = "delete"


class FileAction(BaseModel):
    action: Action = Field(description="File action, e.g. `create` or `delete`")
    file_name: str = Field(description="Name of file to create or delete")
    content: Optional[str] = Field(
        description="Optional content for file creation", default=None
    )


class DirectoryAction(BaseModel):
    action: Action = Field(description="Directory action e.g. `create` or `delete")
    directory_name: str = Field(description="Name of directory to create or delete")


class Patch(BaseModel):
    file_name: str = Field(description="Name of file to apply patch to")
    blob_hash: str = Field(description="Hash of the file blob in local git database")
    diff_range: str = Field(
        description="Diff range for patch file, describing lines to be acted upon"
    )
    changes: List[str] = Field(
        description="List of changes to file, of the form `+<content>` (indicating addition), `-<content>` (indicating removal) or ` <content>` (indicating no change)"
    )

    def to_patch_file(self, file_path: str):
        with open(file_path, "w") as patch_file:
            patch_file.write(f"diff --git a/{self.file_name} b/{self.file_name}\n")
            patch_file.write(f"index {self.blob_hash}..0000000 100644\n")
            patch_file.write(f"--- a/{self.file_name}\n")
            patch_file.write(f"+++ b/{self.file_name}\n")
            patch_file.write(f"@@ {self.diff_range} @@\n")

            for change in self.changes:
                patch_file.write(f"{change}\n")


class RepoChange(BaseModel):
    patch: Optional[Patch] = Field(
        description="Optional patch to apply describing file changes", default=None
    )
    file_action: Optional[FileAction] = Field(
        description="Optional file action, e.g. create or delete a file", default=None
    )
    directory_action: Optional[DirectoryAction] = Field(
        description="Optional directory action, e.g. create or delate a directory",
        default=None,
    )


class RepoToolInput(BaseModel):
    changes: List[RepoChange] = Field(
        description="List of changes to apply to repository, each consisting of either a Patch, a FileAction, or a DirectoryAction"
    )


class Requirement(BaseModel):
    description: str = Field(description="Description of the requirement")
    verification_commands: List[str] = Field(
        description="List of shell commands to verify the requirement"
    )
    expected_output: str = Field(
        description="Expected output from the verification commands to consider the requirement fulfilled"
    )


if __name__ == "__main__":
    print(RepoToolInput.model_json_schema())
