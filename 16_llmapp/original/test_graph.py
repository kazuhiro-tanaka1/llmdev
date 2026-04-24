# original/test_graph.py
from original.graph import run_chat

def test_run_chat():
    response = run_chat("こんにちは")
    assert isinstance(response, str)