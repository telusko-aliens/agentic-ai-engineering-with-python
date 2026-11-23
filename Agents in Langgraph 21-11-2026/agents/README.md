# Agents in LangGraph 21-11-2026

Agents in LangGraph: streaming, human approval, supervisor, handoffs and deep agents.

Class source code for the **Agentic AI Engineering with Python** course.
This project was started on 15-11 and continued in this session.

## Setup

```bash
uv sync
cp .env.example .env    # then add your own API key
```

## Files

Scripts that build a graph save its diagram as a `.png` next to them.
`streaming_modes.txt` lists the streaming modes covered in class.

- `1_agent.py`
- `2_agents_with_tools.py`
- `3_agent_with_multiple_tools.py`
- `4_agent_with_recursion.py`
- `5_agent_graph_as_tool.py`
- `6_agent_with_memory.py`
- `7_agent_streaming.py`
- `8_agent_streamming2.py`
- `9_agent_streaming_with_memory.py`
- `10_stream_values.py`
- `11_stream_debug.py`
- `12_stream_checkpoint.py`
- `13_stream_tasks.py`
- `14_agent_by_hand.py`
- `15_human_approval.py`
- `16_plan_and_execute.py`
- `17_multi_agent_supervisor.py`
- `18_supervisor_graph.py`
- `19_agents_handoff.py`
- `20_orchestration_workers.py`
- `21_deep_agent.py`

Run any file on its own:

```bash
uv run 1_agent.py
```
