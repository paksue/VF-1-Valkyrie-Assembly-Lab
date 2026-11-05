# Verification status — 2026-11-05

## Observed, not inferred
- Connected to Omarchy DevSpace workspace at \`/home/pakyinli/Projects\` (resolved path \`/data/pakyinli/Projects\`).
- Discovered local prior work in \`valkyrie_blender/\`: build checkpoints A–L2, \`qa_L2.py\`, and an **unfinished independent N1 fighter blockout** in \`rebuild_N1.py\`. This folder was **not** a checkout of the GitHub website repository.
- At inspection, loopback listeners existed on Omarchy \`127.0.0.1:9876\` and \`127.0.0.1:8000\`. **Socket listeners alone do not prove live Blender MCP requests work.**
- A diagnostic invocation of \`bridge_runner.py status\` under system Python failed with \`ModuleNotFoundError: mcp\`, because the bridge requires the dedicated \`blender_mcp/mcp\` uv environment. This is an invocation error, **not evidence that Blender itself is disconnected**.
- The DevSpace session subsequently became unavailable/terminated before a valid uv-managed MCP request or Blender render could be executed.
- GitHub main's currently deployed \`dist/assets/vf1-valkyrie.glb\` has **not been replaced**.

## Status by gate
| Gate | Status | Evidence still required |
| --- | --- | --- |
| M0: Omarchy workspace reachable | Observed | Repeat when session restored |
| M0: Blender MCP request succeeds | Not verified | \`uv --directory /home/pakyinli/Projects/blender_mcp/mcp run python /home/pakyinli/Projects/valkyrie_blender/bridge_runner.py status\` plus successful response |
| M1: New Fighter blockout built | Not verified | Run independent N1 script in isolated background Blender, inspect log/BLEND |
| M1: Four rendered comparison views | Not verified | 4 beauty PNGs + 4 masks + manifest.json |
| M1: Reference registration | Blocked | Select lawful/usable orthographic images, align reference masks by view/scale |
| M1: Improved visual fidelity | Not verified | Compare before/after quantitative metrics and human view review |

## Next reproducible action
First restore DevSpace's session, then verify a read-only Blender status request in the correct \`uv\` environment. **Do not execute N1 build against the interactive Blender scene.** In a separate background Blender process, validate the unfinished N1 script before generating comparison renders. Record exact artifact names and timestamps.

This document deliberately contains no unsupported "passed" accuracy rating.
