# GitHub Cardano Ecosystem Insights

A comprehensive data collection and analysis pipeline for the Cardano ecosystem on GitHub, providing insights into development activity, trends, and ecosystem health.

## 🎯 Project Overview

This project provides a **production-ready data pipeline** combining **dlt (data load tool)** for GitHub API ingestion with **dbt (data build tool)** for analytics transformations, following modern data engineering best practices.

### ✨ Key Features

- 🔄 **Modern Data Pipeline** - dlt ingestion → dbt transformations → analytics
- 🛡️ **Production Ready** - Comprehensive error handling, rate limiting, and monitoring  
- 📊 **Rich GitHub Data** - Repositories, pull requests, releases, issues with full metadata
- 🎛️ **Configurable** - Multiple repository sets and data volume controls
- 🧪 **Comprehensive Testing** - Full pytest suite with parametrized testing
- 📝 **Feature Classification** - Automatic PR categorization (bug fix, feature, refactor, etc.)
- 🏗️ **Medallion Architecture** - Bronze/Silver/Gold data layers with dbt

## 🏗️ Architecture

```
GitHub API → dlt → DuckDB → dbt → Analytics & Exports
            (Extract)  (Load)  (Transform)    (Serve)
```

### Data Pipeline Components

- **`dlt Pipeline`** - GitHub API connector with rate limiting and error handling
- **`DuckDB`** - Fast analytical database for local development and production
- **`dbt Models`** - Medallion architecture transformations (Bronze→Silver→Gold)
- **`pytest Suite`** - Comprehensive testing with mocks and integration tests

### Repository Structure

```
├── github_insights/                # Main dbt project
│   ├── src/cardano_insights/      # dlt connectors and pipeline
│   │   ├── connectors/github.py   # GitHub API connector
│   │   └── github_pipeline.py     # Pipeline orchestration
│   ├── models/                    # dbt models
│   │   ├── bronze/               # Raw API data
│   │   ├── silver/               # Cleaned & classified data
│   │   └── gold/                 # Business metrics
│   ├── tests/                    # pytest test suite
│   └── scripts/                  # Utility scripts
├── pipeline.py                   # Legacy root-level pipeline (deprecated)
└── run_pipeline.py              # Legacy runner (deprecated)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token (recommended for rate limits)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd github-trend-insights

# Navigate to main project
cd github_insights

# Install dependencies
pip install -e .
# or for development
pip install -e .[test]
```

### Configuration

1. **Set GitHub Token** (optional but recommended):
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

2. **Configure dlt** (edit `.dlt/secrets.toml`):
```toml
[sources.github]
token = "ghp_your_token_here"
```

### Usage

```bash
# Run complete pipeline
make run-pipeline

# Or run components separately
make run-github      # Collect GitHub data
make run-dbt         # Run dbt transformations  
make export          # Export to parquet files

# Development workflows
make run-github-sample  # Limited data for testing
make test              # Run all tests
make docs             # Generate dbt documentation
```

## 📊 Data Models

### Bronze Layer (Raw Data)
- `stg_github_repositories` - Raw repository metadata
- `stg_github_pull_requests` - Raw pull request data
- `stg_github_releases` - Raw release data

### Silver Layer (Cleaned Data)  
- `stg_pull_requests` - Cleaned PRs with feature classification
- `stg_releases` - Deduplicated and cleaned releases

### Gold Layer (Analytics)
- `feature_prs_monthly` - Monthly PR trends by feature type
- `feature_releases_monthly` - Release patterns over time
- `median_feature_prs_lace_vs_top10` - Comparative ecosystem analysis

## 🎯 Tracked Repositories

- **cardano-foundation/cardano-wallet** - Official Cardano wallet
- **input-output-hk/cardano-node** - Cardano node implementation
- **input-output-hk/plutus** - Plutus smart contract platform
- **Emurgo/cardano-serialization-lib** - Cardano serialization library
- **input-output-hk/cardano-ledger** - Ledger specifications
- **input-output-hk/ouroboros-network** - Networking layer

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test categories
make test-connectors    # Connector tests only
pytest tests/ -v        # Verbose output
pytest tests/ -m integration  # Integration tests only
```

## 🔄 Legacy Pipeline (Deprecated)

The root-level `pipeline.py` and `run_pipeline.py` are legacy components that are being phased out in favor of the new dbt-based architecture in `github_insights/`. They remain for backward compatibility but new development should use the dbt project.

## 📈 Data Exports

Processed data is automatically exported to parquet files:

- `exports/stg_pull_requests.parquet` - All processed pull requests
- `exports/stg_releases.parquet` - All processed releases  
- `exports/feature_prs_monthly.parquet` - Monthly PR analytics
- `exports/feature_releases_monthly.parquet` - Monthly release analytics

## 🤝 Contributing

1. Use the modern `github_insights/` structure for new development
2. Follow the established medallion architecture (Bronze→Silver→Gold)
3. Add tests for any new connectors or models
4. Update documentation for new features
5. Ensure all tests pass before submitting changes

## 📄 License

This project analyzes public GitHub data for research and analytics purposes.