# Reference style rhythm study

This study extracts rhythm, camera language, animation organization, and information presentation patterns. It must not copy source assets, visual compositions, narration, scripts, or brand packaging.

## Sources consulted

- 3Blue1Brown official site and Essence of Linear Algebra materials: https://www.3blue1brown.com/ and https://www.3blue1brown.com/lessons/eola-preview/
- Primer official site and channel direction: https://primerlearning.org/ and https://www.youtube.com/@PrimerBlobs
- StatQuest official site / index: https://statquest.org/ and https://statquest.org/video-index/
- Bilibili Manim references, including Manim tutorial collections and Northernl__ Manim math animation examples: https://www.bilibili.com/video/BV1W4411Z7Zt/ and https://www.bilibili.com/video/BV1XP411o7gY/
- Optional Manim / 3D / AI-assisted animation direction observed in public Bilibili Manim examples, used only for pacing and layering principles.

## 1. 3Blue1Brown rhythm: progressive construction

Reusable lessons:

- Build one visual object at a time; each new object should answer the previous frame's question.
- Formula and geometry should appear as synchronized counterparts, not as independent overlays.
- Camera motion should be smooth and motivated: pan/zoom only when changing conceptual focus.
- Important ideas need a visual pause after construction; the pause is part of the explanation.
- Avoid dense explanatory text while the main object is forming.

How to adapt without copying:

- Use our blackboard/tech palette, not 3Blue1Brown's compositions.
- Keep formulas and curves in our layout, but adopt the principle of synchronized reveal.
- Use slow push/pull or local emphasis only when it clarifies the model state.

## 2. Primer / StatQuest rhythm: simple model explanation

Reusable lessons:

- Primer-style simulation pacing works because rules appear before complex outcomes; viewers see simple agents/points change into a pattern.
- StatQuest-style teaching often gives one conclusion at a time: state intuition, show one visual, then introduce the formal term.
- Short captions beat long subtitles; each caption should resolve one local question.
- The formula should feel earned by the preceding visual, not dropped in at the opening.

How to adapt:

- Use first 2 seconds for a visual hook, not a text-heavy definition.
- Use 1.5-3 second beats: reveal points, draw line, highlight parameter, hold.
- For teaching mode, hold final formula + graph longer than showcase mode.

## 3. Bilibili / Manim Chinese teaching rhythm

Reusable lessons:

- Chinese teaching videos need longer formula hold time because subtitles, formula, and narration compete for attention.
- Manim-style construction is effective when equation transforms retain spatial continuity.
- Chinese subtitles should be short, ideally one clause per beat, and should not overlap the main formula area.
- A final paused frame is especially useful for classroom or creator voice-over contexts.

How to adapt:

- Keep Chinese subtitles in a bottom safe area and avoid simultaneous high-density formula changes.
- For dense formulas, hold the final state 2-4 seconds or export a teaching-pause variant.
- Use contact sheet to check composition, then mp4/WebP to check reading rhythm.

## 4. Optional innovation: 3D surface / particles / HUD

Reusable lessons:

- 3D and particle systems should establish hierarchy: surface first, focus point second, labels third.
- Rotations must be slow; fast 3D motion feels decorative and can hurt comprehension.
- HUD elements should be sparse and functional. Avoid full-screen neon frames, scanlines, or excessive bloom.
- Particle point clouds should reveal distribution/cluster structure, not become background glitter.

How to adapt:

- Use pseudo-3D for model landscapes and embeddings only when the model concept benefits from depth.
- Provide a rollback path to 2D chart if the 3D object is not readable in contact sheet.

## Timing grammar v1

| Time | Purpose | Visual action | Text density | Camera / comfort rule |
| --- | --- | --- | --- | --- |
| 0-2s | First visual hook | Establish mood and first geometric/model object | none/low | Do not stack text; avoid fast camera motion |
| 2-6s | Model name + core formula | Model name or formula appears; graph starts moving | low/medium | Camera stays stable unless focus changes |
| 6-14s | Main construction | Build subject graph/surface/points; one clear change every 1.5-3s | medium | Smooth motion, no competing labels |
| 14-24s | Highlight / parameter / interval | Mark peak, interval, slope, control point, or parameter shift | medium | Light push-in or local zoom allowed; no shake |
| Final 2-4s | Teaching pause | Hold clean formula + graph state | low/medium | Stable frame for narration or classroom pause |

## Short-sample adaptation

Current samples are 3.6-4.2 seconds, so they compress the grammar:

1. 0-1s: visual hook / scene context.
2. 1-2.4s: graph or surface construction.
3. 2.4s-end: conclusion and teaching-pause frame.

Longer 20-24 second versions should use the full grammar above.

## Quality gates for rhythm

- Every animation event must have `start_ms`, `end_ms`, `visual_action`, `camera_action`, `text_density`, and `comfort_note`.
- No two dense text events should overlap.
- Every 1.5-3 seconds should introduce exactly one meaningful visual change.
- Final state must remain clean enough to pause.
- If mp4 is unavailable, validate timing with WebP/HTML preview plus contact sheet; mark it as draft rhythm review only.
