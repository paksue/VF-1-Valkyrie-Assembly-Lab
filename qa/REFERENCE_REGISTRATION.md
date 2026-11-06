# Locked source art and real-projection registration (N2 → N3)

## Sources (referenced, NOT redistributed)
- VF-1A five-view, **1800×1140**: https://www.macross2.net/m3/sdfmacross/vf-1a-valkyrie/vf-1a-schematics.png
  This is a **shared VF-1 airframe** shape proxy, not VF-1J-specific livery.
- VF-1J color and three-view drawing, **1300×1208**: https://macross2.net/m3/sdfmacross/vf-1j-valkyrie/schematic-vf1j-tias-all.png
  This is the correct VF-1J visual target but its crop/camera is **not yet registered** for an apples-to-apples pixel metric.

The source images were fetched into the restricted Windows BlenderAI QA folder for local review; **do not add source-art images or derived masks to the public repo** without permission.

## Actual registration performed
- Used the known VF-1A drawing coordinate convention from the existing traced Blender source: \`u=(model_y+7.115)/S+414\`, \`v=569-model_x/S\`, \`S=14.23/(1470-414)\`.
- Evaluated all Blender meshes at frame 1 (39 meshes) and projected their triangles into the original 1800×1140 image pixels, restricting to the upper/top half; **not a screenshot stretched into place**.
- Saved a local red-boundary/blue-footprint composite on the source five-view drawing and binary model occupancy masks.
- Used these projected masks to check that the **N3 livery change did not damage the N2 airframe** (only 2 half-resolution pixels changed; IoU 0.9999419).
- Visually inspected the correct VF-1J red chest and wing design and increased the N3 red-band coverage.
- This registration does **not** compute reference IoU. The original is line art with alternate wing configurations, internal strokes and two wing/underside renderings; naive thresholding would yield a false shape score.

## Local Blender files
\`C:\Users\BlenderAI\Documents\VF1J_reference_build\qa_reference\`:
\`vf1a_fiveview.png\`, \`vf1j_schematic.png\`, \`vf1a_N2_model_registered_overlay.png\`, \`vf1a_N3_model_registered_overlay.png\`, both occupancy \`.npy\` masks and regression JSON.

\`C:\Users\BlenderAI\Documents\VF1J_reference_build\rebuild_N3\VF1J_rebuild_N3.blend\` is an editable Fighter checkpoint with 4 render PNGs.

## What to fix next
1. Register **VF-1J** top/side views against the model by hand-confirmed landmarks and maintain a camera/scale manifest, not by automatically maximizing overlap.
2. Replace the blocky radome/canopy joint, air intakes, engine nacelles and tail plane with reference-constrained geometry.
3. Develop shared-parts transformation rig, verify intermediate collision frames and load a staged GLB into the existing website.

This is evidence of an actual review loop. It is **not** a claim that the complete aircraft or transformation is accurate.

## New side-view registration
- \`qa/project_side_N3.py\` projects N3's evaluated mesh triangles into the **side view** on the same VF-1A five-view sheet using \`u=(model_y+7.115)/S+414\`, \`v=975-model_z/S\`.
- A local side overlay was generated and visually reviewed. The nose/canopy silhouette aligns relatively well to the drawing; the large engine nacelle and rear underside sections remain less accurate.
- This is **visual correspondence**, not a ground-truth IoU. It must not be conflated with a VF-1J-specific livery accuracy test.
