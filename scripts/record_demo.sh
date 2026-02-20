#!/bin/bash
# Record a demo GIF of the Streamlit app using macOS screen recording + ffmpeg
#
# Prerequisites:
#   brew install ffmpeg
#
# Usage:
#   1. Start the app:  streamlit run app.py
#   2. Open http://localhost:8501 in your browser
#   3. Run this script:  ./scripts/record_demo.sh
#   4. Perform the demo actions in your browser (30 seconds)
#   5. Press Ctrl+C to stop recording
#
# Alternatively, use macOS built-in screen recording:
#   1. Cmd+Shift+5 → Record selected portion
#   2. Record yourself clicking through the demo
#   3. Convert to GIF:
#      ffmpeg -i demo.mov -vf "fps=10,scale=800:-1:flags=lanczos" -loop 0 docs/demo.gif

set -e

OUTPUT_DIR="docs"
OUTPUT_FILE="$OUTPUT_DIR/demo.gif"
TEMP_VIDEO="/tmp/reddit_goldmine_demo.mov"

echo "=== Reddit Goldmine Analyzer — Demo GIF Recorder ==="
echo ""
echo "Option 1: Automatic (requires ffmpeg)"
echo "  This will capture a 30-second screen recording."
echo ""
echo "Option 2: Manual (recommended for best quality)"
echo "  1. Use Cmd+Shift+5 to record your screen"
echo "  2. Navigate the app: Sample Data → click pain points → scroll"
echo "  3. Save the recording as docs/demo.mov"
echo "  4. Run: ffmpeg -i docs/demo.mov -vf 'fps=10,scale=800:-1:flags=lanczos' -loop 0 docs/demo.gif"
echo ""
echo "Suggested demo flow (30 seconds):"
echo "  1. Show the main page (2s)"
echo "  2. Click 'Sample Data' tab (2s)"
echo "  3. Select a sample dataset (3s)"
echo "  4. Scroll through pain points (5s)"
echo "  5. Expand an example comment (3s)"
echo "  6. Show the Discover tab (5s)"
echo "  7. Switch language to Japanese and back (5s)"
echo "  8. Show the download button (3s)"
echo ""

if command -v ffmpeg &> /dev/null && [ -f "$TEMP_VIDEO" ]; then
    echo "Converting $TEMP_VIDEO to GIF..."
    ffmpeg -i "$TEMP_VIDEO" \
        -vf "fps=10,scale=800:-1:flags=lanczos" \
        -loop 0 \
        "$OUTPUT_FILE"
    echo "Done! GIF saved to $OUTPUT_FILE"
    echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
else
    echo "No video file found at $TEMP_VIDEO"
    echo "Record your screen first, then run this script again."
    echo ""
    echo "Quick convert command:"
    echo "  ffmpeg -i YOUR_VIDEO.mov -vf 'fps=10,scale=800:-1:flags=lanczos' -loop 0 docs/demo.gif"
fi
