# Related work (checked November 2026)

What else exists for isometric pictures, and why this skill draws in code.

## Other Claude skills

- **iso-scene** (okou-ai/okou-skills): prompts an image model for one editorial isometric
  scene in a locked style (hairline outlines, a saturated one-hue background). Useful idea
  kept here: *the scene is the subject*, so pick props native to the topic, never a
  generic box with labels. Not adopted: an image model cannot keep two themes identical,
  exact counts, or layering that holds when people overlap.
- **isometric-ops** (0xdarkmatter/claude-mods): a router for isometric work across web,
  games and AI generation (projection math, game tiles, Blender, a scene composer). Its
  point that game tiles are 2:1 dimetric, not 30-degree isometric, does not apply here:
  web vector art uses true isometric, as this engine does.
- **isometric-design** (sickn33/agentic-awesome-skills), **ai-iso-skill** (MrBongoC),
  **isometric-asset-sheets** (amilich/isometric-city): a general design guide, a hairline
  HTML plate, and game sprite sheets. None draws characters or sorts overlapping parts.

## Engines and the sorting method

- **IsometricBlocks** (Shaun Lebron): the classic way to order boxes. Their screen
  hexagons decide which pairs overlap, the separating axis decides which is in front, and a
  topological sort gives the order. The first version of this engine used it on whole
  groups (a person, a bench), so two overlapping groups whose bounding boxes intersected
  fell back to drawing order, which put walkers in front of the people they were behind.
  This engine keeps the method for boxes and adds an exact test from the real faces
  (projected overlap and depth) for everything else, with every part its own unit.
- **heerich.js** (meodai): a voxel engine that writes SVG, one polygon per visible face.
  A good fit for voxel sculpture; not adopted because per-voxel outlines would grid the
  characters, and the blog's tooling is Python and Node without a voxel step.
- **isomer** (jdan), **@elchininet/isometric**: JavaScript isometric drawing libraries for
  the browser. This skill renders offline to static SVG, so the page ships no script.

## Objects first

The object-first structure (build each object in its own space, check it alone, place
instances with a transform, attach people and cables to anchors) is the scene-graph idea
from 3D tools, kept to what an isometric drawing needs: turns in 90-degree steps and
mirroring keep every box axis-aligned, so the exact sorting still holds, while a placed
object stays a group only for building and arranging, never a single paint layer.
