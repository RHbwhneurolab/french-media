# Instructions for the Claude bot on the Qwen-TTS workstation

You are on a headless workstation that has **Qwen TTS** installed. Your job: generate
**French (fr-FR) speech clips** from a list of text, then hand the folder back. You do
NOT need to listen to anything — the person will compare quality on another machine.

This folder is self-contained. You need nothing from any other repo.

## Goal
Produce 10 mp3 files (one per entry in `test-manifest.json`) in `qwen-out/`, named
EXACTLY as the manifest says. This is a small **quality test** before a larger ~1,300-clip
run, so make them representative of your best default settings.

## Step 1 — Find out how Qwen TTS is invoked here
You have a shell. Discover the interface, e.g.:
- `pip list 2>/dev/null | grep -iE "dashscope|qwen|cosyvoice|tts"`
- look for a local TTS server / model dir / example script in the home dir or repo here
- check for an API key: `env | grep -i dash`
- read any Qwen-TTS README/example on this machine
Determine: is it the **DashScope cloud API** (`model=qwen-tts`), or a **local server/model**?
Also list the available **voice names** (you'll need 2 female + 2 male for this test).

## Step 2 — Wire up the generator
Open `generate.py`. Do two things:
1. Fill in `ROLE_TO_VOICE` with real voice names you found (f1/m1/f2/m2 are used in this test).
2. Implement the `synth(text, voice, rate_pct, out_path)` function — there are two worked
   examples in the file (DashScope cloud, or a local server). Keep the one that matches your
   setup, wire it to actually call Qwen, and write an **mp3** to `out_path`. If Qwen returns
   wav, convert to mp3 (`ffmpeg -i in.wav out_path`).
   - `rate_pct` (like `-4%`) is an OPTIONAL gentle slow-down for learners. Apply it if your
     API has a speed/rate knob; otherwise ignore it (natural pace is fine).
   - Mono, ~24 kHz, trim long leading/trailing silence.

## Step 3 — Run it
```
python3 generate.py
```
It reads `test-manifest.json`, calls your `synth()` for each clip, and writes to `qwen-out/`.
It skips any clip already generated, so you can re-run safely.

## Step 4 — Send the results back
You cloned this from GitHub (branch `tts-jobs` of `RHbwhneurolab/french-media`). Return the
audio the same way if this box has push access:
```
git add qwen-out
git commit -m "Qwen TTS test output (10 clips)"
git push origin HEAD:tts-jobs
```
If this box has NO push credentials, tar the output and send it back by any means:
```
tar -czf qwen-out.tar.gz -C qwen-out .
```
Either way, the person pulls `qwen-out/` onto the Mac and A/B-compares against the Azure
originals. That's it.

## What each manifest entry means
```json
{ "id":"test01-vocab", "text":"le quartier", "rate":"-6%", "role":"f1",
  "qwen_out":"qwen-out/test01-vocab.mp3" }
```
- `text` — the French to synthesize.
- `rate` — optional slow-down hint (`-6%` short words, `-4%` sentences).
- `role` — voice slot → map via `ROLE_TO_VOICE`.
- `qwen_out` — the exact output path/filename. **Do not rename.**
(Ignore `azure_reference` — that's the comparison file, used only on the other machine.)

## Notes
- Treat `text` as plain text (no SSML).
- If a clip fails, keep going; just report which ids failed at the end.
- Once this 10-clip test is approved, the same `generate.py` will run against the full
  `audio-manifest.json` (~1,300 clips) with no changes needed.
```
