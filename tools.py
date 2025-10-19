

import re
import os
from indexer import query_index
from langchain_core.documents import Document
from pathlib import Path
from subprocess import run


def read_file(file_path: str, from_line: int |  None = None, to_line: int | None = None, read_entire_file: bool = False) -> str:
    """
    Reads a file and returns the specified lines or the entire file content.
    """
    try:
        with open(file_path, "r") as file:
            if read_entire_file:
                return file.read()
            else:
                lines = file.readlines()
                return "".join(lines[from_line - 1:to_line])
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return ""

def write_file(file_path: str, content: str, insert: bool, from_line: int | None = None, to_line: int |  None = None) -> str:
    """
    Replaces or inserts content in a file
    If insert is true, creates file if it does not exist and inserts content from from_line
    If insert is false, replaces content from from_line to to_line(exclusive)
    """
    try:
        lines = []
        content_lines = content.splitlines()

        print("Content lines to write/insert:")
        print(content_lines)

        file_exists = os.path.exists(file_path)

        if insert and not file_exists:
            path = Path(file_path)
            print("Creating file {}".format(file_path))
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w+") as file:
                file.write("\n".join(content_lines))
            return
        with open(file_path, "r") as file:
            lines = file.readlines()
        print("Current file lines:")
        print(lines)
        if insert:
            if from_line == None:
                from_line = 1
            lines[from_line - 1:from_line - 1] = content_lines
        else:
            lines[from_line - 1:to_line] = content_lines
        print("Updated file lines:")
        print(lines)
        with open(file_path, "w") as file:
            file.write("\n".join(lines))
        return "File updated successfully."
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return str(e)

def list_directory(path: str) -> str:
    """
    Lists all files in the given directory path and its subdirectories.
    """
    result = []
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = '-' * 4 * (level)
        result.append('{}{}/'.format(indent, os.path.basename(root)))
        subindent = '-' * 4 * (level + 1)
        for f in files:
            result.append('{}{}'.format(subindent, f))
    return "\n".join(result)

def grep(root_path, pattern):
    """
    Searches for a regex pattern in all files under the given root directory.
    """
    regex = re.compile(pattern, re.IGNORECASE)

    print("Searching for pattern:", pattern)
    result = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, start=1):
                        if regex.search(line):
                            result.append(f"{file_path}:{line_num}:{line.strip()}")
            except (IOError, OSError):
                continue
    print("Grep results:", result)
    return result

def query(prompt: str) -> list[Document]:
    """
    Performs a vector similarity search on the indexed codebase using the provided prompt.
    Use this to search for relevant code snippets or files based on the prompt.
    """
    return query_index(prompt)

def execute_command(command: str) -> dict:
    """
    Executes a shell command and returns the output.
    Note that the command will be executed in a Windows 11 machine.
    """
    try:
        inp = input("Can I run the command (y/n): {}\n".format(command))
        if inp.lower() == 'n':
            return "Command execution cancelled by user."
        print("Executing command:", command)
        result = run(command, capture_output=True, text=True, shell=True)
        print("Command output:", result.stdout)
        return {
            "output" : result.stdout,
            "error" : result.stderr
        }
    except Exception as e:
        return str(e)