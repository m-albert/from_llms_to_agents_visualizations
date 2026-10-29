#!/usr/bin/env bash
# Render a scene with the light-theme config.
#   ./render.sh <file.py> <SceneName> [manimgl flags...]
# Writes media/<SceneName>/<SceneName>.mp4 (plus stills/ for BuildStills scenes).
# Add e.g. -l (480p), --hd (1080p, default), --uhd (4K).
set -euo pipefail
cd "$(dirname "$0")"

# Use the ffmpeg shipped with imageio-ffmpeg so no system install is needed
if [ ! -x .venv/bin/ffmpeg ]; then
    uv sync
    ln -sf "$(uv run python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" .venv/bin/ffmpeg
fi

PYTHONPATH=. uv run manimgl "$@" -w --video_dir "media/$2"
