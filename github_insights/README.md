# Cardano Insights - GitHub Analytics

This module provides GitHub repository analytics for the Cardano ecosystem, focusing on development activity, pull request patterns, and release cycles.

## Overview

This project uses a modern data pipeline architecture:
- **dlt (data load tool)** for data ingestion from GitHub API
- **dbt (data build tool)** for data transformations using medallion architecture
- **DuckDB** as the analytical database
- **Python** for orchestration and data processing

## Architecture

```
GitHub API → dlt → DuckDB → dbt → Analytics
                   (Bronze)  (Silver/Gold)
```

### Data Layers

- **Bronze**: Raw GitHub API data (repositories, pull_requests, releases, issues)
- **Silver**: Cleaned and standardized data with feature classification  
- **Gold**: Business metrics and aggregated insights

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub API token (recommended for higher rate limits)

### Installation

```bash
# Install dependencies
pip install -e .

# Or install with development dependencies
pip install -e .[test]
```

### Configuration

1. **GitHub Token** (optional but recommended):
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

2. **dlt Configuration**: Edit `.dlt/secrets.toml`:
   ```toml
   [sources.github]
   token = "ghp_your_token_here"
   ```

### Usage

```bash
# Run the complete pipeline
make run-pipeline

# Or run components individually:
make run-github      # Ingest GitHub data
make run-dbt         # Run transformations
make export          # Export to parquet files
```

### Sample Data Pipeline

```bash
# Run with limited data for testing
make run-github-sample
```

## Data Sources

### Repositories Tracked

- `cardano-foundation/cardano-wallet`
- `input-output-hk/cardano-node` 
- `input-output-hk/plutus`
- `Emurgo/cardano-serialization-lib`
- `input-output-hk/cardano-ledger`
- `input-output-hk/ouroboros-network`

### Data Types

- **Pull Requests**: Titles, descriptions, authors, labels, metrics
- **Releases**: Release notes, versions, authors, dates
- **Issues**: Issue tracking and categorization  
- **Repositories**: Metadata and statistics

## dbt Models

### Bronze Layer (`models/bronze/`)
- `stg_github_pull_requests` - Raw PR data
- `stg_github_releases` - Raw release data
- `stg_github_repositories` - Raw repo data

### Silver Layer (`models/silver/`)
- `stg_pull_requests` - Cleaned PRs with feature classification
- `stg_releases` - Cleaned and deduplicated releases

### Gold Layer (`models/gold/`)
- `feature_prs_monthly` - Monthly feature PR trends
- `feature_releases_monthly` - Monthly release patterns
- `median_feature_prs_lace_vs_top10` - Comparative analysis
- `median_releases_lace_vs_top10` - Release frequency comparisons

## Feature Classification

Pull requests are automatically classified based on titles:
- `bug fix` - Bug fixes and patches
- `feature` - New features and enhancements  
- `refactor` - Code refactoring
- `test` - Test-related changes
- `documentation` - Documentation updates
- `not clear` - Unclear categorization

## Development

### Running Tests

```bash
make test                # Run all tests
make test-connectors     # Test connectors only
```

### Code Quality

```bash
make lint               # Check code style
make format             # Format code
```

### Documentation

```bash
make docs               # Generate and serve dbt docs
```

## Data Exports

Processed data is exported to `exports/` directory as parquet files:

- `stg_pull_requests.parquet` - All processed pull requests
- `stg_releases.parquet` - All processed releases
- `feature_prs_monthly.parquet` - Monthly PR metrics
- `feature_releases_monthly.parquet` - Monthly release metrics

## Integration with Cardano Insights

This module is designed to integrate with the main `cardano-insights` repository, providing GitHub analytics alongside Catalyst and other Cardano ecosystem data.

### Directory Structure

```
src/cardano_insights/
├── connectors/
│   └── github.py           # GitHub API connector
├── github_pipeline.py      # Main pipeline script
└── __init__.py

models/
├── bronze/                 # Raw data models
├── silver/                 # Cleaned data models  
├── gold/                   # Business metrics
├── sources.yml            # Data source definitions
└── schema.yml             # Model schemas and tests

tests/
├── connectors/            # Connector tests
└── __init__.py

scripts/
└── export_data.py         # Data export utilities
```

## Environment Variables

- `GITHUB_TOKEN` - GitHub personal access token
- `AWS_ACCESS_KEY_ID` - For S3 exports (optional)
- `AWS_SECRET_ACCESS_KEY` - For S3 exports (optional)

## Contributing

1. Follow the established medallion architecture
2. Add tests for new connectors
3. Update documentation for new models
4. Use descriptive commit messages
5. Ensure all tests pass before submitting

## License

This project is part of the Cardano Insights ecosystem.
