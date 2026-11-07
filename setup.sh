#!/usr/bin/env bash
# One-time setup for a fresh machine/cloud session: Python packages + ffmpeg,
# and the voice/music separation model (only needed to analyse new reference videos).
set -e
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg libcairo2-dev pkg-config)
# Style B text uses Inter Black / Inter Display Black (open-source); cairo falls back to a plain sans without it
fc-list | grep -q "Inter Display" || (apt-get update -qq && apt-get install -y -qq fonts-inter) || true
# thumbnail headline font (Luckiest Guy, SIL Open Font License, from Google Fonts); thumbkit.py falls back to Inter
fc-list | grep -q "Luckiest Guy" || (mkdir -p ~/.local/share/fonts && curl -sSL -o ~/.local/share/fonts/LuckiestGuy-Regular.ttf \
  "$(curl -sSL 'https://fonts.googleapis.com/css2?family=Luckiest+Guy' | grep -o 'https://fonts.gstatic.com[^)]*' | tail -1)" \
  && fc-cache -f >/dev/null) || true
pip install -q -r requirements.txt
mkdir -p analysis/models
[ -f analysis/models/UVR-MDX-NET-Inst_HQ_3.onnx ] || curl -sSL -o analysis/models/UVR-MDX-NET-Inst_HQ_3.onnx \
  https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_HQ_3.onnx
python3 -c "import cairo, cv2, librosa, onnxruntime, pocketsphinx; print('setup ok')"
