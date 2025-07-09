#!/bin/bash

# A shell script to combine a video file and a high-quality audio file
# into a single MP4 optimized for YouTube upload, based on provided guides.

echo "--- YouTube Video & Audio Combiner ---"
echo "This script will combine a video-only .mp4 with a .wav audio file."
echo "Please ensure both files are in the current directory."
echo

# Prompt user for input files
read -p "Enter the full name of the input video file (e.g., video.mp4): " VIDEO_FILE
read -p "Enter the full name of the input audio file (e.g., audio.wav): " AUDIO_FILE
read -p "Enter the desired name for the output file (e.g., output_final.mp4): " OUTPUT_FILE

# --- Pre-flight Checks ---
# Verify that the input files actually exist before attempting to process
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: Video file '$VIDEO_FILE' not found. Please check the filename and try again."
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file '$AUDIO_FILE' not found. Please check the filename and try again."
    exit 1
fi

echo
echo "--- Summary ---"
echo "Video Input: $VIDEO_FILE"
echo "Audio Input: $AUDIO_FILE"
echo "Output File: $OUTPUT_FILE"
echo
echo "Starting FFmpeg process. This may take a significant amount of time..."
echo

# --- FFmpeg Command ---
# This command combines the video and audio streams using settings optimized for quality and YouTube compatibility.
ffmpeg -i "$VIDEO_FILE" -i "$AUDIO_FILE" \
    -map 0:v:0 -map 1:a:0 \
    -c:v libx264 -crf 18 -preset slow -tune film \
    -c:a aac -b:a 384k -ar 48000 \
    -pix_fmt yuv420p \
    -shortest \
    -movflags +faststart \
    "$OUTPUT_FILE"

# --- Completion Message ---
# Check the exit status of the FFmpeg command to confirm success or failure.
if [ $? -eq 0 ]; then
    echo
    echo "Successfully created '$OUTPUT_FILE'!"
else
    echo
    echo "FFmpeg process failed. Please check for errors in the output above."
fi
