# Blender source checkpoints

## Reproducible independent Fighter blockout

- [rebuild_N2.py](rebuild_N2.py) generates an **editable** Fighter-only Blender scene. It derives the common VF-1 airframe from a VF-1A technical five-view drawing and retains provisional VF-1J details. This is not a completed VF-1J or three-mode rig.
- Build in a **separate background Blender 5.2** process, using a dedicated restricted account/workspace:

  \`blender --background --factory-startup --python blender/rebuild_N2.py\`

- The script writes \`blender/rebuild_N2/VF1J_rebuild_N2.blend\`, \`fighter_{top,front,side,threequarter}.png\` and \`reference_landmarks.json\`. When executed through Omarchy's Blender-MCP bridge, \`__file__\` is overridden by the Windows runner and output is inside \`C:\Users\BlenderAI\Documents\VF1J_reference_build\rebuild_N2\`.
- The wing-sweep frame-30 keyframe was tuned from 24° (N1) to 26.5° (N2) so the **actual evaluated model** wingspan moved from 14.5704 m to 14.7852 m. The target fully extended span is 14.78 m. This is an empirical tuning parameter, not proof of an exact toy-joint sweep angle.
- See [evidence JSON](../qa/runs/2026-11-05-n1-n2-wing-iteration.json).

**Never** execute this script inside a live user scene: it calls \`bpy.ops.wm.read_factory_settings(use_empty=True)\`. Use background Blender, not the running GUI process.

## Remaining
- Replace VF-1A shared-airframe proxy with locked VF-1J-specific orthographic source comparison and visually review all four projections.
- Improve nose-to-cockpit transitions, intakes, nacelles, wing planform, tail, head geometry and mechanical subdivisions.
- Build actual GERWALK/Battroid transformation; current N2 does **only** Fighter mode and an illustrative sweep animation.
- Validate staged 3D geometry, render masks and multiple angle overlays before changing the production GLB.

The website under \`dist/\` has not been modified.

## Current candidate — N3 (visual marking pass)

[N3 Blender source](rebuild_N3.py) was built with Blender 5.2 over the live Omarchy→Windows MCP connection in an isolated background process. Editable output is on Windows:
\`C:\Users\BlenderAI\Documents\VF1J_reference_build\rebuild_N3\VF1J_rebuild_N3.blend\`.

**What changed from N2:** wider red wing stripes and the more prominent chevron across the white shoulder-roof, as guided by the original VF-1J color sheet. No new transformation rig or major geometry. The evaluated Fighter length is 14.2337 m and extended span 14.7852 m as before.

**Actual N3 renders:**
- [Top view](../qa/runs/2026-11-05-n3-top.jpg)
- [Three-quarter](../qa/runs/2026-11-05-n3-perspective.jpg)
- [N2 top before](../qa/runs/2026-11-05-n2-top.jpg)

See the [real top + side reference-registration method](../qa/REFERENCE_REGISTRATION.md). The next geometry pass should correct nacelle/intake and rear underside proportions from reference drawings, then revisit head and mechanism.

## Latest candidate — N5 (real intake topology)

[N5 source generator](rebuild_N5.py) builds in isolated Blender 5.2, saving:

\`C:\Users\BlenderAI\Documents\VF1J_reference_build\rebuild_N5\VF1J_rebuild_N5.blend\`

N5's changes from N4:
- Replace painted circular intakes with named **rounded-rectangular rings**, converging wall geometry, and recessed black throats.
- Remove the engine-shell front cap to leave an actual mouth. The opening is 0.484 m wide × 0.394 m high per side.
- Reduce the engine nacelle's loft exponent from 0.43 to 0.25, yielding flatter and more angular surfaces.
- Retain two subtle guide vanes; remove an unsupported vertical divider.

**Actual Blender comparison renders:** [N4 intake closeup](../qa/runs/2026-11-05-n4-intake-closeup.jpg) versus [N5 intake closeup](../qa/runs/2026-11-05-n5-intake-closeup.jpg); [N5 perspective](../qa/runs/2026-11-05-n5-perspective.jpg).

[QA evidence](../qa/runs/2026-11-05-n4-n5-intake-geometry.json): 0 top projected pixels changed, 72 side projected pixels changed, 0 front-cap faces at either intake. This is a **regression check**, not an independently verified Macross-reference fidelity score.

N5 remains Fighter-only. A physically credible GERWALK/Battroid transformation and site GLB export are **not** complete. Model surface details, head, landing gear, nacelle shape and joint clearances remain to be verified against original design art.
