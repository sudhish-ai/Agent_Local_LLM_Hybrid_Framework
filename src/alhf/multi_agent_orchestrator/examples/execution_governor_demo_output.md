
Sudhish Singh@LAPTOP-I14VJ72B MINGW64 /d/AI_Projects/Agent_Local_LLM_Hybrid_Framework (feature/core-contracts-v0.1)
$ PYTHONPATH=src python src/alhf/multi_agent_orchestrator/examples/execution_governor_demo.py

========================================
Execution Governor V1 Demo
========================================

[Scenario 1] READY Workflow
Decision: ALLOW

[Scenario 2] FAILED Workflow
Decision: BLOCK

[Scenario 3] Retry Limit Exceeded
Decision: ESCALATE

[Scenario 4] Timeout Exceeded
Decision: ESCALATE

[Scenario 5] Full Governor Chain
Decision: ALLOW

========================================
Demo Completed
========================================

