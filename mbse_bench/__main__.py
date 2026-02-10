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
from pathlib import Path
from openai import AsyncOpenAI, OpenAI
import dotenv

from mbse_bench.models import ModelConfig
from mbse_bench.tasks import load_task, load_llm_judge_config
from mbse_bench.runner import runtask


async def run_single_task(task_id: str, model_name: str, max_iterations: int, client: AsyncOpenAI, supports_tools: bool, responses_api: bool):
    """Run a single task and evaluate it."""
    print(f"\n{'='*70}")
    print(f"Running task: {task_id}")
    print(f"{'='*70}")
    
    # Load task
    tasks_dir = Path(__file__).parent.parent / "data" / "tasks" / task_id
    if not tasks_dir.exists():
        print(f"❌ Task directory not found: {tasks_dir}")
        return None
    
    llm_judge_config = load_llm_judge_config()
    task = load_task(str(tasks_dir), llm_judge_config)
    
    print(f"Task: {task.name}")
    print(f"Description: {task.description}")
    print(f"Type: {task.type}")
    
    
    # Run the task
    print(f"\n🤖 Running with model: {model_name}")
    try:
        results = await runtask(task, client, model_name, max_iterations, supports_tools, responses_api)
        
        # Display results
        print(f"\n{'='*70}")
        print("EVALUATION RESULTS")
        print(f"{'='*70}")
        
        if not results:
            print("No evaluation results returned")
            return None
        
        total_score = 0
        total_weight = 0
        
        for i, result in enumerate(results, 1):
            print(f"\nEvaluator {i}")
            print(f"  Score: {result.score:.2f} (weight: {result.weight})")
            explanation = result.explanation if result.explanation else "No explanation provided"
            print(f"  Explanation: {explanation[:200]}..." if len(explanation) > 200 else f"  Explanation: {explanation}")
            
            if result.details:
                print(f"  Details:")
                for key, value in result.details.items():
                    if hasattr(value, 'score'):
                        print(f"    - {key}: {value.score:.2f}")
                    else:
                        print(f"    - {key}: {value}")
            
            total_score += result.score * result.weight
            total_weight += result.weight
        
        weighted_avg = total_score / total_weight if total_weight > 0 else 0
        print(f"\n{'='*70}")
        print(f"WEIGHTED AVERAGE SCORE: {weighted_avg:.2f}")
        print(f"{'='*70}")
        
        return {
            "task_id": task_id,
            "model": model_name,
            "score": weighted_avg,
            "results": results
        }
            
    except Exception as e:
        print(f"\n❌ Error running task: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_models() -> list[ModelConfig]:
    """Load model configurations from config/models.json."""
    config_path = Path(__file__).parent.parent / "config" / "models.json"
    with open(config_path) as f:
        data = json.load(f)
        return [ModelConfig(**{
            "model_id": model["id"],
            "supports_tools": model.get("supportsTools", True),
            "support_reponses": model.get("supportsResponses"),
        }) for model in data.get("models", [])]


def load_client(azure: bool) -> OpenAI:
    if azure:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            print("❌ Error: AZURE_OPENAI_ENDPOINT not found in environment")
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
            print("❌ Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable")
            sys.exit(1)
        
        client = AsyncOpenAI(api_key=api_key)

    return client

async def async_main():
    parser = argparse.ArgumentParser(description="Run MBSE benchmark tasks")
    parser.add_argument(
        "--tasks",
        type=str,
        default="sample-task",
        help="Comma-separated list of task IDs to run (default: sample-task)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Model name to use, or 'all' to run all models from config/models.json (default: gpt-4o-mini)"
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
     
    # Parse task IDs
    task_ids = [t.strip() for t in args.tasks.split(",")]
    
    # Determine which models to run
    if args.model.lower() == "all":
        models = load_models()
        model_names = [model.model_id for model in models]
        if not model_names:
            print("❌ Error: No models found in config/models.json")
            sys.exit(1)
        print(f"Running with all {len(model_names)} models from config")
    else:
        models = [ModelConfig(args.model, supports_tools=not args.no_tools, supports_responses=args.responses, temperature=args.temp)]
    
    
    print(f"🚀 Starting MBSE Benchmark")
    print(f"Tasks: {', '.join(task_ids)}")
    print(f"Models: {', '.join(model.model_id for model in models)}")
    
    # Run tasks for each model
    all_results = []
    for model in models:
        print(f"\n{'='*70}")
        print(f"MODEL: {model.model_id}")
        print(f"{'='*70}")

        print(f"Max iterations: {args.max_iterations}")
        print(f"Tool calling: {'enabled' if model.supports_tools else 'disabled'}")
        
        for task_id in task_ids:
            result = await run_single_task(task_id, model.model_id, args.max_iterations, client, model.supports_tools, model.supports_responses)
            if result:
                all_results.append(result)
                print(f"result: {result}")
    
    # Summary
    if all_results:
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        
        # Group by model
        results_by_model = {}
        for result in all_results:
            model = result['model']
            if model not in results_by_model:
                results_by_model[model] = []
            results_by_model[model].append(result)
        
        # Display results grouped by model
        for model, results in results_by_model.items():
            print(f"\n{model}:")
            for result in results:
                print(f"  {result['task_id']}: {result['score']:.2f}")
            
            if len(results) > 1:
                avg_score = sum(r['score'] for r in results) / len(results)
                print(f"  Average: {avg_score:.2f}")
        
        # Overall average if multiple models
        if len(models) > 1:
            overall_avg = sum(r['score'] for r in all_results) / len(all_results)
            print(f"\nOverall Average (all models): {overall_avg:.2f}")
        
        print(f"{'='*70}")


def main():
    """Entry point for the mbse-bench command."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
