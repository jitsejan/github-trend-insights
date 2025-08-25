"""GitHub data pipeline using dlt."""
import dlt
import os
from typing import Optional, List
from connectors.github import repositories, pull_requests, releases, issues


def github_pipeline(
    repos: Optional[List[str]] = None,
    destination: str = "duckdb",
    dataset_name: str = "github_raw",
    max_prs_per_repo: Optional[int] = None,
    max_releases_per_repo: Optional[int] = None,
    max_issues_per_repo: Optional[int] = None
) -> None:
    """
    Run the complete GitHub data pipeline.
    
    Args:
        repos: List of repository names in "owner/repo" format
        destination: dlt destination (duckdb, s3, etc.)
        dataset_name: Name of the dataset/schema
        max_prs_per_repo: Maximum number of PRs to fetch per repo
        max_releases_per_repo: Maximum number of releases to fetch per repo  
        max_issues_per_repo: Maximum number of issues to fetch per repo
    """
    if not repos:
        repos = [
            "cardano-foundation/cardano-wallet",
            "input-output-hk/cardano-node",
            "input-output-hk/plutus",
            "Emurgo/cardano-serialization-lib",
            "input-output-hk/cardano-ledger",
            "input-output-hk/ouroboros-network",
        ]
    
    # Configure the pipeline
    pipeline = dlt.pipeline(
        pipeline_name="github_cardano",
        destination=destination,
        dataset_name=dataset_name,
        progress="log"
    )
    
    print(f"Running GitHub pipeline for {len(repos)} repositories...")
    print(f"Repositories: {repos}")
    
    # Create resources with the specified limits
    repo_resource = repositories(repos=repos)
    pr_resource = pull_requests(repos=repos, max_per_repo=max_prs_per_repo)
    release_resource = releases(repos=repos, max_per_repo=max_releases_per_repo) 
    issue_resource = issues(repos=repos, max_per_repo=max_issues_per_repo)
    
    # Run the pipeline
    info = pipeline.run([
        repo_resource,
        pr_resource, 
        release_resource,
        issue_resource
    ])
    
    print(f"Pipeline completed: {info}")
    return info


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run GitHub data pipeline")
    parser.add_argument(
        "--repos", 
        nargs="+", 
        help="Repository names in owner/repo format"
    )
    parser.add_argument(
        "--destination", 
        default="duckdb", 
        help="dlt destination"
    )
    parser.add_argument(
        "--dataset", 
        default="github_raw",
        help="Dataset name"
    )
    parser.add_argument(
        "--max-prs", 
        type=int,
        help="Maximum PRs per repository"
    )
    parser.add_argument(
        "--max-releases",
        type=int, 
        help="Maximum releases per repository"
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        help="Maximum issues per repository"
    )
    
    args = parser.parse_args()
    
    github_pipeline(
        repos=args.repos,
        destination=args.destination,
        dataset_name=args.dataset,
        max_prs_per_repo=args.max_prs,
        max_releases_per_repo=args.max_releases,
        max_issues_per_repo=args.max_issues
    )