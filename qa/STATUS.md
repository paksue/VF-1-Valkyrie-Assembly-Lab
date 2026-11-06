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

## N3 follow-up — 2026-11-05
- Downloaded **full native-resolution reference sheets** to restricted Windows QA: VF-1A five-view (1800×1140, SHA256 \`8bcf718bbe1f4e5d57038225d4a47d28bebff96e72b1496e3eb13f159a21ae55\`) and VF-1J schematic (1300×1208, SHA256 \`b638bb6a00eaf7d2550cc49ffb9f60cf60d51e99e8bbfe08100788587a038b0e\`). Images were not published.
- Developed and ran **actual evaluated mesh triangle projection** into the source VF-1A top and side drawing coordinates; inspected the registered overlays. This is more reliable than resizing two screenshots to appear aligned.
- Built \`rebuild_N3.py\` through Windows Blender 5.2 over MCP as a **separate background process**, producing new editable .blend and Fighter renders. VF-1J-style red shoulder-chevron and wing-stripe width revised.
- N2→N3 top silhouette self-IoU: **0.9999419**, only two half-resolution projected occupancy pixels changed; Fighter length and extended wingspan unchanged. Red-marking pixels on equal-size top renders increased from 19,742 to 40,755. **Neither value is reference accuracy**.
- Inspected side overlay: nose and canopy follow the common-airframe drawing reasonably closely, but engine nacelles, intake volumes, rear underside profile and head details remain less faithful. These are the next geometry correction priorities.
- Actual Blender render previews: [N2 top](runs/2026-11-05-n2-top.jpg), [N3 top](runs/2026-11-05-n3-top.jpg), [N3 perspective](runs/2026-11-05-n3-perspective.jpg). See [full N3 evidence JSON](runs/2026-11-05-n2-n3-livery.json).
- **Still not done:** registered VF-1J colored-sheet pixel metrics, GERWALK/Battroid mechanical rig for N3, intermediate-frame collision tests, or website GLB replacement.

Current approved work is **only a draft QA branch**; the deployed Three.js workshop and GitHub \`main\` remain unchanged.


## N4 — Recessed twin intakes, 2026-11-05
- Constructed an isolated editable Blender N4 Fighter checkpoint from N3, adding intake lips, dark throats, vane details, and independently named nacelle side seams/hatches.
- Background Blender 5.2 completed the four standard renders and saved \`C:\Users\BlenderAI\Documents\VF1J_reference_build\rebuild_N4\VF1J_rebuild_N4.blend\`. The running UI scene was not modified.
- Evaluated mesh count increased from 39 to **43**. Overall aircraft geometry remains 14.2337 m length and 14.7852 m extended span.
- A pixel-aligned projection onto the VF-1A five-view common airframe showed top mask **0 pixel change** and side mask **16 pixel change** (N3→N4). Self-comparison is NOT a reference-fidelity grade.
- [Actual N4 front Blender render](runs/2026-11-05-n4-front.jpg), [three-quarter render](runs/2026-11-05-n4-perspective.jpg), [reproducible source](../blender/rebuild_N4.py), [N4 QA evidence](runs/2026-11-05-n3-n4-intakes.json).
- **Visual review:** front intake openings are now visible; they still look too circular relative to the flatter rounded-rectangular reference. Next geometry revision should reshape those apertures and build the nacelle casing from the correct 3D contours before rig development.
- No three-mode rig, no website GLB change, no certification of overall shape accuracy.


## N5 — 2026-11-05: rounded-rectangular inlets and open ducts

**Actually executed** on Windows Blender 5.2 using the existing Omarchy MCP bridge; background subprocess preserved the interactive scene. The N5 editable .blend and four Fighter renders are saved to \`C:\Users\BlenderAI\Documents\VF1J_reference_build\rebuild_N5\`.

- Replaced N4 circular black inlet faces with separate rounded-rectangle rim and duct wall meshes, and removed the front cap of each engine shell. Checked that each intake has zero front-cap polygons and 28 duct wall faces.
- N5 mouth geometry per side is **0.484 × 0.394 m**. Front closeups from identical Blender cameras were inspected; unsupported cross-shaped intake dividers were removed.
- Fighter **14.2337 m length**, frame-30 extended **14.7852 m wingspan**, and maximum frame-1 dimensions unchanged from N4.
- Measured registered source-coordinate **N4→N5 self-regression**: top view unchanged (0 pixels, IoU 1.0); side view 72 changed pixels (IoU 0.9975551). This is *not* reference accuracy.
- [Real N4 closeup](runs/2026-11-05-n4-intake-closeup.jpg) · [Real N5 closeup](runs/2026-11-05-n5-intake-closeup.jpg) · [N5 perspective](runs/2026-11-05-n5-perspective.jpg).
- [Reproducible N5 source](../blender/rebuild_N5.py) · [Full observed QA report](runs/2026-11-05-n4-n5-intake-geometry.json).

**Remaining:** independently evaluate against a locked VF-1J front and side technical drawing, rebuild actual engine nacelle casing geometry and other Fighter inaccuracies, then engineer a transformation rig and website GLB. No new model has been deployed to \`main\`.

## N6 — Full nacelle side armor contour, 2026-11-05

- Using the live Omarchy→Windows Blender 5.2 background MCP bridge, **N6** was saved as an editable \`VF1J_rebuild_N6.blend\`. Existing active Blender UI scene remained a separate \`NeonCity2049\` file and was not replaced.
- Each nacelle/engine-leg housing now uses **13 cross-sectional loft stations** (N5 had 6) and a separately grouped, **ten-point removable side armor panel**, plus side panel seams and a circular service ring. The original N5 rectangular intake ducts remain intact.
- Original VF-1A shared-airframe source drawing was used for 3D source-coordinate top and side overlays; VF-1J-specific color reference remains a separate source. Drawings are local only, not redistributed in Git.
- An actual Blender QA script checked the new panel's analytic shell distance. The initial center facet sat 1.1 mm inside the theoretical shell; this was corrected and rerendered. Both final panels now sit **14–22 mm outside the shell**, with no analytic clipping indicated.
- **Geometry unchanged overall:** 14.2337 m length; 14.7852 m extended frame-30 span. 45 meshes in N5 versus 47 in N6.
- N5→N6 reference-coordinate *self-regression* (not Macross source IoU): top IoU **0.9974803** (87 changed half-resolution pixels); side IoU **0.9972218** (82 changed pixels).
- [N5 side closeup](runs/2026-11-05-n5-engine-side.jpg) vs [N6 side closeup](runs/2026-11-05-n6-engine-side.jpg); [N6 full side](runs/2026-11-05-n6-fighter-side.jpg); [N6 three-quarter](runs/2026-11-05-n6-perspective.jpg).
- [Source script](../blender/rebuild_N6.py) · [verified QA report](runs/2026-11-05-n5-n6-engine-side.json).
- **Open:** independent VF-1J-specific view registration and contour score, real three-mode rig and collision validation, GLB export/website integration. No updates to \`dist/\` or \`main\`.

