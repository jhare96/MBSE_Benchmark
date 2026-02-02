import json
import os
from openai import AsyncOpenAI

from filesystem import FileSystem, load_virtual_filesystem
from tools import get_virtual_filesystem_tools, toolcall
from tasks import load_all_tasks, load_tasks_sample
from models import Task
from evaluation import EvaluationContext, EvaluationResult, evaluate_task

NO_TOOLS_PROMPT = """{task_prompt}

Current files in the virtual filesystem:

{files_str}

Please provide your response including any unified diff patches within a triple backtick block needed to create or modify files.
Please only include one single triple backtick block for the diff for all the changes
e.g.
```
--- /dev/null
+++ math.txt
@@ -0,0 +1,4 @@
+0 + 0
+1 + 1
+2 / 3
+3 * 4
--- src/existing_file.txt
+++ src/existing_file.txt
@@ -0,0 +1,4 @@
+add new content here
+add new content here
+add new content here
+add new content here
```
"""

def build_task_prompt(task: Task, fs: FileSystem, supports_tools: bool) -> str:
    if supports_tools:
        return task.prompt
    else:
        # No-tool approach for models that don't support tool calling
        # Provide all context upfront and expect the model to output the patch
        files_str = "\n\n".join([f"=== {path} ===\n{content}" for path, content in fs.files.items()])
        full_prompt = NO_TOOLS_PROMPT.format(task_prompt=task.prompt, files_str=files_str)
        return full_prompt


def extract_and_apply_patch(final_response: str, fs: FileSystem) -> None:
    """manually extract unified diff from the model output for models that don't support tool usage"""
    patch_pattern = r'```(?:diff|patch)?\n(---.*?\n\+\+\+.*?)```'
    patches = re.findall(patch_pattern, final_response, re.DOTALL)
    
    for patch in patches:
        result = fs.apply_patch(patch)
        print(f"Patch Result: {result}")


async def runtask(task: Task, client: AsyncOpenAI, model_name: str, max_iterations: int, tools: list[dict[str,str]], supports_tools: bool = True) -> EvaluationResult:
    """agentic loop to run a task until completion"""
    fs = load_virtual_filesystem(task.task_dir)

    system_prompt = build_task_prompt(task, fs, supports_tools)
    messages = [{"type": "message", "role": "system", "content": system_prompt}]
    for iteration in range(max_iterations):
        # use chat completions for simplicity and general compatibility 
        response = await client.chat.completions.create(   
            model=model_name,
            messages=messages,
            tools=tools if supports_tools else [],
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)
        
        # Check if there are tool calls
        if not supports_tools or not assistant_message.tool_calls:
            break

        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            result = toolcall(fs, tool_call.function.name, json.loads(tool_call.function.arguments))
            
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )        
        
    final_response = ""
    for message in messages:
        # Handle both dict (user-created) and object (API response) formats
        if isinstance(message, dict):
            if message.get("type") == "message" and message.get("role") == "assistant":
                final_response += message["content"] + "\n"
        else:
            if getattr(message, "type", None) == "message" and getattr(message, "role", None) == "assistant":
                content = getattr(message, "content", None)
                if content:
                    # Content may be a list of content blocks
                    if isinstance(content, list):
                        for block in content:
                            if hasattr(block, "text"):
                                final_response += block.text + "\n"
                    else:
                        final_response += str(content) + "\n"

    if not supports_tools:
        extract_and_apply_patch(final_response, fs)

    context = EvaluationContext(
        original_files=load_virtual_filesystem(task.task_dir).snapshot(),
        modified_files=fs.snapshot(),
        task_prompt=task.prompt
    )
    return await evaluate_task(task, final_response, context, client)



async def run_tasks_in_parallel(tasks: list[Task], client: AsyncOpenAI, model_name: str, max_iterations: int) -> dict[str, EvaluationResult]:
    """runs multiple tasks in parallel and returns their outputs"""
    tools = get_virtual_filesystem_tools()
    all_outputs = {}
    for task in tasks:
        task_output = await runtask(task, client, model_name, max_iterations, tools, async_call=True)
        all_outputs[task.name] = task_output
    return all_outputs



async def benchmark(client: AsyncOpenAI, model_name: str, max_iterations: int, supports_tools: bool) -> dict[str, EvaluationResult]:
    """runs the full benchmark on a set of tasks and returns their outputs"""
    tools = get_virtual_filesystem_tools()
    tasks = list(filter(lambda task: task.evaluation.type == "llm-judge", load_tasks_sample()))
    all_outputs = {}
    for task in tasks:
        task_output = await runtask(task, client, model_name, max_iterations, tools, supports_tools)
        all_outputs[task.name] = task_output
    
    return all_outputs



if __name__ == "__main__":
    import asyncio
    import re
    import dotenv
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    dotenv.load_dotenv('../.env')

    async def main():
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        # Get Azure AD credential
        credential = DefaultAzureCredential()

        # Get a token for Azure Cognitive Services
        token = credential.get_token("https://cognitiveservices.azure.com/.default")

        # Use AsyncOpenAI with base_url format
        base_url = f"{endpoint}openai/v1/"

        client = AsyncOpenAI(
            api_key=token.token,  # Use the Azure AD token as the API key
            base_url=base_url,
        )

        results = await benchmark(client, model_name="gpt-4.1", max_iterations=5, supports_tools=False)
        return results

    outputs = asyncio.run(main())

    print("Benchmark Results:")
    for task_name, evaluation in outputs.items():
        print(f"Task: {task_name}")
        print(f"Score: {evaluation.score}")
        print(f"Explanation: {evaluation.explanation}")
        if evaluation.details:
            print("Details:")
            for criterion, detail in evaluation.details.items():
                print(f"  {criterion}: {detail.score} - {detail.feedback}")
        print("\n")
    print("Benchmark completed.")
