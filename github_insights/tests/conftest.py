"""
Pytest configuration and shared fixtures for cardano-insights GitHub tests.
"""
import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Set up test environment variables and cleanup."""
    # Set test environment
    os.environ["TESTING"] = "1"
    
    yield
    
    # Cleanup test databases after all tests
    test_db_patterns = ["*test*.duckdb", "github_test.duckdb", "test_*.duckdb"]
    for pattern in test_db_patterns:
        for db_file in Path(".").glob(pattern):
            if db_file.exists():
                db_file.unlink()


# Parametrized fixtures for different repository scenarios
@pytest.fixture(params=[
    ["cardano-foundation/cardano-wallet"],
    ["input-output-hk/cardano-node"],
    ["cardano-foundation/cardano-wallet", "input-output-hk/plutus"]
])
def sample_repos(request):
    """Parametrized sample repository lists for testing different scenarios."""
    return request.param


@pytest.fixture(params=[
    {
        "id": 1,
        "number": 1,
        "title": "Fix bug in wallet component", 
        "body": "This PR fixes a critical bug in the wallet component",
        "state": "closed",
        "user": {"login": "test-dev"},
        "base": {"ref": "master"},
        "head": {"ref": "fix-wallet-bug"},
        "labels": [{"name": "bug"}, {"name": "wallet"}],
        "html_url": "https://github.com/test/repo/pull/1",
        "additions": 10,
        "deletions": 5,
        "changed_files": 2,
        "commits": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "closed_at": "2024-01-02T00:00:00Z",
        "merged_at": "2024-01-02T00:00:00Z"
    },
    {
        "id": 2,
        "number": 2,
        "title": "Add new feature for staking",
        "body": "Implements new staking functionality",
        "state": "open",
        "user": {"login": "feature-dev"},
        "base": {"ref": "main"},
        "head": {"ref": "add-staking-feature"},
        "labels": [{"name": "feature"}, {"name": "staking"}],
        "html_url": "https://github.com/test/repo/pull/2",
        "additions": 100,
        "deletions": 20,
        "changed_files": 8,
        "commits": 5,
        "created_at": "2024-02-01T00:00:00Z",
        "closed_at": None,
        "merged_at": None
    },
    {
        "id": 3,
        "number": 3,
        "title": "Refactor authentication module",
        "body": "Clean up and refactor the authentication code",
        "state": "merged",
        "user": {"login": "cleanup-dev"},
        "base": {"ref": "develop"},
        "head": {"ref": "refactor-auth"},
        "labels": [{"name": "refactor"}, {"name": "cleanup"}],
        "html_url": "https://github.com/test/repo/pull/3",
        "additions": 50,
        "deletions": 75,
        "changed_files": 4,
        "commits": 3,
        "created_at": "2024-03-01T00:00:00Z",
        "closed_at": "2024-03-05T00:00:00Z",
        "merged_at": "2024-03-05T00:00:00Z"
    }
])
def sample_pull_request(request):
    """Parametrized sample pull request data covering different scenarios."""
    return request.param


@pytest.fixture(params=[
    {
        "id": 1,
        "tag_name": "v1.0.0",
        "name": "Major Release v1.0.0",
        "body": "First major release with wallet functionality",
        "draft": False,
        "prerelease": False,
        "author": {"login": "release-manager"},
        "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
        "published_at": "2024-01-15T00:00:00Z",
        "created_at": "2024-01-10T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z"
    },
    {
        "id": 2,
        "tag_name": "v1.1.0-beta",
        "name": "Beta Release v1.1.0",
        "body": "Beta release with new staking features",
        "draft": False,
        "prerelease": True,
        "author": {"login": "beta-manager"},
        "html_url": "https://github.com/test/repo/releases/tag/v1.1.0-beta",
        "published_at": "2024-02-15T00:00:00Z",
        "created_at": "2024-02-10T00:00:00Z",
        "updated_at": "2024-02-15T00:00:00Z"
    }
])
def sample_release(request):
    """Parametrized sample release data covering different scenarios."""
    return request.param


@pytest.fixture(params=["bug fix", "feature", "refactor", "test", "documentation"])
def feature_classification(request):
    """Parametrized fixture for testing different feature classifications."""
    return request.param


@pytest.fixture(params=[
    {"pipeline_name": "test_github_pipeline_a", "dataset_name": "test_github_dataset_a"},
    {"pipeline_name": "test_github_pipeline_b", "dataset_name": "test_github_dataset_b"}
])
def pipeline_config(request):
    """Parametrized pipeline configuration for testing different setups."""
    return request.param


@pytest.fixture
def bug_fix_pr():
    """Specific fixture for bug fix pull request."""
    return {
        "id": 100,
        "number": 100,
        "title": "Fix critical security vulnerability",
        "body": "Patches a security issue in authentication",
        "state": "merged",
        "user": {"login": "security-team"},
        "labels": [{"name": "security"}, {"name": "bug"}],
        "html_url": "https://github.com/test/repo/pull/100",
        "repository_full_name": "test/repo",
        "fetched_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def feature_pr():
    """Specific fixture for feature pull request."""
    return {
        "id": 200,
        "number": 200,
        "title": "Implement new dashboard feature",
        "body": "Adds comprehensive dashboard with metrics",
        "state": "open",
        "user": {"login": "frontend-team"},
        "labels": [{"name": "feature"}, {"name": "frontend"}],
        "html_url": "https://github.com/test/repo/pull/200",
        "repository_full_name": "test/repo",
        "fetched_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def major_release():
    """Specific fixture for major release."""
    return {
        "id": 300,
        "tag_name": "v2.0.0",
        "name": "Major Release v2.0.0",
        "body": "Breaking changes and new architecture",
        "draft": False,
        "prerelease": False,
        "author": {"login": "architect"},
        "repository_full_name": "test/repo",
        "fetched_at": "2024-01-01T00:00:00Z"
    }