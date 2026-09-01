# v4 — make Qwen CALMER / less exaggerated (correction)

Correction on the goal: we want a **neutral, even, un-exaggerated** voice like Azure —
NOT an expressive/warm one. v1 (greedy) was already too theatrical, and v2 (temperature 0.8)
made it worse. So we go the opposite way: **low temperature + a neutral style instruction.**

Do this on the Qwen box:
```
cd tts-job
git pull                 # gets the updated sweep.py + generate.py  (or re-fetch via curl)
python3 sweep.py         # writes qwen-neutral-t00/ (greedy) and qwen-neutral-t20/ (temp 0.2)
git add qwen-neutral-t00 qwen-neutral-t20
git commit -m "Qwen calmness sweep (neutral, low temp)"
git push origin HEAD:tts-jobs
```

**Also, two quick checks that will save round-trips — please report these in your commit
message or a note:**
1. **Does the server actually apply the `instructions` field?** Look at `~/qwen_tts_server.py`.
   If it ignores `instructions`, the neutral prompt does nothing and the exaggeration is
   coming from the **voice model itself** — in that case the fix is a different voice.
2. **What voices are available?** List them (from the server / model). The current set is
   vivian, aiden, serena, dylan. If some voices are calmer/flatter than others, name them —
   we may switch to the most neutral-sounding ones for the whole project.

We'll compare Azure vs these calm variants and lock in the least-exaggerated one for the full run.
