"""Agents module initialization."""
from src.agents.prover import run_prover_agent
from src.agents.debunker import run_debunker_agent
from src.agents.judge import run_judge_agent

__all__ = [
    "run_prover_agent",
    "run_debunker_agent",
    "run_judge_agent",
]
