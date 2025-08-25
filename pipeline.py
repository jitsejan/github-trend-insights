#!/usr/bin/env python3
"""
GitHub Cardano Wallet Ecosystem Data Pipeline

A comprehensive dlt pipeline for collecting GitHub data from the Cardano wallet ecosystem.
Features incremental loading, error handling, rate limiting, and comprehensive data collection.

Usage:
    python pipeline.py
    
Or with custom parameters:
    from pipeline import github_source
    import dlt
    
    pipeline = dlt.pipeline('github_cardano', destination='duckdb', dataset_name='github_data')
    info = pipeline.run(github_source(search_term='cardano wallet', max_repos=100))
"""

import dlt
import requests
import time
import logging
import os
from datetime import datetime, timezone
from typing import Iterator, Dict, List, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass

class GitHubCollector:
    """GitHub API client with comprehensive error handling and rate limiting"""
    
    def __init__(self, token: str):
        self.token = token
        self.session = self._create_session()
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = None
        
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'CardanoWalletAnalytics/1.0'
        })
        
        return session
    
    def _check_rate_limit(self):
        """Check and handle rate limiting"""
        if self.rate_limit_remaining <= 10:
            if self.rate_limit_reset:
                sleep_time = max(0, self.rate_limit_reset - time.time() + 60)
                logger.warning(f"Rate limit low. Sleeping for {sleep_time:.0f} seconds")
                time.sleep(sleep_time)
    
    def _update_rate_limit(self, response: requests.Response):
        """Update rate limit info from response headers"""
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_timestamp = response.headers.get('X-RateLimit-Reset')
        if reset_timestamp:
            self.rate_limit_reset = int(reset_timestamp)
    
    def graphql_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL query with error handling"""
        self._check_rate_limit()
        
        url = "https://api.github.com/graphql"
        payload = {"query": query, "variables": variables}
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            self._update_rate_limit(response)
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    logger.error(f"GraphQL errors: {data['errors']}")
                    raise GitHubAPIError(f"GraphQL errors: {data['errors']}")
                return data
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                response.raise_for_status()
                
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            raise GitHubAPIError("Request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise GitHubAPIError(f"Request failed: {e}")

def get_existing_repos() -> set:
    """Get list of existing repositories from the database"""
    try:
        import duckdb
        import os
        
        # Try to connect to database file directly
        db_files = ['github_cardano.duckdb', 'github_cardano_test.duckdb']
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    conn = duckdb.connect(db_file, read_only=True)
                    result = conn.execute("SELECT name_with_owner FROM github_data.repositories").fetchall()
                    conn.close()
                    existing = {row[0] for row in result}
                    logger.info(f"Found {len(existing)} existing repositories in {db_file}")
                    return existing
                except Exception:
                    continue
        
        logger.info("No existing repositories table found - starting fresh")
        return set()
    except Exception as e:
        logger.warning(f"Could not check existing repositories: {e}")
        return set()

@dlt.source(name="github_cardano_ecosystem")
def github_source(
    search_term: str = "cardano wallet",
    max_repos: int = 500,
    include_archived: bool = False,
    min_stars: int = 0
):
    """
    dlt source for GitHub Cardano wallet ecosystem data
    
    Args:
        search_term: GitHub search query
        max_repos: Maximum repositories to collect
        include_archived: Include archived repositories
        min_stars: Minimum star count filter
    """
    github_token = os.environ.get('GITHUB_PAT')
    if not github_token:
        raise ValueError("GITHUB_PAT environment variable is required")
    
    collector = GitHubCollector(github_token)
    
    return [
        repositories(collector, search_term, max_repos, include_archived, min_stars),
        pull_requests(collector),
        releases(collector)
    ]

@dlt.resource(
    name="repositories",
    write_disposition="merge",
    primary_key="database_id"
)
def repositories(
    collector: GitHubCollector,
    search_term: str,
    max_repos: int,
    include_archived: bool,
    min_stars: int
) -> Iterator[Dict[str, Any]]:
    """Collect repository data with comprehensive metadata"""
    
    logger.info(f"Collecting repositories for: '{search_term}'")
    
    # Get existing repositories to skip
    existing_repos = get_existing_repos()
    logger.info(f"Found {len(existing_repos)} existing repositories - will skip duplicates")
    
    query = """
    query SearchRepositories($query: String!, $after: String) {
        search(query: $query, type: REPOSITORY, first: 50, after: $after) {
            repositoryCount
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                ... on Repository {
                    databaseId
                    id
                    nameWithOwner
                    name
                    description
                    url
                    homepageUrl
                    createdAt
                    updatedAt
                    pushedAt
                    stargazerCount
                    forkCount
                    diskUsage
                    primaryLanguage {
                        name
                        color
                    }
                    languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                        totalSize
                        edges {
                            size
                            node {
                                name
                                color
                            }
                        }
                    }
                    licenseInfo {
                        key
                        name
                        spdxId
                    }
                    repositoryTopics(first: 20) {
                        nodes {
                            topic {
                                name
                            }
                        }
                    }
                    owner {
                        login
                        ... on Organization {
                            name
                            description
                            websiteUrl
                            createdAt
                        }
                        ... on User {
                            name
                            bio
                            company
                            location
                            websiteUrl
                            createdAt
                        }
                    }
                    isArchived
                    isDisabled
                    isEmpty
                    isFork
                    isPrivate
                    hasIssuesEnabled
                    hasProjectsEnabled
                    hasWikiEnabled
                    hasDiscussionsEnabled
                    defaultBranchRef {
                        name
                    }
                }
            }
        }
        rateLimit {
            remaining
            resetAt
        }
    }
    """
    
    # Build search query
    search_query = search_term
    if not include_archived:
        search_query += " archived:false"
    if min_stars > 0:
        search_query += f" stars:>={min_stars}"
    
    variables = {"query": search_query, "after": None}
    collected_count = 0
    new_repos_count = 0
    
    while collected_count < max_repos:
        try:
            logger.info(f"Fetching repositories batch (collected: {collected_count}/{max_repos})")
            
            result = collector.graphql_query(query, variables)
            search_data = result["data"]["search"]
            
            if not search_data["nodes"]:
                logger.info("No more repositories found")
                break
            
            for repo in search_data["nodes"]:
                if collected_count >= max_repos:
                    break
                
                # Skip existing repositories
                if repo["nameWithOwner"] in existing_repos:
                    logger.debug(f"Skipping existing repo: {repo['nameWithOwner']}")
                    collected_count += 1
                    continue
                
                # Process repository data
                processed_repo = {
                    **repo,
                    "repo_database_id": repo["databaseId"],  # Add for FK relationships
                    "topics": [topic["topic"]["name"] for topic in repo.get("repositoryTopics", {}).get("nodes", [])],
                    "languages_data": repo.get("languages", {}),
                    "collected_at": datetime.now(timezone.utc).isoformat()
                }
                
                yield processed_repo
                new_repos_count += 1
                collected_count += 1
                
                logger.debug(f"Collected: {repo['nameWithOwner']} ({repo['stargazerCount']} stars)")
            
            # Check for next page
            page_info = search_data["pageInfo"]
            if not page_info["hasNextPage"]:
                logger.info("No more pages available")
                break
            
            variables["after"] = page_info["endCursor"]
            
            # Rate limiting pause
            time.sleep(1)
            
        except GitHubAPIError as e:
            logger.error(f"GitHub API error: {e}")
            if "rate limit" in str(e).lower():
                logger.info("Rate limit hit - waiting 60 seconds")
                time.sleep(60)
                continue
            else:
                raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    logger.info(f"Repository collection complete: {new_repos_count} new repos, {collected_count} total processed")

@dlt.resource(
    name="pull_requests",
    write_disposition="merge",
    primary_key="database_id"
)
def pull_requests(collector: GitHubCollector) -> Iterator[Dict[str, Any]]:
    """Collect pull requests for repositories with comprehensive metadata"""
    
    logger.info("Collecting pull requests for repositories")
    
    # Get repositories from database
    try:
        import duckdb
        import os
        
        db_files = ['github_cardano.duckdb', 'github_cardano_test.duckdb']
        repositories_list = []
        
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    conn = duckdb.connect(db_file, read_only=True)
                    result = conn.execute("""
                        SELECT name_with_owner, repo_database_id, stargazer_count 
                        FROM github_data.repositories 
                        ORDER BY stargazer_count DESC
                    """).fetchall()
                    conn.close()
                    repositories_list = list(result)
                    break
                except Exception:
                    continue
        
        if not repositories_list:
            logger.info("No repositories found - PRs will be collected on next run")
            return
            
    except Exception as e:
        logger.info(f"Could not load repositories: {e}")
        return
    
    if not repositories_list:
        logger.info("No repositories available for PR collection")
        return
    
    query = """
    query GetPullRequests($owner: String!, $name: String!, $after: String) {
        repository(owner: $owner, name: $name) {
            pullRequests(first: 100, after: $after, orderBy: {field: CREATED_AT, direction: DESC}) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    databaseId
                    number
                    title
                    body
                    bodyText
                    state
                    url
                    createdAt
                    updatedAt
                    closedAt
                    mergedAt
                    mergeable
                    additions
                    deletions
                    changedFiles
                    commits {
                        totalCount
                    }
                    author {
                        login
                        ... on User {
                            name
                            email
                            company
                            location
                        }
                    }
                    baseRefName
                    headRefName
                    labels(first: 20) {
                        nodes {
                            name
                            color
                            description
                        }
                    }
                    reviewRequests(first: 10) {
                        nodes {
                            requestedReviewer {
                                ... on User {
                                    login
                                    name
                                }
                            }
                        }
                    }
                    reviews(first: 10) {
                        nodes {
                            author {
                                login
                            }
                            state
                            createdAt
                        }
                    }
                    milestone {
                        title
                        state
                        dueOn
                    }
                    assignees(first: 10) {
                        nodes {
                            login
                            name
                        }
                    }
                }
            }
        }
        rateLimit {
            remaining
            resetAt
        }
    }
    """
    
    total_prs = 0
    
    for repo_name, repo_database_id, stars in repositories_list:
        try:
            owner, name = repo_name.split('/')
            logger.info(f"Collecting PRs for {repo_name} ({stars} stars)")
            
            variables = {"owner": owner, "name": name, "after": None}
            repo_pr_count = 0
            
            while True:
                try:
                    result = collector.graphql_query(query, variables)
                    repo_data = result["data"]["repository"]
                    
                    if not repo_data or not repo_data["pullRequests"]["nodes"]:
                        break
                    
                    for pr in repo_data["pullRequests"]["nodes"]:
                        # Process PR data
                        processed_pr = {
                            **pr,
                            "repo": repo_name,
                            "repo_database_id": repo_database_id,
                            "database_id": pr["databaseId"],
                            "author__login": pr.get("author", {}).get("login") if pr.get("author") else None,
                            "author__name": pr.get("author", {}).get("name") if pr.get("author") else None,
                            "author__email": pr.get("author", {}).get("email") if pr.get("author") else None,
                            "author__company": pr.get("author", {}).get("company") if pr.get("author") else None,
                            "author__location": pr.get("author", {}).get("location") if pr.get("author") else None,
                            "base_branch": pr.get("baseRefName"),
                            "head_branch": pr.get("headRefName"),
                            "commit_count": pr.get("commits", {}).get("totalCount", 0),
                            "labels_list": [label["name"] for label in pr.get("labels", {}).get("nodes", [])],
                            "labels_json": pr.get("labels", {}).get("nodes", []),
                            "milestone_title": pr.get("milestone", {}).get("title") if pr.get("milestone") else None,
                            "assignees_list": [assignee["login"] for assignee in pr.get("assignees", {}).get("nodes", [])],
                            "collected_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        yield processed_pr
                        repo_pr_count += 1
                        total_prs += 1
                    
                    # Check for next page
                    page_info = repo_data["pullRequests"]["pageInfo"]
                    if not page_info["hasNextPage"]:
                        break
                    
                    variables["after"] = page_info["endCursor"]
                    
                    # Rate limiting pause
                    time.sleep(0.5)
                    
                except GitHubAPIError as e:
                    logger.error(f"API error for {repo_name}: {e}")
                    if "rate limit" in str(e).lower():
                        logger.info("Rate limit hit - waiting 60 seconds")
                        time.sleep(60)
                        continue
                    else:
                        logger.warning(f"Skipping {repo_name} due to API error")
                        break
            
            logger.info(f"Collected {repo_pr_count} PRs from {repo_name}")
            
        except Exception as e:
            logger.error(f"Error processing {repo_name}: {e}")
            continue
    
    logger.info(f"Pull request collection complete: {total_prs} total PRs")

@dlt.resource(
    name="releases",
    write_disposition="merge", 
    primary_key="database_id"
)
def releases(collector: GitHubCollector) -> Iterator[Dict[str, Any]]:
    """Collect releases for repositories"""
    
    logger.info("Collecting releases for repositories")
    
    # Get repositories from database
    try:
        import duckdb
        import os
        
        db_files = ['github_cardano.duckdb', 'github_cardano_test.duckdb']
        repositories_list = []
        
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    conn = duckdb.connect(db_file, read_only=True)
                    result = conn.execute("""
                        SELECT name_with_owner, repo_database_id, stargazer_count 
                        FROM github_data.repositories 
                        ORDER BY stargazer_count DESC
                    """).fetchall()
                    conn.close()
                    repositories_list = list(result)
                    break
                except Exception:
                    continue
        
        if not repositories_list:
            logger.info("No repositories found - releases will be collected on next run")
            return
            
    except Exception as e:
        logger.info(f"Could not load repositories: {e}")
        return
    
    if not repositories_list:
        logger.info("No repositories available for release collection")
        return
    
    query = """
    query GetReleases($owner: String!, $name: String!, $after: String) {
        repository(owner: $owner, name: $name) {
            releases(first: 100, after: $after, orderBy: {field: CREATED_AT, direction: DESC}) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    databaseId
                    name
                    tagName
                    description
                    url
                    createdAt
                    publishedAt
                    updatedAt
                    isLatest
                    isPrerelease
                    isDraft
                    author {
                        login
                        ... on User {
                            name
                        }
                    }
                    releaseAssets(first: 10) {
                        nodes {
                            name
                            size
                            downloadCount
                            contentType
                            url
                        }
                    }
                }
            }
        }
        rateLimit {
            remaining
            resetAt
        }
    }
    """
    
    total_releases = 0
    
    for repo_name, repo_database_id, stars in repositories_list:
        try:
            owner, name = repo_name.split('/')
            logger.info(f"Collecting releases for {repo_name}")
            
            variables = {"owner": owner, "name": name, "after": None}
            repo_release_count = 0
            
            while True:
                try:
                    result = collector.graphql_query(query, variables)
                    repo_data = result["data"]["repository"]
                    
                    if not repo_data or not repo_data["releases"]["nodes"]:
                        break
                    
                    for release in repo_data["releases"]["nodes"]:
                        # Process release data
                        processed_release = {
                            **release,
                            "repo": repo_name,
                            "repo_database_id": repo_database_id,
                            "database_id": release["databaseId"],
                            "author__login": release.get("author", {}).get("login") if release.get("author") else None,
                            "author__name": release.get("author", {}).get("name") if release.get("author") else None,
                            "assets_count": len(release.get("releaseAssets", {}).get("nodes", [])),
                            "assets_data": release.get("releaseAssets", {}).get("nodes", []),
                            "collected_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        yield processed_release
                        repo_release_count += 1
                        total_releases += 1
                    
                    # Check for next page
                    page_info = repo_data["releases"]["pageInfo"]
                    if not page_info["hasNextPage"]:
                        break
                    
                    variables["after"] = page_info["endCursor"]
                    
                    # Rate limiting pause
                    time.sleep(0.5)
                    
                except GitHubAPIError as e:
                    logger.error(f"API error for {repo_name}: {e}")
                    if "rate limit" in str(e).lower():
                        logger.info("Rate limit hit - waiting 60 seconds")
                        time.sleep(60)
                        continue
                    else:
                        logger.warning(f"Skipping {repo_name} due to API error")
                        break
            
            if repo_release_count > 0:
                logger.info(f"Collected {repo_release_count} releases from {repo_name}")
                
        except Exception as e:
            logger.error(f"Error processing releases for {repo_name}: {e}")
            continue
    
    logger.info(f"Release collection complete: {total_releases} total releases")

if __name__ == "__main__":
    """Run the pipeline directly"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configuration
    SEARCH_TERM = "cardano wallet"
    MAX_REPOS = 100
    
    logger.info(f"Starting GitHub Cardano Wallet Pipeline")
    logger.info(f"Search term: '{SEARCH_TERM}'")
    logger.info(f"Max repositories: {MAX_REPOS}")
    
    # Create and run pipeline
    pipeline = dlt.pipeline(
        pipeline_name='github_cardano',
        destination='duckdb',
        dataset_name='github_data'
    )
    
    # Run source
    info = pipeline.run(
        github_source(
            search_term=SEARCH_TERM,
            max_repos=MAX_REPOS,
            include_archived=False,
            min_stars=0
        )
    )
    
    print(f"\nPipeline completed successfully!")
    print(f"Pipeline info: {info}")