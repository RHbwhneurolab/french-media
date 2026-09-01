# Qwen TTS — quality A/B test kit

## ⇒ If you are the bot on the Qwen workstation: read **BOT-INSTRUCTIONS.md** and follow it.

That file is a complete, standalone walkthrough: find your Qwen TTS interface, wire it
into `generate.py` (one small function), run it, send `qwen-out/` back. You need nothing
else and no other repo.

## Files here
- **BOT-INSTRUCTIONS.md** — start here (for the generation bot).
- **generate.py** — the harness; you only fill in the `synth()` call to Qwen + the voice names.
- **test-manifest.json** — the 10 French clips to generate (id, text, rate, role, output path).
- **azure-reference/** — the current Azure clips (.m4a). Comparison files for the OTHER machine; ignore during generation, do not overwrite.
- **qwen-out/** — where generated .mp3 go (created by `generate.py`).

## The point
Generate these 10 clips with Qwen, send them back, and we compare Qwen vs Azure side by side
on the Mac before committing to the full ~1,300-clip run.
