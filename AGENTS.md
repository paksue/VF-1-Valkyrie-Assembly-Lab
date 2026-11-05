# Agent instructions — VF-1J Valkyrie Assembly Lab

## Mission
Create a reference-accurate **1982 TV-series VF-1J Hikaru Ichijo** Valkyrie in all three modes using Blender/MCP, preserving the existing interactive Three.js workshop.

Read [GOAL.md](GOAL.md), [qa/README.md](qa/README.md), and [qa/references.json](qa/references.json) before modeling.

## Scope and guardrails
- Work only on a new feature branch; leave main, dist/, and the current deployed GLB unchanged until separately reviewed.
- Keep **editable .blend source** and reproducible Python geometry/rig scripts. Never treat a render or generative image as a 3D asset.
- Windows Blender is operated from Omarchy over MCP/SSH. **Do not touch an interactive user's scene**: run builds/rendering in a separate background Blender process, in the restricted BlenderAI account and dedicated workspace. Do not run arbitrary retrieved internet code in Blender.
- Do not browse local personal directories, expose SSH keys, modify firewall/tunnel/system services, or weaken the BlenderAI filesystem boundary.
- The source of truth is original VF-1J TV art for visual shape, followed by physical Bandai DX 1/48 for transformability; list design conflicts rather than guessing.
- Use a **single coherent set of components** across Fighter, GERWALK and Battroid. No invisible teleporting/rescaling of parts to fake transformation.
- Prefer named rigid components and pivots; explicitly label geometry inferred from incomplete blueprints.
- No Blender/MCP output, code assertion, or successful GLB export alone is evidence of visual fidelity.

## Required iteration (one assembly at a time)
1. Lock exact reference drawing(s), view, crop, and feature landmarks in a local manifest. Record source URLs; don't commit copyrighted photos without permission.
2. Make a reversible change to one component; record the revision/commit.
3. Create fixed-camera orthographic **top/front/side** and three-quarter Blender beauty+mask renders (qa/render_views.py).
4. Use qa/compare_masks.py for like-for-like masks at the **same alignment and scale**. Save overlays, JSON metrics, and measured Blender dimensions.
5. Review every image, including the **worst** match; document the three highest-priority discrepancies. Never claim a high similarity score without checking view correspondence and reference provenance.
6. Fix the largest discrepancy; rerender and demonstrate that the mismatch reduced **without regressions in other views or modes**.
7. Limit cycles to 3 per part before recording blockers/reconsidering the modeling approach. No open-ended self-assigned runs.

## Milestones and acceptance
- **M0 — Connection:** Prove actual read-only Blender scene inspection over MCP; record timestamp and command/result.
- **M1 — Fighter blockout:** Deliver Blender .blend, 4 beauty renders, 4 masks, bounds JSON, reference overlays and a defect log. Accurate nose, cockpit, fuselage and wing silhouette must be shown, not merely asserted.
- **M2 — Three-mode rig:** Show verifiable shared geometry, pivot hierarchy, intermediate animation frames and collision/deformation review.
- **M3 — Website:** GLB loaded in existing viewer; verify transform, exploded parts, isolation, reassembly and download.
- Only promote a milestone after artifacts are examined. Record unknowns as **not verified**.
- Commit evaluation artifacts to feature branch when size/licensing permit; use Git LFS or external linked storage for large binary .blend and video files, and record exact immutable identifiers.

## Test commands
- \`python -m unittest discover -s qa -p 'test_*.py'\`
- \`blender --background --python qa/render_views.py -- --input /path/to/model.blend --collection "N1 newly traced replaceable components" --out /path/to/qa-run\`
- \`python qa/compare_masks.py --reference /path/to/ref-top-mask.png --render /path/to/qa-run/top_mask.png --out /path/to/qa-run/top_overlay.png\`

These commands are distinct from the existing site's build script; keep the site's no-install/offline design intact.
