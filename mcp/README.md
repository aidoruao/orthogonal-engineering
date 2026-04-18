# MCP — Model Context Protocol Integration

This directory contains MCP (Model Context Protocol) configuration files for the Orthogonal Engineering repository.

## What is MCP?

Model Context Protocol (MCP) is a standard interface that allows AI agents to discover and invoke tools exposed by a server. Supported clients include:

- Claude Desktop (Anthropic)
- Cursor IDE (with MCP plugin)
- Cline (VS Code extension)
- Continue.dev (with MCP support)

## Files

| File | Purpose |
|------|---------|
| `oe-basic.mcp.json` | MCP server descriptor — lists available tool endpoints and resource files |
| `orthogonal_mcp_server.py` | Existing MCP server implementation (demo protocol) |
| `demo_protocol_fix.py` | Protocol fix utilities |

## Using with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "orthogonal-engineering": {
      "command": "python",
      "args": ["mcp/orthogonal_mcp_server.py"],
      "cwd": "/path/to/orthogonal-engineering"
    }
  }
}
```

## Using with Cursor

Add to `.cursor/mcp.json`:

```json
{
  "servers": {
    "orthogonal-engineering": {
      "command": "python mcp/orthogonal_mcp_server.py",
      "descriptor": "mcp/oe-basic.mcp.json"
    }
  }
}
```

## Available Tools

See `oe-basic.mcp.json` for the full list. Key tools:

| Tool | Description |
|------|-------------|
| `run_popperian_audit` | Run Popperian audit; returns JSON pass/fail per domain |
| `run_health_check` | Run agent health check; returns 9 check results |
| `verify_feed_integrity` | Verify AGENT_FEED.md chain integrity |
| `query_standards` | Query STANDARDS_REGISTRY.json by scope or category |
| `estimate_tokens` | Estimate token cost of reading a path |
| `onboard_agent` | Get onboarding context for a specific agent type |
| `since_last_session` | Report changes since a feed row or commit |

## Standards Reference

This MCP integration is governed by `T3-001` through `T3-005` and `T5-004` in `STANDARDS_REGISTRY.json`.

## Falsifies If

This directory is invalid if `oe-basic.mcp.json` is missing, not valid JSON, or contains fewer than 5 tool definitions.
