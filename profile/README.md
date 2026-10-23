# The Code Foundry

Code is the lifeline of productivity.

Tools for running AI agents and local models on your own hardware: our own projects, and forks of open-source
projects extended where we needed more. Every fork has a `tcf.md` listing its changes versus the original repo.

## Projects

| repo | what |
|---|---|
| [kv-chunk-fs](https://github.com/the-code-foundry/kv-chunk-fs) | A content-addressed, deduplicating FUSE filesystem for llama.cpp KV-cache snapshots: transparent disk persistence with fast sequential restore |

## Forks

| repo | original | what the fork adds |
|---|---|---|
| [plane-mcp-server-ce](https://github.com/the-code-foundry/plane-mcp-server-ce) | [windyboy/plane-mcp-server-ce](https://github.com/windyboy/plane-mcp-server-ce) | MCP server for self-hosted Plane Community Edition; page content updates that reach Plane's editor ([changes](https://github.com/the-code-foundry/plane-mcp-server-ce/blob/main-ce/tcf.md)) |
| [local-llm-kv-cache](https://github.com/the-code-foundry/local-llm-kv-cache) | [gbuisson/local-llm-kv-cache](https://github.com/gbuisson/local-llm-kv-cache) | Disk-backed prefix and session KV-cache proxy for local coding agents with llama.cpp; per-request cache controls ([changes](https://github.com/the-code-foundry/local-llm-kv-cache/blob/HEAD/tcf.md)) |
| [Android-MCP-Full-Controll](https://github.com/the-code-foundry/Android-MCP-Full-Controll) | [CursorTouch/Android-MCP](https://github.com/CursorTouch/Android-MCP) | MCP server for Android devices; full device control: `Shell`, `Call` (the whole uiautomator2 API) and exclusive `Session` leases ([changes](https://github.com/the-code-foundry/Android-MCP-Full-Controll/blob/HEAD/tcf.md)) |

## Activity

![Contributions to The Code Foundry repos in the last year](./activity-graph.svg)

Pull requests are welcome.
