# GitHub Cardano Wallet Ecosystem Insights

A comprehensive data collection and analysis pipeline for the entire Cardano wallet ecosystem on GitHub.

## 🎯 Project Overview

This project collects and analyzes development data from all cardano wallet repositories on GitHub, providing insights into the ecosystem's activity, trends, and key players.

### 📊 Dataset Stats
- **389 repositories** (complete cardano wallet ecosystem)
- **24,714 pull requests** (with full bodies, labels, and metadata)
- **3,734 releases** (with descriptions)
- **7,617 labeled PRs** (30.8% label coverage)
- **Complete development history** for major wallets

## 🏗️ Architecture

Built using modern data engineering patterns with **dlt (data load tool)** for ingestion and **dbt** for analytics:

```
GitHub GraphQL API → DLT Pipeline → DuckDB → dbt Models → Analytics & Export
                                      ↓
                              S3 V3 Parquet → dbt Direct Access
```

### Key Components
- **`pipeline.py`** - Core dlt data collection pipeline with incremental updates
- **`run_pipeline.py`** - Pipeline runner with configurable parameters
- **`github_ingestion.duckdb`** - Main database with all collected data
- **`github_insights/`** - **dbt project** for analytics and transformations
- **`analysis/`** - Data analysis and visualization scripts
- **`scripts/`** - Utility scripts for maintenance and inspection

### dbt Analytics Layer
- **Bronze**: Raw data from S3 V3 parquet (repository data with PR classifications)
- **Silver**: Cleaned pull requests and releases data
- **Gold**: Business logic models for feature tracking and ecosystem analysis

## 🚀 Quick Start

### Prerequisites
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repo-url>
cd github-trend-insights
uv sync
```

### Environment Setup
Create `.env` file:
```bash
GITHUB_PAT=your_github_personal_access_token
```

### Run Data Collection
```bash
# Verify pipeline setup
python utils/verify_pipeline.py

# Collect data (incremental - skips existing repos)
python run_pipeline.py

# Or collect specific batch
python -c "
from pipeline import github_source
import dlt

pipeline = dlt.pipeline('github_ingestion', destination='duckdb', dataset_name='github_data')
info = pipeline.run(github_source(search_term='cardano wallet', max_repos=50))
print(info)
"
```

## 📊 Data Analysis

### dbt Analytics (Recommended)
```bash
# Navigate to dbt project
cd github_insights

# Run dbt models
dbt run

# Run specific model
dbt run --select feature_prs_monthly

# Generate docs
dbt docs generate && dbt docs serve
```

### Quick Database Inspection
```bash
python scripts/test_db_access.py
```

### Load Data with Pandas
```python
import json
import pandas as pd

# Load from exported JSON
with open('archive/datasets/cardano_wallet_clean_data.json', 'r') as f:
    data = json.load(f)

repos_df = pd.DataFrame(data['repositories'])
prs_df = pd.DataFrame(data['pull_requests'])
releases_df = pd.DataFrame(data['releases'])

# Join data
combined = repos_df.merge(
    prs_df.groupby('repo').agg({
        'number': 'count',
        'additions': 'sum',
        'deletions': 'sum'
    }).rename(columns={'number': 'total_prs'}),
    left_on='name_with_owner',
    right_index=True,
    how='left'
)
```

### Direct DuckDB Queries
```python
import duckdb

conn = duckdb.connect('github_ingestion.duckdb', read_only=True)

