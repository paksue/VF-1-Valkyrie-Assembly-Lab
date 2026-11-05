# Verification status — 2026-11-05

## Executed successfully
- Omarchy DevSpace workspace \`/home/pakyinli/Projects\` responded.
- Blender MCP bridge on Windows \`Blender 5.2.0 LTS\` responded in the dedicated Python virtual environment (\`blender_mcp/mcp/.venv/bin/python\`).
- Background Blender subprocess completed; the active interactive Blender scene remained a separate \`NeonCity2049\` file with 409 objects at launch. The project's active UI was not overwritten.
- Inspected existing \`valkyrie_blender/rebuild_N1.py\` Fighter blockout and four rendered views.
- Corrected a **false width measurement caused by rotating object-axis-aligned bounding boxes**. Accuracy tests now sample evaluated mesh vertices; measurements changed accordingly.
- Created an independent N2 checkpoint (\`blender/rebuild_N2.py\`) with only the final wing-sweep keyframe changed from 24° to 26.5°.
- Background Blender generated N2 .blend and four Fighter views. Independently reopened N1 and N2 .blend files in background Blender and measured frame-1/15/30 mesh vertices.
- Rendered frame-30 top views from both checkpoints and inspected the before/after results.
- Wrote [first numerical evidence](runs/2026-11-05-n1-n2-wing-iteration.json) with artifact hashes.

## Measured results
| Check | Reference | N1 | N2 |
| --- | ---: | ---: | ---: |
| Fighter length | 14.23 m | 14.2337 m | 14.2337 m |
| Frame-30 extended span | 14.78 m | 14.5704 m | 14.7852 m |
| Absolute span error | 0 m | 0.2096 m | 0.0052 m |

The reduction in **this one error** is 97.5%, not a model-wide fidelity score. Frame-1 width (12.4966 m) has not been certified as matching a documented sweep angle. Fighter height (3.6788 m) is not an apples-to-apples validation against a dimension that may include landing gear.

## Open gates
| Gate | Status |
| --- | --- |
| M0: Live Omarchy-to-Windows MCP verified | **Observed** |
| M1: Fighter blockout and four-view renders | **Observed for N1/N2** |
| M1: Locked VF-1J-specific reference masks, same-scale registered overlays | **Not yet done** |
| M1: Overall visual fidelity | **Not verified** |
| M2: Working three-mode mechanical rig | **Not built for N2** |
| M3: Replacement site GLB / interface regression tests | **Not done** |

## Visual defects seen in the renders
- Abrupt radome-to-cockpit seam, simplified canopy and fuselage cross-sections.
- Simplified air intakes, nacelles, fins and markings; provisional VF-1J stowed head.
- Need to align actual VF-1J technical drawings in all three orthographic views; N2's common-airframe trace uses a VF-1A sheet.
- No continuous GERWALK/Battroid transformation rig in N2. Existing K/L2 studies are separate and remain unmodified.

The existing \`dist/\` site and production GLB are unchanged. The present work is on a draft pull request/feature branch. No accuracy certification has been issued.

## CI tool verification
- The GitHub Actions \`VF-1J verification tools\` job passed for commit \`fe3a2c8\`, run [42132511073](https://github.com/paksue/VF-1-Valkyrie-Assembly-Lab/actions/runs/42132511073).
- CI covered Python dependencies, five synthetic mask-comparison tests and syntax compilation of \`qa/render_views.py\`.
- CI **did not** execute Blender itself, compare licensed reference drawings, or validate transformation. Those remain independent gates.
