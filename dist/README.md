# Valkyrie Assembly Lab

An interactive, original VF-1J-inspired model with 24 independently selectable assemblies containing 424 separate modeled elements, a layered exploded view, reassembly, Fighter / GERWALK / Battroid poses, and portable 3D exports.

## Open it on your computer

1. Extract the entire ZIP into a folder.
2. With Python 3 installed, run `python start.py` from that folder. On Windows, double-click `START-WINDOWS.bat` (uses the Python launcher).
3. The workshop opens in your browser. Close the terminal to stop it.

A local web server is necessary because browsers restrict ES modules opened directly with file://. Any static web server also works. Once served, the workshop and exports work without an internet connection. No external API, account, package installation or CDN is required by the application.

## Put it on another website

Upload this folder to a static website host. Keep the relative folder structure intact and serve `index.html`. All model, source and Three.js files are included. The original Sites access controls are hosting settings and are not part of this portable project; configure the audience on your new host.

## Controls

- Drag: orbit. Scroll / pinch: zoom. Right-drag / two fingers: pan.
- Tap a modeled part or use the assemblies list, then Detach, Isolate or Focus.
- Use the separation slider or Explode model / Reassemble.
- Choose Fighter, GERWALK or Battroid. On desktop, Play transformation cycles the three modes.
- Keyboard: 1–3 modes, Space explode/assemble, R reset, F fit, L labels, W wireframe, A orbit, Escape clear selection.
- Export: animated GLB, current pose / isolated assembly GLB, or the whole portable website.

## Tesla-style exploded presentation

The workshop opens partly exploded. The slider first separates the main assemblies, then peels their individual modeled elements apart. Use **All pieces** for a flat catalog of all 424 elements; their display sizes are normalized in this catalog only. Click any element to isolate and inspect it, and use **Reassemble** to restore the complete vehicle. Some elements are trim, markings or geometric details, rather than separate manufactured parts.

The dark studio, floating inspection panels, continuous separation and parts catalog are based on the user-supplied [Tesla Model X exploded-view demo](https://www.tripo3d.ai/3d-prompts/tesla-model-x-exploded-view-2096009146248122416). No Tesla geometry or media is included.

## 3D asset

`assets/vf1-valkyrie.glb` contains 24 named assembly roots, 424 independently named model elements, 46,180 triangles and four animation clips: Fighter to GERWALK, GERWALK to Battroid, Full transformation, Explode and reassemble. Import the GLB directly into Blender or another glTF 2.0 tool. Coordinates are arbitrary model units; do not use the geometry as a dimensionally accurate manufacturing or 3D-printing design.

## Change the model

- `model.js`: authored component geometry, material palette and three assembly poses.
- `pieces.js`: staged separation and normalized parts-grid coordinates.
- `studio.css`: dark studio presentation.
- `viewer.js`: interaction state, selection, animation and camera controls.
- `style.css` and `index.html`: responsive interface.
- `source/build-model.mjs`: rebuilds and validates the GLB with Node.js, using included dependencies. Run `node source/build-model.mjs`; no npm installation is needed.
- `portable-files.json`: files included by Export project. Update the list if you add files.

## Reference and rights

The supplied Macross screenshot informed the white/red direction. Additional design reference: [Bandai / Tamashii Nations VF-1J](https://tamashiiweb.com/item/15096/?wovn=en).

This is an original stylized fan model with interpretive transformation mechanics. It is not an exact toy/CAD reconstruction or an official Macross product. Macross character and vehicle designs belong to their respective rights holders. Three.js 0.180.0 is included under its MIT license in `vendor/THREE-LICENSE.txt`.

## Validation

The shipped GLB was exported and loaded again using Three.js. All 24 roots, finite geometry and pose bounds, and all four animation clips were checked. Local imports, syntax and ZIP contents were checked. Browser visual testing was not performed in this build.
