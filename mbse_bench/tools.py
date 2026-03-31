from mbse_bench.filesystem import FileSystem


def get_virtual_filesystem_tools(responses_api: bool) -> list[dict[str, str]]:
    """Returns the tool definitions for the virtual filesystem."""
    tools = [
        {
            "type": "function",
            "name": "read_file",
            "description": "Reads the contents of a file at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path to the file to read."},
                },
                "required": ["path"],
            }
        },
        {
            "type": "function",
            "name": "list_files",
            "description": "Lists all files in the given directory path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The directory path to list files from."},
                },
                "required": ["path"],
            },
        },
        {
            "type": "function",
            "name": "apply_patch",
            "description": "Applies a unified diff patch to the virtual filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patch": {"type": "string", "description": "The unified diff patch to apply."},
                },
                "required": ["patch"],
            },
        }
    ]
    if responses_api:
        return tools
    # else chat completions
    chat_completion_tools = []
    for tool in tools:
        chat_completion_tools.append({
            "type": tool["type"],
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            }
        })
    return chat_completion_tools



def toolcall(fs: FileSystem, tool_name: str, arguments):
    if tool_name == "read_file":
        return fs.read_file(arguments["path"])
    elif tool_name == "list_files":
        return fs.list_files(arguments["path"])
    elif tool_name == "apply_patch":
        fs.apply_patch(arguments["patch"])
        return "Patch applied."