# CULTURE//BOUNTY

CULTURE//BOUNTY is a Qloo-grounded Cultural Scout Agent built for the Qloo Agentic Hackathon.

## What it does

A user gives the agent a brand and a campaign objective. The agent then:

1. **Resolve** — maps the brand to a Qloo entity.
2. **Explore** — traverses Qloo's taste graph across podcasts, artists, movies and destinations.
3. **Diversify** — runs a second podcast search with popularity capped at 0.80 to deliberately surface non-obvious candidates.
4. **Explain** — preserves Qloo explainability metadata with each recommendation.
5. **Select** — chooses a long-tail cultural bridge.
6. **Brief** — creates a fail-closed creator bounty brief for human approval.

## Why Qloo is essential

The product is not a generic LLM recommendation wrapper. Qloo is the cultural grounding layer.

Before BUILD, a live API gate was run against a frozen LLM-only baseline:

- Patagonia: normal 5/5 novel, long-tail 5/5 novel
- Aesop: normal 5/5 novel, long-tail 5/5 novel
- Liquid Death: normal 4/5 novel, long-tail 5/5 novel

The gate passed 3/3 brands in both normal and long-tail modes.

## Run locally

```bash
pip install -r requirements.txt
set QLOO_API_KEY=your_key_here
python app.py
```

Then open http://127.0.0.1:8088

If no server-side key is configured, the local UI allows a key to be entered for that request only. It is not written to disk.

## Deployment

A Render blueprint is included. Configure `QLOO_API_KEY` as a secret environment variable.

## Safety / payment boundary

The current bounty flow is intentionally fail-closed:

```
AUTHORIZE -> verify placement -> CAPTURE
                         \-> VOID
```

No real payment action is executed in this version.

## License

MIT.
