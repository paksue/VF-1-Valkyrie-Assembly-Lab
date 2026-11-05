# VF-1J reference-accurate reconstruction goal

**Target:** The original TV-series VF-1J (Hikaru Ichijo / white-red / 101); not VF-1S, DYRL redesign, FAST Pack or a generic F-14.

**Outcome:** An editable, dimensionally anchored Blender model with a credible transformation rig and three visually faithful silhouettes, usable as a replacement GLB in the existing interactive assembly website.

## Reference hierarchy
1. Original 1982 VF-1J design/line art for visual identity and silhouettes.
2. Macross technical specifications for scale (in-universe, not real aircraft manufacturing measurements).
3. Bandai/Tamashii DX Chogokin VF-1J 1/48 for physically achievable articulation (acknowledge toy-specific compromises).
4. Hasegawa fighter kit for aircraft panel detail; never let later interpretations silently override the TV design.

Baseline spec values to verify per source: Fighter **length 14.23 m**; extended **wingspan 14.78 m**; swept configurations vary; wingspan only applies at the referenced angle. Do not assume the old GLB's arbitrary units are meters.

## Strict evidence contract
Every review must record:
- exact reference image provenance, variant, viewpoint and any inferred camera perspective;
- source model commit, Blender version, file hash, active frame, render camera/orientation and output filenames;
- mesh/scene bounds in stated units and scale assumptions;
- top/front/side/three-quarter renders with visual comparison;
- silhouette IoU **only if** both images are registered at the same view, resolution, scale and position;
- per-part landmarks (nose tip, canopy beginning/end, wing pivots/tips, tail, inlet centers), compared numerically when possible;
- transformation intermediate frames and geometry continuity/penetrations in later milestones;
- explicit unresolved differences and changes attempted.

**IoU is a diagnostic, not a certificate of accuracy.** A high number can conceal a wrong head, no internal detail, inconsistent references or impossible transformation. Different perspective/orthographic views must not be scored against each other.

## Phases
- 0. Verify the MCP/Windows background-workflow connection without disturbing running Blender.
- 1. Clean Fighter geometry and fixed reference comparison loop, starting with nose/cockpit.
- 2. Correct wings, nacelles, tail, marking proportions.
- 3. Develop GERWALK/Battroid from the same assembled components; establish mechanical pivots.
- 4. Validate all three endpoints and intermediate frames, then integrate with \`dist/viewer.js\`/the model asset contract.
- 5. Regression, accessibility, exports and visual acceptance; user reviews before merging/deploying.

## Not established
There is currently **no proven reference-accuracy score**, no completed mechanical transformation validation, and no verified new Blender-generated GLB deployed. Previous local checkpoints may exist, but must be inspected/retested rather than assumed valid.
