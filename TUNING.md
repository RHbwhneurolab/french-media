# v2 — make Qwen sound more natural (re-run the 10-clip test)

Feedback from the A/B: Qwen quality and pace are good, but Azure sounds a **little more
natural**. For LLM-based TTS like Qwen3-TTS, the usual cause is **greedy decoding** (no
sampling) → flat, even prosody. Adding a little sampling temperature restores natural
intonation. I've updated `generate.py` to send sampling params (+ an optional style
instruction). Please do this:

## 1. Confirm the knobs against your server
Open `~/qwen_tts_server.py` (the local Qwen3-TTS server). Check how it accepts generation
params and make `generate.py`'s request match:
- Where do `temperature` / `top_p` go? Top-level of the JSON body, or nested (e.g. an
  `extra_body` / `sampling` / `generation` dict)? Move the `SAMPLING` fields there if needed.
- Does it accept an `instructions` (style) field? If not, drop it (harmless if ignored).
- If it exposes `repetition_penalty`, add ~1.05.
The values I set: `temperature=0.8`, `top_p=0.9`. If 0.8 sounds unstable/mispronounced,
try 0.7; if still flat, try 0.9.

## 2. Regenerate the SAME 10 test clips
The script skips files that already exist, so clear the old ones first:
```
rm -f qwen-out/*.mp3
python3 generate.py
```

## 3. Send back
```
git add -A && git commit -m "Qwen TTS v2 (sampling for naturalness)" && git push origin HEAD:tts-jobs
```
(or tar `qwen-out/` back if this box has no push access).

We'll A/B v2 vs Azure again. Once it's there, the same settings apply to the full ~1,300-clip run.

## Note
Everything else stays the same (voices, 24 kHz mono mp3, natural pace, silence trim). The
only change is turning on sampling so the delivery isn't flat.
