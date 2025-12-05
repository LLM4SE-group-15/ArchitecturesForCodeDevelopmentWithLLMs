"""
Main Execution Script

Orchestrates the complete evaluation pipeline:
1. Loads tasks from dataset
2. Runs single-agent system
3. Runs multi-agent system
4. Evaluates results
5. Generates comparison report
"""

import argparse
from pathlib import Path
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="LLM Code Architecture Evaluation")
    parser.add_argument("--tasks-dir", type=str, default="tasks", help="Tasks directory")
    parser.add_argument("--output-dir", type=str, default="results", help="Output directory")
    parser.add_argument("--architecture", type=str, choices=["single", "multi", "both"], 
                        default="both", help="Which architecture to run")
    args = parser.parse_args()
    
    # Validate configuration
    Config.validate()
    logger.info("Configuration validated successfully")
    
    # TODO: Load tasks
    # TODO: Run single-agent evaluation
    # TODO: Run multi-agent evaluation
    # TODO: Generate comparison report
    
    logger.info("Evaluation complete")


if __name__ == "__main__":
    main()
