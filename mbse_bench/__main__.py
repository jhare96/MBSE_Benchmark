#!/usr/bin/env python3
"""
Main entry point for running the MBSE benchmark.

Usage:
    python run_benchmark.py [--tasks TASK_IDS] [--model MODEL_NAME] [--max-iterations N]
    
Examples:
    # Run a few sample tasks
    python run_benchmark.py
    
    # Run specific tasks
    python run_benchmark.py --tasks sample-task,sysml-generate-actions-001
    
    # Use a different model
    python run_benchmark.py --model gpt-4o --tasks sample-task
"""

import asyncio
import argparse
import sys
import os
import re
import json
import time
from pathlib import Path
from openai import AsyncOpenAI, OpenAI
import dotenv
from datetime import datetime

from mbse_bench.models import ModelConfig
from mbse_bench.tasks import load_task, load_llm_judge_config, load_all_tasks
from mbse_bench.runner import runtask
from mbse_bench.results import save_result


# ANSI Color codes
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def format_time(seconds: float) -> str:
    """Format time in seconds to human-readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds / 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def format_score(score: float) -> str:
    """Format score as percentage."""
    return f"{int(score * 100)}%"


def get_score_color(score: float) -> str:
    """Get color based on score."""
    if score >= 0.8:
        return Colors.GREEN
    elif score >= 0.5:
        return Colors.YELLOW
    elif score > 0:
        return Colors.RED
    return Colors.GRAY


def progress_bar(value: int, max_val: int, width: int = 40, color: str = Colors.CYAN) -> str:
    """Create a progress bar."""
    if max_val == 0:
        pct = 0
    else:
        pct = value / max_val
    filled = int(pct * width)
    bar = color + "━" * filled + Colors.GRAY + "─" * (width - filled) + Colors.RESET
    return bar


def get_grade(score: float) -> tuple[str, str]:
    """Get letter grade and color for score."""
    if score >= 0.9:
        return "A", Colors.GREEN
    elif score >= 0.8:
        return "B", Colors.CYAN
    elif score >= 0.7:
        return "C", Colors.YELLOW
    elif score >= 0.6:
        return "D", Colors.RED
    return "F", Colors.RED


async def run_single_task(task_id: str, model_name: str, max_iterations: int, client: AsyncOpenAI, supports_tools: bool, responses_api: bool, task_num: int, total_tasks: int, start_time: float, temperature: float = 0.0):
    """Run a single task and evaluate it."""
    # Show task progress
    elapsed = time.time() - start_time
    pct = int((task_num - 1) / total_tasks * 100) if total_tasks > 0 else 0
    print(f"\r{Colors.YELLOW}◐{Colors.RESET} {Colors.GRAY}[{task_num}/{total_tasks}]{Colors.RESET} {Colors.YELLOW}{task_id[:40].ljust(40)}{Colors.RESET} {Colors.GRAY}{pct}% • {format_time(elapsed)}{Colors.RESET}", end="", flush=True)
    
    # Load task
    tasks_dir = Path(__file__).parent.parent / "data" / "tasks" / task_id
    if not tasks_dir.exists():
        print(f"\r{Colors.RED}✗{Colors.RESET} {task_id[:40].ljust(40)} {Colors.RED}Task not found{Colors.RESET}")
        return None
    
    llm_judge_config = load_llm_judge_config()
    task = load_task(str(tasks_dir), llm_judge_config)
    
    task_start = time.time()
    
    try:
        results = await runtask(task, client, model_name, max_iterations, supports_tools, responses_api, temperature)
        
        if not results:
            print(f"\r{Colors.RED}✗{Colors.RESET} {task_id[:40].ljust(40)} {Colors.RED}No results{Colors.RESET}")
            return None
        
        total_score = 0
        total_weight = 0
        
        for result in results:
            total_score += result.score * result.weight
            total_weight += result.weight
        
        weighted_avg = total_score / total_weight if total_weight > 0 else 0
        task_time = time.time() - task_start
        
        # Display result inline
        score_color = get_score_color(weighted_avg)
        status = f"{Colors.GREEN}✓{Colors.RESET}" if weighted_avg >= 0.5 else f"{Colors.RED}✗{Colors.RESET}"
        print(f"\r{status} {task_id[:32].ljust(32)} {score_color}{format_score(weighted_avg)}{Colors.RESET} {Colors.GRAY}{format_time(task_time)}{Colors.RESET}")
        
        
        return {
            "task_id": task_id,
            "model": model_name,
            "score": weighted_avg,
            "latency_ms": task_time * 1000,
            "results": results
        }
            
    except Exception as e:
        print(f"\r{Colors.RED}✗{Colors.RESET} {task_id[:40].ljust(40)} {Colors.RED}Error: {str(e)[:30]}{Colors.RESET}")
        return {
            "task_id": task_id,
            "model": model_name,
            "score": 0.0,
            "latency_ms": 0,
            "error": str(e)
        }


def load_models() -> list[ModelConfig]:
    """Load model configurations from config/models.json."""
    config_path = Path(__file__).parent.parent / "config" / "models.json"
    with open(config_path) as f:
        data = json.load(f)
        return [ModelConfig(**{
            "model_id": model["id"],
            "supports_tools": model.get("supportsTools", True),
            "supports_responses": model.get("supportsResponses"),
        }) for model in data.get("models", [])]


def load_client(azure: bool) -> OpenAI:
    if azure:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            print(f"{Colors.RED}✗ Error: AZURE_OPENAI_ENDPOINT not found in environment{Colors.RESET}")
            sys.exit(1)

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
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"{Colors.RED}✗ Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable{Colors.RESET}")
            sys.exit(1)
        
        client = AsyncOpenAI(api_key=api_key)

    return client

async def async_main():
    parser = argparse.ArgumentParser(description="Run MBSE benchmark tasks")
    parser.add_argument(
        "--task",
        "--tasks",
        type=str,
        dest="tasks",
        default=None,
        help="Comma-separated list of task IDs to run (default: all tasks)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1",
        help="Model name to use, or 'all' to run all models from config/models.json (default: gpt-4.1)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum iterations for agent loop (default: 10)"
    )
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Disable tool calling (use patch-based approach)"
    )
    parser.add_argument(
        "--azure",
        action="store_true",
        help="Use Azure OpenAI instead of OpenAI"
    )
    parser.add_argument(
        "--responses",
        type=bool,
        default=True,
        help="Supports OpenAI Responses API default = true"
    )
    parser.add_argument(
        '--temp',
        type=float,
        default=0.0,
        help="temperature of the model to use, this does *not* override the model config if you use --model all"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    dotenv.load_dotenv()
    
    # Set up OpenAI client
    client = load_client(args.azure)
     
    # Parse task IDs - load all tasks if none specified
    if args.tasks:
        task_ids = [t.strip() for t in args.tasks.split(",")]
    else:
        # Load all tasks
        print(f"{Colors.GRAY}Loading all tasks...{Colors.RESET}", end="", flush=True)
        all_tasks = load_all_tasks()
        task_ids = [task.id for task in all_tasks]
        if not task_ids:
            print(f"\r{Colors.RED}✗ No tasks found in data/tasks{Colors.RESET}")
            sys.exit(1)
        print(f"\r{Colors.GREEN}✓{Colors.RESET} Loaded {Colors.BOLD}{len(task_ids)}{Colors.RESET} tasks from {Colors.CYAN}data/tasks{Colors.RESET}")
    
    # Determine which models to run
    if args.model.lower() == "all":
        models = load_models()
        model_names = [model.model_id for model in models]
        if not model_names:
            print("❌ Error: No models found in config/models.json")
            sys.exit(1)

    else:
        models = [ModelConfig(args.model, supports_tools=not args.no_tools, supports_responses=args.responses, temperature=args.temp)]
    
    
    # Run tasks for each model
    all_results = []
    
    for model in models:
        start_time = time.time()
        
        # Header
        print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 MBSE Benchmark{Colors.RESET} {Colors.GRAY}•{Colors.RESET} {Colors.MAGENTA}{model.model_id}{Colors.RESET}")
        print(f"{Colors.CYAN}{'━' * 80}{Colors.RESET}")
        print(f"{Colors.GRAY}Running {len(task_ids)} tasks{Colors.RESET}\n")
        
        model_results = []
        
        # Run each task
        for idx, task_id in enumerate(task_ids, 1):
            result = await run_single_task(
                task_id, 
                model.model_id, 
                args.max_iterations, 
                client, 
                model.supports_tools, 
                model.supports_responses,
                idx,
                len(task_ids),
                start_time,
                model.temperature
            )
            if result:
                model_results.append(result)
                all_results.append(result)
    
        # Summary for this model
        if model_results:
            duration = time.time() - start_time
            avg_score = sum(r['score'] for r in model_results) / len(model_results)
            passed = len([r for r in model_results if r['score'] >= 0.5])
            perfect = len([r for r in model_results if r['score'] == 1.0])
            grade, grade_color = get_grade(avg_score)
            
            print(f"\n{Colors.BOLD}{Colors.GREEN}✓ Benchmark Complete{Colors.RESET}")
            
            # Overall progress bar
            completed = len(model_results)
            total = len(task_ids)
            pct_complete = int((completed / total) * 100) if total > 0 else 0
            print(f"\n{progress_bar(completed, total, 40, Colors.GREEN)} {Colors.GREEN}{Colors.BOLD}{pct_complete}%{Colors.RESET} {Colors.GRAY}({completed}/{total}){Colors.RESET}")
            
            # Score display
            score_color = get_score_color(avg_score)
            pct = int(avg_score * 100)
            print(f"\nScore: {score_color}{Colors.BOLD}{format_score(avg_score)}{Colors.RESET} {grade_color}{Colors.BOLD}[{grade}]{Colors.RESET} {Colors.GRAY}•{Colors.RESET} {progress_bar(pct, 100, 20, score_color)}")
            
            # Stats
            failed = len(model_results) - passed
            print(f"\n{Colors.GREEN}✓ {passed} passed{Colors.RESET} {Colors.GRAY}│{Colors.RESET} {Colors.RED}✗ {failed} failed{Colors.RESET} {Colors.GRAY}│{Colors.RESET} {Colors.YELLOW}★ {perfect} perfect{Colors.RESET} {Colors.GRAY}│{Colors.RESET} ⏱ {format_time(duration)}")
            
            # Top performers
            sorted_results = sorted(model_results, key=lambda x: x['score'], reverse=True)
            top3 = sorted_results[:3]
            
            if top3:
                print(f"\n{Colors.BOLD}🏆 Best{Colors.RESET}")
                medals = ["🥇", "🥈", "🥉"]
                for i, result in enumerate(top3):
                    medal = medals[i] if i < len(medals) else "  •"
                    task_name = result['task_id'][:28].ljust(28)
                    score_color = get_score_color(result['score'])
                    print(f"  {medal} {task_name} {score_color}{format_score(result['score'])}{Colors.RESET}")
            
            # Bottom performers
            bottom3 = [r for r in sorted_results if r['score'] < 0.5][-3:]
            if bottom3:
                print(f"\n{Colors.BOLD}📉 Needs Work{Colors.RESET}")
                for result in bottom3:
                    task_name = result['task_id'][:28].ljust(28)
                    score_color = get_score_color(result['score'])
                    print(f"  {Colors.RED}•{Colors.RESET} {task_name} {score_color}{format_score(result['score'])}{Colors.RESET}")
            
            # Export results to JSON
            output_path = save_result(
                model.model_id,
                avg_score,
                model_results,
                duration
            )
            
            # Footer
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{Colors.GRAY}{'-' * 80}{Colors.RESET}")
            print(f"{Colors.GRAY}Saved: {Colors.CYAN}{output_path}{Colors.RESET}")
            print(f"{Colors.GRAY}Time: {timestamp}{Colors.RESET}\n")
    
    # Overall summary if multiple models
    if len(models) > 1 and all_results:
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 Overall Summary{Colors.RESET}")
        print(f"{Colors.CYAN}{'━' * 80}{Colors.RESET}")
        
        # Group by model
        results_by_model = {}
        for result in all_results:
            model = result['model']
            if model not in results_by_model:
                results_by_model[model] = []
            results_by_model[model].append(result)
        
        # Display results grouped by model
        for model_name, results in results_by_model.items():
            avg_score = sum(r['score'] for r in results) / len(results)
            score_color = get_score_color(avg_score)
            print(f"\n{Colors.MAGENTA}{model_name}{Colors.RESET}")
            for result in results:
                task_score_color = get_score_color(result['score'])
                print(f"  {result['task_id'][:40]}: {task_score_color}{format_score(result['score'])}{Colors.RESET}")
            print(f"  {Colors.BOLD}Average: {score_color}{format_score(avg_score)}{Colors.RESET}")
        
        # Overall average
        overall_avg = sum(r['score'] for r in all_results) / len(all_results)
        overall_color = get_score_color(overall_avg)
        print(f"\n{Colors.BOLD}Overall Average: {overall_color}{format_score(overall_avg)}{Colors.RESET}")
        print(f"{Colors.GRAY}{'─' * 80}{Colors.RESET}\n")


def main():
    """Entry point for the mbse-bench command."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
