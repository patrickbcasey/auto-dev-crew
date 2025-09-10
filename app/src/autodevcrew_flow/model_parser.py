import re


class Edit:
    filename: str
    preceeding_lines: str
    following_lines: str
    changed_lines: str

    def __init__(self, filename, preceeding_lines, following_lines, changed_lines):
        self.filename = filename
        self.preceeding_lines = preceeding_lines
        self.following_lines = following_lines
        self.changed_lines = changed_lines


class OutputParser:
    patch_code: str
    model_output_file: str
    file_to_change: str | None

    def __init__(self, file_path: str):
        self.model_output_file = file_path
        self.patch_code = self.get_patch_code(file_path)

    def get_patch_code(self, file_path: str) -> str:
        patch = ""
        with open(file_path, "r") as file:
            output = "\n".join(file.readlines())
            start_pattern = r"<patch>"
            end_pattern = r"</patch>"

            code_pattern = re.compile(f"{start_pattern}(.*?){end_pattern}", re.DOTALL)
            patch = "\n".join(code_pattern.findall(output))
        return patch

    def get_edits(self) -> Edit | None:
        patch_contents = ""
        original_contents = ""
        filename = ""
        file_start_pattern = r"<file>"
        file_end_pattern = r"</file>"
        original_start_pattern = r"<original>"
        original_end_pattern = r"</original>"
        patch_start_pattern = r"<patch>"
        patch_end_pattern = r"</patch>"

        filename_pattern = re.compile(
            f"{file_start_pattern}(.*?){file_end_pattern}", re.DOTALL
        )
        original_code_pattern = re.compile(
            f"{original_start_pattern}(.*?){original_end_pattern}", re.DOTALL
        )
        patch_code_pattern = re.compile(
            f"{patch_start_pattern}(.*?){patch_end_pattern}", re.DOTALL
        )

        with open(self.model_output_file, "r") as file:
            original_lines = file.readlines()
            model_output = "".join(original_lines)
            filename = filename_pattern.findall(model_output)
            original_contents = original_code_pattern.findall(model_output)
            patch_contents = patch_code_pattern.findall(model_output)

        filename = "\n".join(filename)
        self.file_to_change = filename
        original_contents = "\n".join(original_contents)
        patch_contents = "\n".join(patch_contents)

        # for file, original, patch in zip(filename, original_contents, patch_contents):

        filename.strip()
        original_contents.strip("\n")
        patch_contents.strip("\n")

        original_lines = original_contents.splitlines()
        patch_lines = patch_contents.splitlines()

        buffer = []
        for i in range(0, len(patch_lines)):
            if patch_lines[i] not in original_lines:
                buffer.append((patch_lines[i]))
                preceeding_lines = patch_lines[:i]
        if len(patch_lines) < 1:
            return None

        end_index = patch_lines.index(buffer[-1])
        following_lines = "\n".join(patch_lines[end_index + 1 :])
        preceeding_lines = "\n".join(preceeding_lines)
        changed_lines = "\n".join(buffer)

        changed_lines = changed_lines.strip("\n")
        preceeding_lines = preceeding_lines.strip("\n")
        following_lines = following_lines.strip("\n")

        edits = Edit(
            filename,
            preceeding_lines,
            following_lines,
            changed_lines,
        )

        return edits

    def apply_edit(self, edit: Edit, file_path: str) -> str | None:
        with open(file_path) as file:
            original_file = file.readlines()

        # remove trailing whitespaces for matching
        # lines that preceed the edit location
        preceeding_lines = edit.preceeding_lines.split("\n")
        preceeding_lines_stripped = [line.strip() for line in preceeding_lines]
        # lines of the original program with the bug
        original_lines_stripped = [line.strip() for line in original_file]
        # search each line until there aren't enough lines left to fit the match
        start = -1
        end = -1
        for i in range(
            len(original_lines_stripped) - len(preceeding_lines_stripped) + 1
        ):
            # if a match is found
            if (
                original_lines_stripped[i : i + len(preceeding_lines_stripped)]
                == preceeding_lines_stripped
            ):
                start = i
                end = i + len(preceeding_lines_stripped)
                break

        # no match found
        if start == -1:
            print("matching failed")
            return None

        match = original_file[start:end]
        changed_lines = edit.changed_lines.split("\n")

        # match indentation in edit to context lines
        if preceeding_lines[0] in match[0]:
            indent = match[0].index(preceeding_lines[0])
            indented_change = "\n".join([" " * indent + line for line in changed_lines])

        matching_lines = "".join(match)
        before_match = "".join(original_file[:start])
        following_match = "".join(original_file[end:])

        edited_code = (
            before_match
            + "\n"
            + matching_lines
            + "\n"
            + indented_change
            + "\n"
            + following_match
        )

        with open(file_path, "w") as file:
            file.write(edited_code)

        return file_path

    def get_diff(self):
        print(self.file_to_change)
        return
