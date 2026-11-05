# Blender visual QA proof-of-loop

This directory is **independent of the deployed website**. The existing \`dist/\` app remains untouched.

## First proof
1. Check that the Omarchy -> Windows loopback forwarding to Blender MCP responds. Avoid modifying the running interactive scene.
2. Run a **separate background Blender** build and save an editable .blend in a restricted working directory. Open the new .blend with the background renderer:
   \`blender --background --python qa/render_views.py -- --input /path/to/model.blend --collection "N1 newly traced replaceable components" --out /path/to/run --frame 1\`
3. Inspect four generated \`*_beauty.png\` and four \`*_mask.png\` views, and \`manifest.json\`. The script assumes Blender axes: **X right, Y rear (nose -Y), Z up**.
4. Prepare one human-approved 1-bit or alpha silhouette mask from a **matching orthographic source drawing**. Do not compare photo perspective with orthographic views.
5. With \`python -m pip install -r qa/requirements.txt\`, run:
   \`python qa/compare_masks.py --reference /path/to/reference_top_mask.png --render /path/to/run/top_mask.png --out /path/to/run/top_overlay.png\`
6. Compare JSON, overlay, source landmarks and beauty renders, then write the defects to a report. Revise one component and repeat.

## Test
\`python -m unittest discover -s qa -p 'test_*.py'\`

## Caveats
- The renderer can verify **real** shape views and objective Blender bounds, not source correctness or mechanics.
- Mask comparison assumes equal image size and alignment, and **does not auto-rescale or rotate** the render to flatter the result. If reference/model registration is missing, report \`not comparable\`.
- RGB reference masks without transparent pixels must contain **white foreground on black background**; use \`--invert-reference\` for black subject on white. Transparent masks use alpha. Reject empty masks.
- \`manifest.json\` is about *render execution*, not an accuracy grade.
- The reference manifest contains source links only. Images or derivative masks must be supplied or prepared by a reviewer, with use rights checked.
- Large .blend files/renders belong on a feature branch or an artifact store, not directly on the live deployment.
