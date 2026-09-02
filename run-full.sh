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
  pkill -f "uvicorn qwen_tts_server" 2>/dev/null
  sleep 3
  nohup /home/neurolab/start-qwen3-tts-server.sh > "$STARTLOG" 2>&1 &
  disown
  until curl -s -m 2 http://localhost:8001/health > /dev/null 2>&1; do sleep 2; done
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
