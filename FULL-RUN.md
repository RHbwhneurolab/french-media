# Full run — generate all French audio (approved config: neutral-t00)

The 10-clip test is approved. Voice config locked to **neutral-t00**: greedy
(temperature 0) + the neutral French style instruction + repetition_penalty 1.3.
`generate.py` is already set to this. Now generate the whole content set.

## Steps
```
cd tts-job
git pull                                 # gets audio-manifest.json + the final generate.py
python3 generate.py audio-manifest.json  # ~2000 clips -> qwen-out/<content-hash>.mp3
```
- `audio-manifest.json` has ~2,043 clips. Each: `file` (exact output name — content hash,
  DO NOT rename), `text` (French), `rate` (ignore — server has no speed knob), `role`
  (f1/m1/f2/m2/f3/m3 → your voice map). Output goes to `qwen-out/<file>`.
- The script **skips files already generated**, so it's fully resumable — if it dies or
  you stop it, just run it again and it continues.
- This will take a while and produce ~60–120 MB of mp3. Mono, 24 kHz, as before.

## Send back (in batches is fine)
```
git add qwen-out
git commit -m "Qwen full run (neutral-t00) — <N> clips"
git push origin HEAD:tts-jobs
```
You can commit/push partway through and again at the end — the Mac side is incremental
and only pulls what's new. If push isn't available, tar `qwen-out/` and send it.

## Notes
- Keep `generate.py` as-is (temperature 0, repetition_penalty 1.3, neutral instruction).
  If you hear any clip loop/repeat a word, that clip can be re-run; delete it from
  qwen-out and run again.
- When everything's in, the Mac stages the clips and publishes them to the CDN; the app
  already references these exact filenames, so audio just turns on across the French app.
