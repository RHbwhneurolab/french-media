# v3 — temperature sweep (pick the pace/naturalness sweet spot)

Measured result from v2: temperature **0.8** made the pace **uneven** (some clips rushed,
some slow) — pace spread was wider than both Azure and greedy. We want a lower temperature:
still more natural than greedy, but steady pace.

Do this on the Qwen box:

```
cd tts-job        # (the folder you cloned; or wherever generate.py lives)
git pull          # gets sweep.py + this file   (or re-fetch via curl)
python3 sweep.py  # generates the 10 clips at temperature 0.5 and 0.65 into qwen-t50/ and qwen-t65/
git add qwen-t50 qwen-t65
git commit -m "Qwen temp sweep 0.5/0.65"
git push origin HEAD:tts-jobs
```

`sweep.py` reuses your existing `generate.py` wiring (same server call, same voices) and only
changes the temperature. It skips clips already generated, so it's safe to re-run.

We'll then compare Azure vs temp 0 / 0.5 / 0.65 / 0.8 side by side and lock the winner in for
the full ~1,300-clip run.
