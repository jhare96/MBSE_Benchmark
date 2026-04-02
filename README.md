# MBSE Benchmark

A benchmarking framework for evaluating AI models on Model-Based Systems Engineering tasks, with a focus on SysML v2.

## Overview

This tool provides a standardized way to benchmark AI models against a curated set of MBSE tasks, with versioning and a colorized CLI output.

## Features

- 🐍 **Python-powered** - Simple setup with Python 3.10+
- 🤖 **Multi-model support** - Test any AI model via OpenAI-compatible APIs (Azure, OpenAI, local models)
- 📊 **Versioned benchmarks** - Track changes to tasks, tools, and datasets
- 📈 **GitHub Actions** - Automated benchmark runs with published rankings
- 🔧 **SysML v2 Validators** - Built-in syntax validation and component extraction

## SysML v2 Tasks

The benchmark includes 59 SysML v2 tasks across 7 categories:

- **Validation** (6 tasks, e.g., `sysml-valid-detection-001`): Syntax validation, error detection
- **Extraction** (8 tasks, e.g., `sysml-extract-parts-001`): Part, port, requirement, connection, attribute, action, hierarchy, and interface extraction
- **Analysis** (11 tasks, e.g., `sysml-analyze-flow-001`): Specialization, flow, constraints, dependencies, variations, topology, individuals, cross-references, and state machine analysis
- **Requirements Traceability** (5 tasks, e.g., `sysml-req-satisfaction-001`): Satisfaction, coverage, constraint, derivation, and impact analysis
- **Generation** (14 tasks, e.g., `sysml-generate-part-001`): Generating valid SysML v2 from natural language requirements
- **Transformation** (12 tasks, e.g., `sysml-transform-refactor-001`): Converting SysML v2 to/from other representations (PlantUML, TypeScript, documentation, etc.)
- **Advanced Semantic Analysis** (3 tasks, e.g., `sysml-advanced-quality-001`): Expert-level model quality, pattern, and merge analysis

### Source Models

The SysML v2 models in `data/tasks/models/source/` are from the
[GfSE SysML-v2-Models](https://github.com/GfSE/SysML-v2-Models) repository
(BSD-3-Clause license).

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/jhare96/MBSE_Benchmark.git
cd MBSE_Benchmark

# Install dependencies
pip install -e .
```

### Requirements

- Python 3.10 or higher
- An OpenAI-compatible API key (Azure AI Foundry, OpenAI, or local model server)

## Usage

```bash
# Run all tasks with the default model (gpt-4.1)
python -m mbse_bench

# Run benchmark for a specific model
python -m mbse_bench --model gpt-4.1

# Run specific tasks
python -m mbse_bench --tasks sysml-valid-detection-001,sysml-extract-parts-001

# Run all configured models from config/models.json
python -m mbse_bench --model all

# Use Azure OpenAI (with DefaultAzureCredential)
python -m mbse_bench --model gpt-4.1 --azure

# Disable tool calling
python -m mbse_bench --model gpt-4.1 --no-tools
```

## Configuration

### Models (`config/models.json`)

Define your AI models with their specifications:

```json
{
  "models": [
    {
      "id": "gpt-4.1",
      "name": "GPT-4.1",
      "provider": "azure",
      "envKey": "AZURE_OPENAI_API_KEY",
      "envEndpoint": "AZURE_OPENAI_ENDPOINT",
      "deployment": "gpt-4.1",
      "supportsResponses": true,
      "supportsTools": true
    },
    {
      "id": "local-model",
      "name": "Local Model",
      "provider": "openai-compatible",
      "envEndpoint": "LOCAL_MODEL_URL",
      "model": "your-model-name",
      "supportsTools": true
    }
  ]
}
```

See [docs/model-configuration.md](./docs/model-configuration.md) for the full list of supported properties and models.

### Environment Variables

Copy `.env.example` to `.env` and set credentials for your AI providers:

```bash
# Azure AI Foundry / Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Local models (LM Studio, Ollama, vLLM, etc.)
LOCAL_API_KEY=
LOCAL_MODEL_URL=http://localhost:1234/v1
```

## Project Structure

```text
├── mbse_bench/           # Python package (benchmark runner)
│   ├── __main__.py       # CLI entry point
│   ├── runner.py         # Task runner / agent loop
│   ├── evaluation.py     # Evaluation strategies
│   ├── tasks.py          # Task loading
│   ├── models.py         # Model configuration
│   ├── filesystem.py     # Virtual filesystem utilities
│   ├── tools.py          # Agent tools
│   └── results.py        # Result saving
├── data/
│   ├── tasks/            # Benchmark task definitions
│   │   ├── models/       # Source SysML models (from GfSE)
│   │   │   ├── source/   # Valid models
│   │   │   └── invalid/  # Intentionally invalid models
│   │   ├── index.json    # Task registry with categories
│   │   └── sysml-*/      # Individual task definitions
│   └── results/          # Stored benchmark results
├── config/
│   ├── models.json       # Model configurations
│   └── benchmark.json    # Benchmark runner settings
└── docs/                 # Extended documentation
```

## Benchmark Versioning

The benchmark version is computed from:

- Task definitions
- Available tools
- Evaluation criteria
- Base dataset

Any change to these creates a new version, ensuring result comparability.

## Results

Results are stored in `data/results/` organized by benchmark version and timestamp:

```text
data/results/
├── 0.1.0-202512221459/
│   ├── gpt-4.1.json
│   └── deepseek-v3.2.json
└── 0.1.0-202512240921/
    └── gpt-5.2.json
```

## License

MIT License

## Contributing

See [AGENTS.md](./AGENTS.md) for AI agent contribution guidelines.
