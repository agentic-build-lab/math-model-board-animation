# Formula Creator Reference Study Plan

This document tracks the reference-study direction for short-form math/model
visualization videos. The goal is to learn repeatable production grammar, not
to store or redistribute the original video.

## Reference

- User-provided creator label: `数理化之王`
- User-provided title: `人生改变命运的五次机会及数学原理`
- Share URL: `https://v.douyin.com/EyF4TnI76fI/`
- Resolved public page: `https://www.douyin.com/video/7657866076827187572`
- Capture status: browser page resolved; frame/contact-sheet study still needs
  manual or browser-based capture.

Do not commit downloaded reference video files. If visual evidence is needed,
commit only small derived review notes, timing tables, and approved thumbnails.

## Why This Reference Matters

This direction is not only formula rendering. It combines:

1. a high-curiosity life or society topic;
2. a mathematical principle that feels powerful;
3. synchronized formula and graph explanation;
4. cover/title packaging that makes the topic clickable;
5. fast but comfortable pacing.

The product target is a reusable topic-to-model-visualization workflow:
topic -> hook -> math model -> visual blocks -> title/cover -> render -> review.

## What To Extract

For each reference pass, fill a versioned study note under `work/` or `docs/`
without storing the original video.

### Topic And Packaging

- title pattern;
- first 3 seconds hook;
- conflict or curiosity gap;
- audience promise;
- cover text structure;
- cover visual structure;
- whether the model is explained for understanding or used as authority.

### Visual Grammar

- background style;
- formula placement and density;
- graph placement and axis treatment;
- line thickness, glow, and fill opacity;
- highlight color and duration;
- camera zoom, pan, and hold timing;
- relationship between narration, formula reveal, and graph motion.

### Timing Grammar

Use this minimum table:

| beat | start_ms | end_ms | voiceover_role | formula_action | graph_action | camera_action | comfort_note |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| hook | 0 | 3000 | topic hook | none or key symbol | visual teaser | slow push | must be immediately readable |
| model intro | 3000 | 8000 | name principle | reveal formula | show axes | stable | do not overload text |
| mechanism | 8000 | 18000 | explain variable effects | highlight terms | animate curve | small zoom | every highlight needs a reason |
| conclusion | 18000 | 26000 | return to life topic | simplify formula | final state | hold | leave one takeaway |

## Input Schema Extension Ideas

Future scene configs should support:

- `topic_hook`
- `title_candidates`
- `cover_brief`
- `reference_style_id`
- `formula_blocks`
- `graph_blocks`
- `visual_authority_level`
- `viewer_understanding_level`
- `timing_beats`

The same math model can produce two versions:

- `premium_visual`: spectacular, advanced, high-status visual effect;
- `teaching`: slower, clearer, lower density, better for real understanding.

## Implementation Backlog

1. Add a browser capture helper that records a reference contact sheet from a
   user-opened public page.
2. Add a `reference_style_study` template with fields for color, line width,
   fill opacity, glow, camera motion, title, and cover.
3. Add a `topic_to_formula_video_brief` generator that turns a topic into a
   math-model visual plan.
4. Add title and cover generators as first-class outputs.
5. Add a review gate that rejects samples when the formula or graph looks cheap,
   cramped, visually noisy, or too hard to parse.
6. Promote good samples to recipes and the future
   `math-model-board-animation` skill.

## Review Rule

Do not judge the reference match only by a single still frame. The standard is:

- the first frame sells the topic;
- the motion rhythm feels deliberate;
- the formula and graph reinforce each other;
- the viewer can feel the model is powerful even if they do not fully
  understand every detail;
- the final output has a recipe, config, manifest, and review notes.
