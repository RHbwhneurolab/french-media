#!/usr/bin/env python3
# TTS generation harness. Reads a manifest of French clips and writes one audio
# file per clip. The ONLY thing you must wire up is `synth()` — the actual call
# to the Qwen TTS that is installed on THIS machine. Everything else (looping,
# naming, skipping already-done clips, output folder) is handled for you.
#
#   python3 generate.py                      # uses test-manifest.json (the 10-clip A/B test)
#   python3 generate.py <manifest.json>      # any manifest with the same shape
#
# Output goes to ./qwen-out/  (filenames come from the manifest — DO NOT rename).
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "test-manifest.json")
OUT_DIR = os.path.join(HERE, "qwen-out")
os.makedirs(OUT_DIR, exist_ok=True)

# Map the manifest's abstract voice roles to REAL voice names available in your
# Qwen TTS install. Use 3 distinct female + 3 distinct male voices if you have them
# (the test only uses f1/m1/f2/m2). Fill these in after you check what's available.
ROLE_TO_VOICE = {
    "f1": "FILL_ME_female_voice_1",
    "m1": "FILL_ME_male_voice_1",
    "f2": "FILL_ME_female_voice_2",
    "m2": "FILL_ME_male_voice_2",
    "f3": "FILL_ME_female_voice_3",
    "m3": "FILL_ME_male_voice_3",
}


def synth(text: str, voice: str, rate_pct: str, out_path: str) -> None:
    """Synthesize `text` (French, fr-FR) with Qwen TTS; write an mp3 to out_path."""
    # >>> WIRE THIS TO THE QWEN TTS ON THIS MACHINE. <<<
    # Two common shapes (use whichever matches your setup); delete the other.
    #
    # --- A) DashScope cloud Qwen-TTS (pip install dashscope; needs DASHSCOPE_API_KEY) ---
    # import dashscope, urllib.request
    # resp = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
    #     model="qwen-tts", text=text, voice=voice)          # voice from ROLE_TO_VOICE
    # data = urllib.request.urlopen(resp.output.audio["url"]).read()
    # open(out_path, "wb").write(data)
    #
    # --- B) A local Qwen/CosyVoice TTS server (adjust host/port/params) ---
    # import urllib.request, json as _j
    # req = urllib.request.Request("http://127.0.0.1:8000/tts",
    #     data=_j.dumps({"text": text, "voice": voice, "language": "fr"}).encode(),
    #     headers={"Content-Type": "application/json"})
    # open(out_path, "wb").write(urllib.request.urlopen(req).read())
    #
    # `rate_pct` (e.g. "-4%") is an OPTIONAL learner slow-down. Apply it if your API
    # has a speed/rate knob; otherwise ignore it (natural pace is acceptable).
    # If the API returns wav, convert to mp3 (e.g. `ffmpeg -i in.wav out_path`).
    raise NotImplementedError(
        "Wire up synth() to the Qwen TTS installed here (see the two examples above), "
        "then re-run. Check `pip list | grep -i dash`, any local TTS server, or the "
        "Qwen TTS README on this machine to see which interface you have.")


def main():
    man = json.load(open(MANIFEST))
    clips = man["clips"]
    done = made = 0
    for c in clips:
        # test-manifest uses `qwen_out`; the full manifest uses `file`
        rel = c.get("qwen_out") or os.path.join("qwen-out", c["file"])
        out_path = os.path.join(HERE, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if os.path.exists(out_path):
            done += 1
            continue
        voice = ROLE_TO_VOICE.get(c.get("role", "f1"), "")
        synth(c["text"], voice, c.get("rate", ""), out_path)
        made += 1
        print(f"  [{made}] {os.path.basename(out_path)}  <- {c['text'][:50]}")
    print(f"\nDONE: generated {made}, already present {done}, total {len(clips)}.")
    print(f"Output in: {OUT_DIR}")
    print("Send that folder back. On the Mac it goes into "
          "source-materials/french/tts-test/qwen-out/ for A/B listening.")


if __name__ == "__main__":
    main()
