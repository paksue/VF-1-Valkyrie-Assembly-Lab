# VF-1J Valkyrie — Codex operating contract

## Primary objective
Reconstruct the **1982 TV-series VF-1J Hikaru Ichijo** Valkyrie using editable Blender geometry and a coherent Fighter / GERWALK / Battroid rig. Accuracy is evidence-based, not a judgement from one attractive screenshot.

## Hard rules
- Never replace the existing `dist/assets/vf1-valkyrie.glb`, modify published `dist/` assets, or merge to `main` without explicit user approval.
- Work in small, named assemblies. First milestone: Fighter-mode fuselage/nose/canopy blockout. Do not detail every part before validating silhouette.
- Always preserve an editable `.blend` and the scripts that generated it. Exported GLB is a deliverable, not the source of truth.
- Keep one consistent mesh and rig across all three transformations. Never disguise a failing transformation by swapping whole models between modes.
- Each geometry change must be followed by fixed-camera renders and a machine-readable metrics report. Review the **worst-matching** angle, not just the best one.
- Never say "accurate", "validated", "ready" or assign an accuracy percentage until the corresponding comparison artifacts exist.
- Do not auto-download or commit third-party copyrighted reference images. Store source links, descriptions, perspective and provenance in `references/manifest.json`; reference masks may be created for local analysis.
- Do not use unreviewed generated 3D assets as geometric ground truth.
- Avoid paid services/API calls or external asset services unless the user explicitly authorizes their cost.
- Limit Blender MCP's access to approved project directories. Prefer a least-privilege Windows account and local-only Blender socket tunnel.
- MCP telemetry must not be assumed disabled; check consent before running if privacy matters.

## Evidence-based build/observe/repair loop
1. Read `docs/GOAL.md`, `qa/README.md`, and the reference manifest. Identify the exact assembly and canonical viewpoints.
2. Check Blender MCP connectivity and the current .blend before edits. Save a baseline and/or use a feature branch.
3. Build or modify only one assembly or tightly related group.
4. Run `qa/render_blender.py` on the saved scene to generate 5 orthographic/perspective angles plus `metrics.json`.
5. Where a **registered, same-camera** ground truth silhouette mask exists, run `qa/compare_masks.py`; inspect the overlay and numerical result.
6. Produce a short defect list sorted by geometric importance; choose the largest defect and fix it.
7. Rerender; record before/after IoU and bounding boxes, make sure other angles do not regress.
8. Save the approved checkpoint, update the log, and repeat. Escalate inconsistent drawings and impossible physical constraints instead of inventing correctness.

## Milestone acceptance
- Model is dimensionally scaled only if a documented and verified reference convention has been applied; current repo units are arbitrary.
- All camera orientations must be documented; changing camera angle to get a prettier match is not a valid improvement.
- Fighter passes top/side/front silhouette and landmark reviews before GERWALK and Battroid are developed.
- Subsequent milestones validate rig movement and intersections **over intermediate frames**, not just at endpoint poses.
- The final exported GLB must load in the existing Three.js website, with transform/explode/reassemble/export checked independently.
- When a visual comparison cannot be run, report "not evaluated" rather than a guessed score.

## Commands
- Headless renders: `blender --background --python qa/render_blender.py -- --input path/to/model.blend --output qa/runs/baseline`
- Silhouette comparison (requires Pillow): `python qa/compare_masks.py --reference references/local/masks/top.png --render qa/runs/baseline/top.png --output qa/runs/baseline/top_overlay.png`

See `qa/README.md` for prerequisites and coordinate conventions.
