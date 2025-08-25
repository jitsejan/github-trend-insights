"""Export dbt models to parquet files for sharing."""
import duckdb
import os
from pathlib import Path


def export_models_to_parquet():
    """Export key dbt models to parquet files."""
    
    # Connect to DuckDB database
    db_path = Path("github_cardano.duckdb")
    if not db_path.exists():
        print(f"Database {db_path} not found. Run the pipeline first.")
        return
        
    con = duckdb.connect(str(db_path))
    
    # Create exports directory
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    
    # Models to export
    models = [
        "stg_pull_requests",
        "stg_releases", 
        "feature_prs_monthly",
        "feature_releases_monthly",
        "feature_prs_lace_vs_top10",
        "feature_releases_lace_vs_top10",
        "median_feature_prs_lace_vs_top10",
        "median_releases_lace_vs_top10"
    ]
    
    print("Exporting models to parquet files...")
    
    for model in models:
        try:
            output_path = exports_dir / f"{model}.parquet"
            
            # Check if table exists
            tables = con.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            
            if model not in table_names:
                print(f"⚠️  Table {model} not found in database. Skipping.")
                continue
                
            # Export to parquet
            con.execute(f"COPY {model} TO '{output_path}' (FORMAT 'parquet')")
            
            # Get row count for confirmation
            count = con.execute(f"SELECT COUNT(*) FROM {model}").fetchone()[0]
            print(f"✅ Exported {model}: {count:,} rows -> {output_path}")
            
        except Exception as e:
            print(f"❌ Error exporting {model}: {e}")
    
    con.close()
    print(f"\n📁 Exports saved to: {exports_dir.absolute()}")


if __name__ == "__main__":
    export_models_to_parquet()