#!/bin/bash
# Self-healing wrapper for the full audio-manifest.json run. The TTS server has been
# observed to develop a GPU-memory creep over ~7h of continuous use (this box's headroom
# is razor-thin, shared with an always-on 35B LLM server) that eventually wedges it into
# failing every request. generate.py already tolerates per-clip failures and is fully
# resumable (skips existing files), so: restart the server fresh, run generate.py to
# completion, and if anything failed, restart again and retry. Repeat until a pass
# completes with zero failures, or MAX_ROUNDS is hit.
set -uo pipefail
cd /home/neurolab/tts-job
MAX_ROUNDS=15
STARTLOG=/home/neurolab/qwen3-tts-server.log
RUNLOG=/home/neurolab/tts-job/full-run.log

restart_server() {
  pkill -9 -f "uvicorn qwen_tts_server" 2>/dev/null
  # Wait for the old process to actually be gone AND its GPU memory to actually be
  # reclaimed before starting a new one — pkill returns before the process (and its
  # CUDA context) is fully torn down, and this box's headroom (~800MB-1GB after model
  # load) is too thin to tolerate two instances resident at once, even briefly (that
  # caused a startup-OOM crash once already).
  for _ in $(seq 1 30); do
    pgrep -f "uvicorn qwen_tts_server" > /dev/null || break
    sleep 1
  done
  for _ in $(seq 1 30); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits)
    [ "$free" -gt 3000 ] && break
    sleep 1
  done
  nohup /home/neurolab/start-qwen3-tts-server.sh > "$STARTLOG" 2>&1 &
  disown
  # Bound the wait: if the new process dies on startup (e.g. still-tight memory), retry
  # the whole kill+wait+start cycle instead of looping forever on a dead process.
  for _ in $(seq 1 60); do
    curl -s -m 2 http://localhost:8001/health > /dev/null 2>&1 && return 0
    pgrep -f "uvicorn qwen_tts_server" > /dev/null || break  # died on startup, retry
    sleep 2
  done
  echo "restart_server: attempt failed, retrying" | tee -a "$RUNLOG"
  restart_server
}

for round in $(seq 1 "$MAX_ROUNDS"); do
  echo "=== ROUND $round: restarting server ===" | tee -a "$RUNLOG"
  restart_server
  echo "=== ROUND $round: running generate.py ===" | tee -a "$RUNLOG"
  /home/neurolab/qwen-tts-env/bin/python generate.py audio-manifest.json >> "$RUNLOG" 2>&1
  failed=$(tail -20 "$RUNLOG" | grep -oP 'failed \K[0-9]+' | tail -1)
  echo "=== ROUND $round: failed=${failed:-unknown} ===" | tee -a "$RUNLOG"
  if [ "${failed:-1}" = "0" ]; then
    echo "ALL_ROUNDS_CLEAN" | tee -a "$RUNLOG"
    break
  fi
done
