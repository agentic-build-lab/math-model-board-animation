# Math Model Board Animation

A configurable renderer for board-style explanations of mathematical formulas, statistical models, quantitative factors, physics, economics, and machine-learning concepts.

The project separates structured content from visual templates, while preserving a manual review gate for mathematical accuracy and presentation quality.

## Repository layout

- `packages/model_animation/` — reusable rendering components.
- `scripts/render_model_video.py` — command-line renderer.
- `schemas/model_video.schema.json` — structured input schema.
- `examples/` — JSON and YAML scene examples.
- `docs/` — workflow, templates, architecture, and review guidance.

## Render the sample

```powershell
python scripts/render_model_video.py --config examples/garch_volatility_scene.json
```

The renderer writes a video, contact sheet, and render report under `outputs/renders/`.

## Design principles

- Keep formulas readable at the target resolution.
- Use motion to explain structure, not to decorate it.
- Validate mathematical claims before publishing.
- Keep third-party reference media and account-specific branding out of Git history.

See [Automation Integration](docs/automation_integration.md) and [Reference Assets](docs/reference_assets.md).

## License

Licensed under the [Apache License 2.0](LICENSE). Third-party assets remain under their original licenses.
