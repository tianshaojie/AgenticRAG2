"""Unit tests for AgentState enum and AgentContext dataclass."""

import pytest

from app.agent.protocols import AgentContext, AgentState


def test_agent_state_values():
    assert AgentState.IDLE == "IDLE"
    assert AgentState.DONE == "DONE"
    assert AgentState.ABSTAINING == "ABSTAINING"


def test_agent_context_defaults():
    ctx = AgentContext(query="What is RAG?")
    assert ctx.current_state == AgentState.IDLE
    assert ctx.step_count == 0
    assert ctx.abstained is False
    assert ctx.retrieval_results == []
    assert ctx.citations == []
    assert ctx.answer == ""
    assert ctx.trace_steps == []


def test_agent_context_step_count_incrementable():
    ctx = AgentContext(query="test")
    ctx.step_count += 1
    assert ctx.step_count == 1
