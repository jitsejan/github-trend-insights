#!/usr/bin/env python3
"""
GitHub Cardano Wallet Pipeline Runner

A configurable runner for the GitHub Cardano wallet ecosystem data pipeline.
Supports different configurations and provides detailed logging and monitoring.

Usage:
    python run_pipeline.py --config cardano
    python run_pipeline.py --search "cardano wallet" --max-repos 200
    python run_pipeline.py --help
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import dlt
from dotenv import load_dotenv

from pipeline import github_source

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration"""
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = getattr(logging, log_level.upper())
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

class PipelineRunner:
    """Pipeline runner with configuration management and monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def validate_environment(self):
        """Validate required environment variables"""
        
        github_token = os.environ.get('GITHUB_PAT')
        if not github_token:
            raise ValueError(
                "GITHUB_PAT environment variable is required. "
                "Please set your GitHub Personal Access Token in .env file"
            )
        
        # Validate token format (should start with ghp_ or classic tokens)
        if not (github_token.startswith('ghp_') or len(github_token) == 40):
            self.logger.warning(
                "GitHub token format looks unusual. Make sure it's a valid Personal Access Token"
            )
        
        self.logger.info("Environment validation passed")
        
    def create_pipeline(self) -> dlt.Pipeline:
        """Create and configure dlt pipeline"""
        
        pipeline_config = {
            'pipeline_name': self.config.get('pipeline_name', 'github_cardano'),
            'destination': self.config.get('destination', 'duckdb'),
            'dataset_name': self.config.get('dataset_name', 'github_data')
        }
        
        # For DuckDB, let dlt use its default database file naming
        # The database will be created as {pipeline_name}.duckdb automatically
        
        self.logger.info(f"Creating pipeline: {pipeline_config}")
        return dlt.pipeline(**pipeline_config)
    
    def run(self) -> Dict[str, Any]:
        """Run the pipeline with monitoring and error handling"""
        
        start_time = time.time()
        
        try:
            # Validate environment
            self.validate_environment()
            
            # Create pipeline
            pipeline = self.create_pipeline()
            
            # Configure source
            source_config = {
                'search_term': self.config.get('search_term', 'cardano wallet'),
                'max_repos': self.config.get('max_repos', 100),
                'include_archived': self.config.get('include_archived', False),
                'min_stars': self.config.get('min_stars', 0)
            }
            
            self.logger.info("Starting pipeline execution")
            self.logger.info(f"Configuration: {source_config}")
            
            # Run pipeline
            source = github_source(**source_config)
            info = pipeline.run(source)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Log results
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            self.logger.info(f"Pipeline info: {info}")
            
            return {
                'success': True,
                'execution_time': execution_time,
                'pipeline_info': info,
                'config': self.config
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Pipeline failed after {execution_time:.2f} seconds: {e}")
            
            return {
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'config': self.config
            }

def get_predefined_configs() -> Dict[str, Dict[str, Any]]:
    """Get predefined pipeline configurations"""
    
    return {
        'cardano': {
            'search_term': 'cardano wallet',
            'max_repos': 500,
            'include_archived': False,
            'min_stars': 0,
            'description': 'Complete Cardano wallet ecosystem'
        },
        'cardano-popular': {
            'search_term': 'cardano wallet',
            'max_repos': 100,
            'include_archived': False,
            'min_stars': 5,
            'description': 'Popular Cardano wallets (5+ stars)'
        },
        'cardano-active': {
            'search_term': 'cardano wallet pushed:>2023-01-01',
            'max_repos': 200,
            'include_archived': False,
            'min_stars': 0,
            'description': 'Recently active Cardano wallet projects'
        },
        'test': {
            'search_term': 'cardano wallet',
            'max_repos': 10,
            'include_archived': False,
            'min_stars': 0,
            'description': 'Small test run'
        }
    }

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    
    parser = argparse.ArgumentParser(
        description='GitHub Cardano Wallet Pipeline Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config cardano                    # Run full Cardano ecosystem collection
  %(prog)s --config test                       # Run small test
  %(prog)s --search "ada wallet" --max-repos 50  # Custom search
  
Predefined configurations:
  cardano        - Complete Cardano wallet ecosystem (500 repos)
  cardano-popular- Popular Cardano wallets (5+ stars, 100 repos)
  cardano-active - Recently active projects (200 repos)
  test           - Small test run (10 repos)
        """
    )
    
    # Configuration options
    parser.add_argument(
        '--config', '-c',
        choices=['cardano', 'cardano-popular', 'cardano-active', 'test'],
        help='Use predefined configuration'
    )
    
    # Custom parameters
    parser.add_argument(
        '--search', '-s',
        help='GitHub search term (e.g., "cardano wallet")'
    )
    
    parser.add_argument(
        '--max-repos', '-m',
        type=int,
        help='Maximum number of repositories to collect'
    )
    
    parser.add_argument(
        '--min-stars',
        type=int,
        default=0,
        help='Minimum star count filter'
    )
    
    parser.add_argument(
        '--include-archived',
        action='store_true',
        help='Include archived repositories'
    )
    
    # Pipeline configuration
    parser.add_argument(
        '--database',
        help='DuckDB database file path'
    )
    
    parser.add_argument(
        '--pipeline-name',
        default='github_cardano',
        help='Pipeline name for dlt'
    )
    
    parser.add_argument(
        '--dataset-name',
        default='github_data',
        help='Dataset name in destination'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path'
    )
    
    # Environment
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Environment file path'
    )
    
    return parser

def main():
    """Main entry point"""
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Load environment variables
    env_file = Path(args.env_file)
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment from {env_file}")
    else:
        print(f"Warning: Environment file {env_file} not found")
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # Build configuration
    config = {}
    
    # Use predefined config if specified
    if args.config:
        predefined_configs = get_predefined_configs()
        config = predefined_configs[args.config].copy()
        logger.info(f"Using predefined config '{args.config}': {config['description']}")
    
    # Override with command line arguments
    if args.search:
        config['search_term'] = args.search
    
    if args.max_repos:
        config['max_repos'] = args.max_repos
    
    if args.min_stars:
        config['min_stars'] = args.min_stars
    
    if args.include_archived:
        config['include_archived'] = True
    
    # Pipeline configuration
    if args.database:
        config['database_file'] = args.database
    
    config['pipeline_name'] = args.pipeline_name
    config['dataset_name'] = args.dataset_name
    
    # Set defaults if no config specified
    if not config.get('search_term'):
        config['search_term'] = 'cardano wallet'
    
    if not config.get('max_repos'):
        config['max_repos'] = 100
    
    # Display configuration
    logger.info("Pipeline Configuration:")
    for key, value in config.items():
        if key != 'description':
            logger.info(f"  {key}: {value}")
    
    # Create and run pipeline
    runner = PipelineRunner(config)
    result = runner.run()
    
    # Display results
    if result['success']:
        print(f"\n✅ Pipeline completed successfully!")
        print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
        
        if result['pipeline_info'].has_table('repositories'):
            print(f"📚 Repositories collected: {result['pipeline_info']['repositories'].get('job_metrics', {}).get('rows', 0)}")
        
        if result['pipeline_info'].has_table('pull_requests'):
            print(f"🔄 Pull requests collected: {result['pipeline_info']['pull_requests'].get('job_metrics', {}).get('rows', 0)}")
        
        if result['pipeline_info'].has_table('releases'):
            print(f"🚀 Releases collected: {result['pipeline_info']['releases'].get('job_metrics', {}).get('rows', 0)}")
        
    else:
        print(f"\n❌ Pipeline failed!")
        print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
        print(f"💥 Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()