import pytest
from deepseek_cli.agents.base_agent import BaseAgent

class DummyAgent(BaseAgent):
    def build_prompt(self, *args, **kwargs):
        return [{'role': 'system', 'content': 'test'}]

def test_build_prompt():
    agent = DummyAgent('role', 'goal', 'backstory')
    prompts = agent.build_prompt()
    assert isinstance(prompts, list)
    assert prompts[0]['content'] == 'test' 