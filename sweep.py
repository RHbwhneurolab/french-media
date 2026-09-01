#!/usr/bin/env python3
# Temperature sweep for the naturalness-vs-pace tradeoff.
#
# v2 (temperature 0.8) sounded more natural than greedy but the PACE became uneven
# (some clips rushed, some slow). Lower temperature keeps most of the naturalness
# with a steadier pace. This reuses generate.py's exact, already-working server
# wiring — it only varies SAMPLING["temperature"] and writes each temp to its own
# folder, so we pick the sweet spot in ONE round-trip.
#
#   python3 sweep.py
import json, os
import generate  # reuses ROLE_TO_VOICE, SAMPLING, synth() — importing does NOT run its main()

HERE = os.path.dirname(os.path.abspath(__file__))
man = json.load(open(os.path.join(HERE, "test-manifest.json")))
TEMPS = [0.5, 0.65]   # greedy(≈0)=qwen-v1 and 0.8=qwen-v2 already exist; this fills the gap

for t in TEMPS:
    generate.SAMPLING["temperature"] = t          # top_p stays 0.9 (from generate.py)
    out_dir = os.path.join(HERE, f"qwen-t{int(round(t * 100))}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n=== temperature {t} -> {os.path.basename(out_dir)}/ ===")
    for c in man["clips"]:
        out_path = os.path.join(out_dir, f"{c['id']}.mp3")
        if os.path.exists(out_path):
            continue
        voice = generate.ROLE_TO_VOICE.get(c.get("role", "f1"), "")
        generate.synth(c["text"], voice, c.get("rate", ""), out_path)
        print(f"  {c['id']}.mp3")

print("\nDONE. Commit qwen-t50/ and qwen-t65/ and push:")
print("  git add qwen-t50 qwen-t65 && git commit -m 'Qwen temp sweep 0.5/0.65' && git push origin HEAD:tts-jobs")
