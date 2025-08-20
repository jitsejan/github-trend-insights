# GitHub Cardano Wallet Ecosystem Insights

A comprehensive data collection and analysis pipeline for the entire Cardano wallet ecosystem on GitHub.

## 🎯 Project Overview

This project provides a production-ready **dlt (data load tool)** pipeline for collecting GitHub data from the Cardano wallet ecosystem. It features comprehensive error handling, incremental loading, rate limiting, and state management.

### ✨ Key Features

- 🔄 **Incremental Loading** - Only processes new data, skipping existing repositories
- 🛡️ **Comprehensive Error Handling** - Robust retry logic and graceful failure handling
- ⚡ **Rate Limiting** - Intelligent GitHub API rate limit management
- 📊 **Rich Data Collection** - Repositories, pull requests, releases, labels, and metadata
- 🎛️ **Configurable** - Multiple predefined configurations and custom parameters
- 📝 **Production Logging** - Detailed logging with configurable levels and file output
- 🗄️ **DuckDB Integration** - Fast, local analytical database
- ☁️ **S3 Support** - Cloud storage integration for large datasets

## 🚀 Quick Start

### Prerequisites

```bash
# Install uv (recommended Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install -r requirements.txt
```

### Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repo-url>
   cd github-trend-insights
   uv sync
   # or: pip install -e .
   ```

2. **Configure environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your GitHub Personal Access Token
   # Get token from: https://github.com/settings/tokens
   GITHUB_PAT=ghp_your_token_here
   ```

3. **Run the pipeline:**
   ```bash
   # Quick test run (10 repositories)
   python run_pipeline.py --config test
   
   # Full Cardano ecosystem (500 repositories)
   python run_pipeline.py --config cardano
   
   # Popular wallets only (100 repos, 5+ stars)
   python run_pipeline.py --config cardano-popular
   ```

## 🎛️ Configuration Options

### Predefined Configurations

| Config | Description | Repos | Min Stars |
|--------|-------------|-------|-----------|
| `cardano` | Complete Cardano wallet ecosystem | 500 | 0 |
| `cardano-popular` | Popular Cardano wallets | 100 | 5+ |
| `cardano-active` | Recently active projects | 200 | 0 |
| `test` | Small test run | 10 | 0 |

### Custom Parameters

```bash
# Custom search and limits
python run_pipeline.py --search "ada wallet" --max-repos 50 --min-stars 3

# Specify database file
python run_pipeline.py --config cardano --database cardano_wallets.duckdb

# Enable debug logging
python run_pipeline.py --config test --log-level DEBUG --log-file logs/debug.log

# Include archived repositories
python run_pipeline.py --search "cardano" --include-archived
```

### Command Line Help

```bash
python run_pipeline.py --help
```

## 📊 Data Schema

The pipeline collects three main data types:

### Repositories
- Basic metadata (name, description, stars, forks)
- Owner information (user/organization details)
- Languages and topics
- Repository settings and permissions
- Creation, update, and push timestamps

### Pull Requests
- PR metadata (title, body, state, author)
- Code changes (additions, deletions, files changed)
- Labels and milestones
- Review information
- Timeline data (created, merged, closed)

### Releases  
- Release metadata (name, tag, description)
- Publication dates and authors
- Pre-release and draft status
- Release assets and download counts

## 🏗️ Architecture

### Pipeline Design

```
GitHub GraphQL API → dlt Pipeline → DuckDB → Analytics
```

**Key Components:**

- **`pipeline.py`** - Core dlt pipeline with all resources and transformations
- **`run_pipeline.py`** - Configurable runner with monitoring and error handling
- **`GitHubCollector`** - API client with rate limiting and retry logic
- **Incremental Loading** - Automatically skips existing data

### Error Handling & Resilience

- **Automatic Retries** - Exponential backoff for transient failures
- **Rate Limit Management** - Intelligent waiting when limits are approached  
- **Graceful Degradation** - Continues processing when individual repositories fail
- **State Persistence** - Resumes from where it left off after interruptions

