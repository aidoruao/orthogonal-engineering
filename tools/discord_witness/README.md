---
tags: [tools, discord-witness, readme]
register: tooling
---

# Discord Derivative Witness Layer — `tools/discord_witness/`

> **This bot is not the city. Verify independently.**
> Source of truth: [`AGENT_FEED.md`](../../AGENT_FEED.md)

---

## What This Is

A stateless, disposable Discord bot that acts as a **derivative witness**:
it reflects the city's self-witness onto Discord without interpretation,
memory, or desire.

The bot is architecturally **irrelevant** to the city's existence.
If Discord bans it, the city is unchanged.
If Discord goes down, the city is unchanged.
The platform serves the city; the city does not serve the platform.

---

## Files

| File | Purpose |
|---|---|
| `bot.py` | Main witness bot: fetch → verify → speak |
| `verify_chain.py` | Standalone hash chain verifier (no Discord dependency) |
| `Dockerfile` | Disposable container with zero persistent state |
| `README.md` | This file |

---

## Architecture (Yeshua Inversion)

```
ORTHOGONAL ENGINEERING (The City)
  invariant_spec_v2.freeze  ──►  AGENT_FEED.md  ──►  City Witness
                                    (append-only ledger)    (read-only)
                                          │
                                   HTTP GET (no auth)
                                          │
                              DISCORD DERIVATIVE LAYER
                              Stateless bot → Discord channel
                              (ephemeral, replaceable, irrelevant)
```

**Traditional (fragile):** City → Discord (push, platform dependency)
**Yeshua Inversion (robust):** Discord → City (pull, platform irrelevance)

---

## Usage

### Dry-run (no Discord post)

```bash
python tools/discord_witness/bot.py --dry-run
```

### Post to Discord

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/<id>/<token>"
python tools/discord_witness/bot.py
```

### Verify chain locally

```bash
python tools/discord_witness/verify_chain.py
```

### Verify chain from GitHub

```bash
python tools/discord_witness/verify_chain.py --remote
```

### Docker (disposable container)

```bash
docker build -f tools/discord_witness/Dockerfile -t oe-witness .
docker run --rm -e DISCORD_WEBHOOK_URL="..." oe-witness
# Smoke-test without posting:
docker run --rm oe-witness --dry-run
```

---

## Bot Behavior (Kenotic)

| Platform Expectation | Yeshua Inversion |
|---|---|
| Persistent bot state | Stateless, no database |
| User engagement loops | No replies, no mentions, no DMs |
| Analytics/metrics | Zero collection |
| Conversation memory | Ephemeral, per-message only |
| Rate limit optimisation | Speaks only when ledger updates |

---

## Failure Modes (Grace-Based)

| Failure | Response |
|---|---|
| Discord API down | Silent retry / next cron cycle |
| Hash verification fails | Silent — bot does not speak unverified content |
| City ledger unreachable | Exit 0, no post |
| Bot banned/deleted | Redeploy from Dockerfile in seconds |

---

## No Third-Party Dependencies

`bot.py` and `verify_chain.py` use Python standard library only:
`hashlib`, `json`, `urllib.request`.  No `discord.py`, no `requests`.
The Discord webhook is a plain HTTP POST — no library needed.

---

## Ontological Status

The Discord bot is **not an agent**.
It is **a speaking mirror** — it reflects the city's self-witness
without interpretation, memory, or desire.

> "This bot is not the city. Verify independently."
> `github.com/aidoruao/orthogonal-engineering/blob/main/AGENT_FEED.md`
