#!/usr/bin/env python3
# CALMNESS sweep. Correction: the goal is a NEUTRAL, even, un-exaggerated voice
# (Azure-like) — NOT expressive. v1 (greedy) was already too theatrical and v2
# (temp 0.8) was worse. So we go the OTHER way: low temperature + a neutral style
# instruction. This produces two variants so we can pick the calmest:
#   qwen-neutral-t00/  temperature 0.0 (greedy)  + neutral instruction
#   qwen-neutral-t20/  temperature 0.2           + neutral instruction
# Reuses generate.py's working server wiring; only overrides the style + temperature.
#   python3 sweep.py
import json, os
import generate  # importing does NOT run its main()

HERE = os.path.dirname(os.path.abspath(__file__))
man = json.load(open(os.path.join(HERE, "test-manifest.json")))

# Force the neutral, un-exaggerated delivery for this whole sweep.
generate.STYLE_INSTRUCTIONS = ("Lis d'une voix neutre et posee, a un rythme regulier, "
                               "sans emphase ni intonation exageree, sur un ton informatif et calme.")

VARIANTS = [("qwen-neutral-t00", 0.0), ("qwen-neutral-t20", 0.2)]

for folder, temp in VARIANTS:
    if temp == 0.0:
        # True greedy decoding: temperature=0.0 with sampling still on is invalid
        # (the server's underlying transformers .generate() raises a ValueError:
        # "temperature has to be a strictly positive float ... set do_sample=False").
        generate.SAMPLING.pop("temperature", None)
        generate.SAMPLING["do_sample"] = False
    else:
        # BUG FOUND + FIXED: temperature=0.2 with no repetition_penalty caused runaway
        # non-terminating generation (a 2-word phrase came out 24s long, ~20x too long;
        # a longer sentence blew past a 120s client timeout). repetition_penalty=1.3
        # fixes it cleanly — verified against both the short phrase (1.68s vs greedy's
        # 1.13s) and the long sentence that originally hung (13.6s vs greedy's 14.14s).
        generate.SAMPLING.pop("do_sample", None)
        generate.SAMPLING["temperature"] = temp
        generate.SAMPLING["repetition_penalty"] = 1.3
    out_dir = os.path.join(HERE, folder)
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n=== {folder}/  (temperature {temp}, neutral instruction) ===")
    for c in man["clips"]:
        out_path = os.path.join(out_dir, f"{c['id']}.mp3")
        if os.path.exists(out_path):
            continue
        voice = generate.ROLE_TO_VOICE.get(c.get("role", "f1"), "")
        generate.synth(c["text"], voice, c.get("rate", ""), out_path)
        print(f"  {c['id']}.mp3")

print("\nDONE. Then:")
print("  git add qwen-neutral-t00 qwen-neutral-t20")
print("  git commit -m 'Qwen calmness sweep (neutral, low temp)' && git push origin HEAD:tts-jobs")