# Top repositories by development activity
top_repos = conn.execute("""
    SELECT 
        r.name_with_owner as repo,
        r.stargazer_count as stars,
        COUNT(pr.number) as total_prs,
        COUNT(rel.name) as total_releases
    FROM github_data.repositories r
    LEFT JOIN github_data.pull_requests pr ON r.name_with_owner = pr.repo
    LEFT JOIN github_data.releases rel ON r.name_with_owner = rel.repo
    GROUP BY r.name_with_owner, r.stargazer_count
    ORDER BY total_prs DESC
    LIMIT 10
""").fetchall()
```

## 🏆 Key Findings

### Top Repositories by Development Activity
1. **cardano-foundation/cardano-wallet**: 4,079 PRs (805 ⭐)
2. **Emurgo/yoroi-frontend**: 3,811 PRs (338 ⭐)
3. **Emurgo/yoroi**: 3,713 PRs (169 ⭐)
4. **input-output-hk/lace**: 1,703 PRs (31 ⭐)
5. **input-output-hk/cardano-js-sdk**: 1,364 PRs (228 ⭐)

### Ecosystem Insights
- **Main wallet implementation** (cardano-foundation/cardano-wallet) leads in development activity
- **Browser/web wallets** (Yoroi, Lace) show high activity
- **SDK projects** enable broader ecosystem development
- **Active development** across multiple organizations (IOG, Emurgo, Cardano Foundation)

## 🔧 Advanced Features

### Incremental Collection
The pipeline automatically skips existing repositories and appends new data:

```python
# Pipeline handles duplicates automatically
existing_repos = get_existing_repos()  # Checks database
# Only processes new repositories
```

### Rate Limiting & Error Handling
- Automatic retry logic with exponential backoff
- GitHub GraphQL API rate limiting
- Comprehensive error handling for network issues

### Extended Collection
For comprehensive data beyond API limits:
- Pagination strategies to break through 1,000 PR limits
- Multiple collection approaches (GraphQL + REST API)
- Data merging and deduplication

## 📁 Project Structure

```
github-trend-insights/
├── README.md                 # This file
├── pipeline.py              # Core DLT pipeline (consolidated with all improvements)
├── run_pipeline.py          # Pipeline runner
├── github_ingestion.duckdb  # Main database
├── pyproject.toml          # Python dependencies
├── github_insights/          # 🆕 dbt Analytics Project
│   ├── dbt_project.yml      # dbt configuration
│   ├── models/              # dbt transformation models
│   │   ├── bronze/          # Raw data access (S3 V3 parquet)
│   │   ├── silver/          # Cleaned data (PRs, releases)
│   │   └── gold/            # Business logic (feature analysis)
│   ├── analyses/            # dbt analysis queries
│   ├── tests/               # Data quality tests
│   └── target/              # Generated artifacts
├── data/                   # Generated datasets
│   └── cardano_wallet_ecosystem_complete.json  # Complete dataset export
├── utils/                  # Utility scripts
│   ├── verify_pipeline.py  # Pipeline verification
│   ├── incremental_labels_collection.py  # Advanced labels collection
│   └── migrate_add_missing_fields.py     # Database migration tools
├── examples/               # Usage examples
│   ├── basic_analysis.py   # DuckDB analysis examples
│   └── pandas_examples.py  # Pandas usage examples
├── scripts/                # Database utilities
│   ├── test_db_access.py   # Database inspection
│   ├── compare_top_repos.py # Repository comparison
│   └── merge_databases.py  # Database utilities
├── analysis/               # Advanced analysis scripts
├── archive/                # Historical data and backups
└── PROJECT_SUMMARY.md      # Detailed project summary
```

## 🌐 Data Sharing

Complete dataset available on S3:
- **Clean JSON**: `s3://tech-intelligence-data-new/share/cardano_wallet_clean_data_*.json`
- **Raw format**: Ready for pandas, analysis tools, and BI platforms

## 🛠️ Development

### Adding New Analysis
1. Create script in `analysis/`
2. Use either DuckDB connection or pandas DataFrames
3. Follow existing patterns for data access

### Extending Data Collection
1. Modify `pipeline.py` source functions
2. Add new resources following dlt patterns
3. Test with small batches first

### Performance Notes
- DuckDB handles 20k+ records efficiently
- JSON exports suitable for datasets up to ~50MB
- Use database queries for large-scale analysis

## 📈 Future Enhancements

- **Time-series analysis** of development trends
- **Network analysis** of contributor relationships
- **Technology stack analysis** from repository languages
- **Automated reporting** and dashboard generation
- **Real-time updates** with scheduled pipeline runs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add analysis or pipeline improvements
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Built with**: Python, dlt, dbt, DuckDB, GitHub GraphQL API, pandas
**Dataset**: Complete Cardano wallet ecosystem (389 repos, 20k+ PRs, 3k+ releases)
**Analytics**: Modern data stack with Bronze/Silver/Gold medallion architecture
