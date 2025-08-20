import duckdb

# Connect to your dbt project's DuckDB
con = duckdb.connect("github_insights.duckdb")

# List of gold tables
tables = [
    "feature_prs_monthly",
    "feature_releases_monthly",
    "feature_prs_lace_vs_top10",
    "feature_releases_lace_vs_top10",
    "median_feature_prs_lace_vs_top10",
    "median_releases_lace_vs_top10"
]

# Export each to Parquet
for table in tables:
    con.execute(f"COPY main.{table} TO 'exports/{table}.parquet' (FORMAT 'parquet')")
