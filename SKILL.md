---
name: audio-transcribe-notes
description: Transcribe local audio/video files with faster-whisper and generate structured Markdown notes. Use when Codex is asked to convert recordings, lectures, meetings, livestreams, MP4/MP3/WAV/M4A audio, or speech-heavy video into text, timestamped transcripts, summaries, study notes, meeting notes, or competition/technical notes.
---

# Audio Transcribe Notes

Use this skill to turn local audio or video into timestamped text and structured Markdown notes. Prefer the bundled script for long recordings because it isolates each chunk in a subprocess and can split failing chunks to avoid native CTranslate2 crashes.

## Workflow

1. Locate the source media file and decide an output prefix in the same folder unless the user asks otherwise.
2. Verify the environment:
   - Prefer Python 3.11 on Windows.
   - Prefer `faster-whisper`, `ctranslate2==4.5.0`, `setuptools<81`, CUDA 12, and cuDNN 9 for GPU.
   - If GPU is requested or available, ensure `cudnn64_9.dll`, `cudnn_ops64_9.dll`, and `cublas64_12.dll` are on `PATH`.
   - Read `references/windows-whisper-gpu.md` if setup or GPU loading fails.
3. Transcribe with `scripts/audio_to_transcript.py`.
   - Use a local faster-whisper model directory when available.
   - Use chunked mode for recordings longer than a few minutes.
   - Keep `.segments.json`, `.txt`, and `.md` outputs.
4. Inspect the transcript for repeated intro/outro/hallucinated filler and domain terms.
5. Generate the final Markdown note by reorganizing the transcript around the user's goal. Include key timestamps and append the full transcript when useful.
6. Verify the final `.md` exists and briefly report paths, model, device, and any caveats.

## Transcription Command

From the folder that contains the media file:

```powershell
.\.venv-whisper-gpu\Scripts\python.exe C:\Users\SXY\.codex\skills\audio-transcribe-notes\scripts\audio_to_transcript.py `
  --input "recording.mp4" `
  --model "D:\SXY\Whisper\.cache\models\faster-whisper-large-v3" `
  --device cuda `
  --chunk-seconds 60 `
  --output-prefix "recording_transcript"
```

If the skill is not installed under `C:\Users\SXY\.codex\skills`, adjust the script path.

Outputs:

- `<prefix>.segments.json`: metadata and structured timestamped segments.
- `<prefix>.txt`: plain timestamped transcript.
- `<prefix>.md`: transcript-only Markdown.
- `<prefix>_chunks/`: per-chunk outputs for recovery and debugging.

## Note Generation Guidance

For technical/lecture/competition recordings, structure the final note around actionable use:

- Topic and purpose.
- Key background.
- Main tasks or workflow.
- Data/schema/interface details.
- Algorithms, constraints, formulas, or implementation advice.
- Risks, pitfalls, and validation checks.
- Key timestamps.
- Full transcript appendix if the user wants traceability or the transcript is the primary deliverable.

Do not blindly summarize repeated filler, intro music, outro text, or obvious hallucinated repeated lines. Mention that the transcript was filtered for note quality if relevant.

## Windows GPU Notes

Use `references/windows-whisper-gpu.md` when:

- `ctranslate2` imports but GPU transcription fails.
- The error mentions `cudnn_ops64_9.dll`, `cudnnCreateTensorDescriptor`, `cublas64_12.dll`, or `access violation`.
- Python 3.13/3.12 causes dependency or native loading problems.
- Long recordings work for 60 seconds but crash for longer clips.

## Fallbacks

- If CUDA fails, retry with `--device cpu --cpu-compute-type int8`; warn that it may be slower.
- If a long clip crashes, keep `--chunk-seconds 60`; the script automatically splits failed chunks down to `--min-chunk-seconds`.
- If model download is slow, ask the user to manually place a faster-whisper model directory locally; do not package large model files in the skill.
