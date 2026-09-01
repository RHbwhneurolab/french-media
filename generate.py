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
    "f1": "vivian",
    "m1": "aiden",
    "f2": "serena",
    "m2": "dylan",
    "f3": "sohee",
    "m3": "eric",
}

# Local Qwen3-TTS server set up on this box (see ~/qwen_tts_server.py /
# ~/start-qwen3-tts-server.sh): OpenAI-speech-shaped API, CustomVoice-0.6B on GPU.
TTS_URL = "http://127.0.0.1:8001/v1/audio/speech"

# --- NATURALNESS TUNING (v2) -------------------------------------------------
# The first pass sounded a touch flat vs Azure. LLM-based TTS (like Qwen3-TTS)
# sounds noticeably more natural with a little sampling instead of greedy decode.
# These get added to the request below. **Check ~/qwen_tts_server.py for the exact
# field names / where they belong** (top-level vs an "extra_body"/"sampling" dict)
# and adjust if the server ignores them — the goal is: sampling ON, ~0.8 temp.
# CHOSEN CONFIG for the full run = the "neutral-t00" variant (approved).
# Greedy (temperature 0) + neutral instruction = calm, even, un-exaggerated delivery.
# repetition_penalty 1.3 prevents the greedy loop/repeat bug. If your server takes
# repetition_penalty somewhere other than the request body (as you wired for the
# sweep), apply it the same way here so the full run matches neutral-t00 exactly.
SAMPLING = {
    "temperature": 0.0,
    "top_p": 0.9,
    "repetition_penalty": 1.3,
}
# Goal: NEUTRAL, even, un-exaggerated delivery (Azure-like), NOT expressive/warm.
# If the server honors an OpenAI-style `instructions` field, this pushes it calmer;
# harmless if ignored. Keep it in French.
STYLE_INSTRUCTIONS = "Lis d'une voix neutre et posée, à un rythme régulier, sans emphase ni intonation exagérée, sur un ton informatif et calme."

import subprocess, tempfile, urllib.request
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()  # static binary; no system ffmpeg/sudo needed


def synth(text: str, voice: str, rate_pct: str, out_path: str) -> None:
    """Synthesize `text` (French, fr-FR) with the local Qwen3-TTS server; write an mp3 to out_path."""
    payload = {
        "model": "qwen3-tts-customvoice",
        "input": text,
        "voice": voice,
        "language": "french",
        "instructions": STYLE_INSTRUCTIONS,   # ignored by servers that don't support it
    }
    payload.update(SAMPLING)                   # temperature/top_p for natural prosody
    req = urllib.request.Request(
        TTS_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    wav_bytes = urllib.request.urlopen(req, timeout=120).read()
    # rate_pct: this API has no speed/rate knob, so it's ignored (natural pace) as
    # BOT-INSTRUCTIONS.md allows.
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tf.write(wav_bytes)
        wav_path = tf.name
    try:
        subprocess.run([
            FFMPEG, "-y", "-i", wav_path,
            "-af", "silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB:detection=peak,"
                   "areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB:detection=peak,areverse",
            "-ac", "1", "-ar", "24000", "-codec:a", "libmp3lame", "-qscale:a", "4",
            out_path,
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    finally:
        os.unlink(wav_path)


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
