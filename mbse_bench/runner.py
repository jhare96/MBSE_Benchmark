import json
import os
from openai import AsyncOpenAI
import re
from mbse_bench.filesystem import FileSystem, load_virtual_filesystem
from mbse_bench.tools import get_virtual_filesystem_tools, toolcall
from mbse_bench.tasks import load_all_tasks, load_tasks_sample
from mbse_bench.models import Task
from mbse_bench.evaluation import EvaluationContext, EvaluationResult, evaluate_task

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


async def get_response(client, model_name, input, tools, responses_api, temperature: float):
    if responses_api:
        return await client.responses.create(
            model=model_name,
            input=input,
            tools=tools,
            temperature=temperature,
        )
    else:
        return await client.chat.completions.create(   
            model=model_name,
            messages=input,
            tools=tools,
            temperature=temperature,
        )


def format_response(input: list) -> str:
    formatted_output = ""
    for item in input:
        if isinstance(item, dict):
            formatted_output += f"[{item.get('role', 'unknown')}]\n{item.get('content', '')}\n"
        elif hasattr(item, 'role') and hasattr(item, 'content') and getattr(item, 'content') is not None:
            formatted_output += f"[{getattr(item, 'role', 'unknown')}]\n{getattr(item, 'content', '')}\n"
        # don't include tool calls as we only want to judge the final output.
    return formatted_output

async def runtask(task: Task, client: AsyncOpenAI, model_name: str, max_iterations: int, supports_tools: bool, responses_api: bool, temperature: float) -> EvaluationResult:
    """agentic loop to run a task until completion"""
    fs = load_virtual_filesystem(task.task_dir)
    tools = get_virtual_filesystem_tools(responses_api)
    system_prompt = build_task_prompt(task, fs, supports_tools)
    input = [{"type": "message", "role": "system", "content": system_prompt}]
    for iteration in range(max_iterations):
        response = await get_response(client, model_name, input, tools if supports_tools else [], responses_api, temperature)
        if responses_api:
            input += response.output
            tool_calls = [item for item in response.output if item.type == "function_call"]
        else: # chat completions
            assistant_message = response.choices[0].message
            input.append(assistant_message)
            tool_calls = assistant_message.tool_calls
        
        # Check if there are tool calls
        if not supports_tools or not tool_calls:
            break

        # Process each tool call
        for tool_call in tool_calls:
            fn_name = tool_call.name if responses_api else tool_call.function.name
            args = tool_call.arguments if responses_api else tool_call.function.arguments
            result = toolcall(fs, fn_name, json.loads(args))
            
            if responses_api:
                input.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,  # Changed from tool_call.id
                        "output": str(result),  # Changed from json.dumps dict to just the result string
                    }
                )
            else:
                input.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    }
                ) 
        
    final_response = format_response(input)
    
    if not supports_tools:
        extract_and_apply_patch(final_response, fs)

    context = EvaluationContext(
        original_files=load_virtual_filesystem(task.task_dir).snapshot(),
        modified_files=fs.snapshot(),
        task_prompt=task.prompt
    )
    return await evaluate_task(task, final_response, context, client)



async def run_tasks_in_parallel(tasks: list[Task], client: AsyncOpenAI, model_name: str, max_iterations: int) -> dict[str, list[EvaluationResult]]:
    """runs multiple tasks in parallel and returns their outputs"""
    all_outputs = {}
    for task in tasks:
        task_output = await runtask(task, client, model_name, max_iterations, async_call=True)
        all_outputs[task.name] = task_output
    return all_outputs



async def benchmark(client: AsyncOpenAI, model_name: str, max_iterations: int, supports_tools: bool, responses_api: bool, temperature: float) -> dict[str, list[EvaluationResult]]:
    """runs the full benchmark on a set of tasks and returns their outputs"""
    tasks = load_tasks_sample()
    all_outputs = {}
    for task in tasks:
        task_output = await runtask(task, client, model_name, max_iterations, supports_tools, responses_api, temperature)
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