## 📈 Usage Examples

### Basic Data Collection

```python
from pipeline import github_source
import dlt

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name='cardano_analysis',
    destination='duckdb',
    dataset_name='cardano_data'
)

# Run collection
info = pipeline.run(github_source(
    search_term='cardano wallet',
    max_repos=100,
    min_stars=1
))

print(f"Collected: {info}")
```

### Analyzing Results

```python
import duckdb

# Connect to database
conn = duckdb.connect('cardano_analysis.duckdb', read_only=True)

# Top repositories by activity
top_repos = conn.execute("""
    SELECT 
        r.name_with_owner as repo,
        r.stargazer_count as stars,
        COUNT(pr.number) as total_prs,
        COUNT(rel.name) as total_releases
    FROM cardano_data.repositories r
    LEFT JOIN cardano_data.pull_requests pr ON r.name_with_owner = pr.repo  
    LEFT JOIN cardano_data.releases rel ON r.name_with_owner = rel.repo
    GROUP BY r.name_with_owner, r.stargazer_count
    ORDER BY total_prs DESC
    LIMIT 10
""").fetchall()

print("Top repositories by development activity:")
for repo, stars, prs, releases in top_repos:
    print(f"  {repo}: {stars}⭐ {prs} PRs, {releases} releases")
```

## 🔧 Advanced Features

### Custom Search Queries

The pipeline supports GitHub's full search syntax:

```bash
# Recent activity
python run_pipeline.py --search "cardano wallet pushed:>2024-01-01"

# Specific languages
python run_pipeline.py --search "cardano wallet language:typescript"

# Organization-specific
python run_pipeline.py --search "cardano wallet org:input-output-hk"

# Size filters
python run_pipeline.py --search "cardano wallet size:>1000"
```

### Monitoring & Logging

```bash
# Detailed logging to file
python run_pipeline.py --config cardano --log-level DEBUG --log-file logs/pipeline.log

# Monitor rate limits and performance
tail -f logs/pipeline.log | grep -E "(rate limit|completed|error)"
```

### Database Management

```python
import duckdb

# Check collection status
conn = duckdb.connect('github_cardano.duckdb')

# Repository counts
repo_count = conn.execute("SELECT COUNT(*) FROM github_data.repositories").fetchone()[0]
print(f"Total repositories: {repo_count}")

# PR statistics  
pr_stats = conn.execute("""
    SELECT 
        state,
        COUNT(*) as count
    FROM github_data.pull_requests 
    GROUP BY state
""").fetchall()

print("Pull request states:")
for state, count in pr_stats:
    print(f"  {state}: {count}")
```

## 🛠️ Development

### Installation for Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black pipeline.py run_pipeline.py

# Sort imports  
isort pipeline.py run_pipeline.py

# Type checking
mypy pipeline.py run_pipeline.py

# Run tests
pytest
```

### Project Structure

```
github-trend-insights/
├── pipeline.py              # Core dlt pipeline
├── run_pipeline.py          # Configurable runner
├── pyproject.toml          # Dependencies and configuration
├── .env.example            # Environment template
├── README.md               # This file
├── .gitignore              # Git ignore rules
└── logs/                   # Log files (created during runs)
```

## 📊 Dataset Statistics

Typical collection results for the Cardano wallet ecosystem:

- **~500 repositories** (complete ecosystem)
- **~25,000 pull requests** (with full metadata and bodies)
- **~4,000 releases** (with descriptions and assets)
- **~8,000 labeled PRs** (30%+ label coverage)
- **Complete development history** for all major wallets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[dlt](https://github.com/dlt-hub/dlt)** - Data load tool for modern data stack
- **[DuckDB](https://github.com/duckdb/duckdb)** - Fast analytical database
- **[GitHub GraphQL API](https://docs.github.com/en/graphql)** - GitHub's API v4

---

**Built with**: Python, dlt, DuckDB, GitHub GraphQL API  
**Author**: [jitsejan](https://github.com/jitsejan)  
**Dataset**: Complete Cardano wallet ecosystem