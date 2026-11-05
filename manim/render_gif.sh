#!/usr/bin/env bash
# Render a scene at 1080p and create a high quality gif.
#   ./render_gif.sh <file.py> <SceneName> [gif width, default 1920]
# Writes media/<SceneName>/<SceneName>.mp4 and .gif (plus stills/). Both are
# encoded from a lossless render, which keeps thin text crisp in the gif.
set -euo pipefail
cd "$(dirname "$0")"

scene_dir="media/$2"
lossless="$scene_dir/$2_lossless.mp4"
width="${3:-1920}"

./render.sh "$1" "$2" --hd --vcodec libx264rgb --pix_fmt rgb24 --config_file lossless_config.yml
mv "$scene_dir/$2.mp4" "$lossless"

.venv/bin/ffmpeg -y -v error -i "$lossless" -c:v libx264 -crf 16 -pix_fmt yuv420p "$scene_dir/$2.mp4"
.venv/bin/ffmpeg -y -v error -i "$lossless" -loop 0 -filter_complex \
    "scale=$width:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
    "$scene_dir/$2.gif"
rm "$lossless"
