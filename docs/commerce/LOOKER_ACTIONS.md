# Looker Actions Orchestration

This connects Looker to the Chimera org so KPI triggers can launch workflows.

## Endpoint
```
POST https://youtube-ai-backend-lenljbhrqq-uc.a.run.app/api/looker/trigger
```

## Authentication (optional)
Set `LOOKER_ACTION_TOKEN` in the backend environment and send it as:
```
X-Looker-Token: <token>
```

## Execution mode
- `LOOKER_ACTION_MODE=execute` (default): triggers the Chimera workflow.
- `LOOKER_ACTION_MODE=queue`: writes to `logs/looker_actions_queue.jsonl`.

## Payload (example)
Use the payload format in `profit_os_execution_pack/autonomax/api_trigger.json`.

## Test
```bash
python3 scripts/looker_action_trigger.py
```

## Notes
- Use this for KPI‑based triggers (churn, sales spike, refund spike).
- Workflow routing defaults to `operations` unless the workflow id contains
  `sales` or `support`.
