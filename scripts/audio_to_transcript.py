from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_PROMPT = (
    "这是一段中文录音，可能包含会议、课程、直播、技术讲解、竞赛说明、"
    "业务背景、数据、算法、约束、流程和问答。"
)


def format_timestamp(seconds: float) -> str:
    total_ms = int(round(max(0.0, float(seconds)) * 1000))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def clean_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def media_duration(path: Path) -> float:
    import av

    with av.open(str(path)) as container:
        if container.duration:
            return float(container.duration / av.time_base)
        durations = []
        for stream in container.streams:
            if stream.duration and stream.time_base:
                durations.append(float(stream.duration * stream.time_base))
        if durations:
            return max(durations)
    raise RuntimeError(f"Could not determine media duration: {path}")


def write_outputs(output_prefix: Path, metadata: dict[str, Any], segments: list[dict[str, Any]]) -> None:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".segments.json")
    txt_path = output_prefix.with_suffix(".txt")
    md_path = output_prefix.with_suffix(".md")

    json_path.write_text(
        json.dumps({"metadata": metadata, "segments": segments}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    txt_path.write_text(
        "\n".join(f"[{s['start_text']} --> {s['end_text']}] {s['text']}" for s in segments) + "\n",
        encoding="utf-8",
    )
    lines = ["# Transcript", "", "## Segments", ""]
    lines.extend(f"- [{s['start_text']} - {s['end_text']}] {s['text']}" for s in segments)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def worker(args: argparse.Namespace) -> int:
    from faster_whisper import WhisperModel

    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.cuda_compute_type if args.device == "cuda" else args.cpu_compute_type,
        local_files_only=args.local_files_only,
    )

    segments_iter, info = model.transcribe(
        str(args.input),
        language=args.language,
        task="transcribe",
        beam_size=args.beam_size,
        vad_filter=args.vad_filter,
        word_timestamps=False,
        condition_on_previous_text=True,
        clip_timestamps=[float(args.clip_start), float(args.clip_end)],
        initial_prompt=args.initial_prompt,
    )

    segments: list[dict[str, Any]] = []
    for segment in segments_iter:
        text = clean_text(segment.text)
        if not text:
            continue
        start = float(segment.start)
        end = float(segment.end)
        segments.append(
            {
                "index": len(segments) + 1,
                "start": start,
                "end": end,
                "start_text": format_timestamp(start),
                "end_text": format_timestamp(end),
                "text": text,
            }
        )

    metadata = {
        "input": str(args.input.resolve()),
        "model": args.model,
        "device": args.device,
        "compute_type": args.cuda_compute_type if args.device == "cuda" else args.cpu_compute_type,
        "language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "clip_start": args.clip_start,
        "clip_end": args.clip_end,
    }
    write_outputs(args.output_prefix, metadata, segments)
    print(json.dumps({"segments": len(segments), "output_prefix": str(args.output_prefix)}, ensure_ascii=False), flush=True)
    return 0


def run_chunk(args: argparse.Namespace, start: float, end: float, prefix: Path, depth: int = 0) -> None:
    existing = sorted(prefix.parent.glob(prefix.name + "*.segments.json"))
    if existing:
        print(f"SKIP {prefix.name}: {start:.1f}-{end:.1f}s", flush=True)
        return

    print(f"RUN {prefix.name}: {start:.1f}-{end:.1f}s", flush=True)
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--input",
        str(args.input),
        "--model",
        args.model,
        "--device",
        args.device,
        "--clip-start",
        str(start),
        "--clip-end",
        str(end),
        "--output-prefix",
        str(prefix),
        "--language",
        args.language,
        "--beam-size",
        str(args.beam_size),
        "--cuda-compute-type",
        args.cuda_compute_type,
        "--cpu-compute-type",
        args.cpu_compute_type,
        "--initial-prompt",
        args.initial_prompt,
    ]
    if args.no_vad_filter:
        cmd.append("--no-vad-filter")
    if args.local_files_only:
        cmd.append("--local-files-only")

    env = os.environ.copy()
    if args.prepend_path:
        env["PATH"] = args.prepend_path + os.pathsep + env.get("PATH", "")

    result = subprocess.run(cmd, cwd=str(Path.cwd()), env=env)
    if result.returncode == 0:
        return

    duration = end - start
    if duration <= args.min_chunk_seconds or depth >= args.max_split_depth:
        raise RuntimeError(f"Chunk {prefix} failed with exit code {result.returncode}")

    midpoint = start + duration / 2.0
    print(f"SPLIT {prefix.name}: exit {result.returncode}, duration {duration:.1f}s", flush=True)
    run_chunk(args, start, midpoint, prefix.with_name(prefix.name + "_a"), depth + 1)
    run_chunk(args, midpoint, end, prefix.with_name(prefix.name + "_b"), depth + 1)


def combine_chunks(chunk_dir: Path, output_prefix: Path) -> None:
    segments: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}

    for path in sorted(chunk_dir.glob("chunk_*.segments.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        metadata = data.get("metadata") or metadata
        for segment in data.get("segments", []):
            text = clean_text(segment.get("text", ""))
            if not text:
                continue
            start = float(segment["start"])
            end = float(segment["end"])
            if segments and abs(start - segments[-1]["start"]) < 0.01 and text == segments[-1]["text"]:
                continue
            segments.append(
                {
                    "index": len(segments) + 1,
                    "start": start,
                    "end": end,
                    "start_text": format_timestamp(start),
                    "end_text": format_timestamp(end),
                    "text": text,
                }
            )

    if not segments:
        raise RuntimeError(f"No chunk transcripts found in {chunk_dir}")

    write_outputs(output_prefix, metadata, segments)
    print(json.dumps({"segments": len(segments), "output_prefix": str(output_prefix.resolve())}, ensure_ascii=False), flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chunked faster-whisper transcription for audio/video files.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", required=True, help="faster-whisper model name or local model directory")
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--chunk-seconds", type=float, default=60.0)
    parser.add_argument("--min-chunk-seconds", type=float, default=15.0)
    parser.add_argument("--max-split-depth", type=int, default=3)
    parser.add_argument("--clip-start", type=float, default=None)
    parser.add_argument("--clip-end", type=float, default=None)
    parser.add_argument("--cuda-compute-type", default="int8_float16")
    parser.add_argument("--cpu-compute-type", default="int8")
    parser.add_argument("--initial-prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--no-vad-filter", action="store_true")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--prepend-path", default=None, help="Optional PATH prefix for CUDA/cuDNN DLL directories")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.input = args.input.resolve()
    args.output_prefix = args.output_prefix.resolve()
    if not args.input.exists():
        raise FileNotFoundError(args.input)

    if args.worker:
        return worker(args)

    duration = media_duration(args.input)
    start = 0.0 if args.clip_start is None else args.clip_start
    end = duration if args.clip_end is None else min(args.clip_end, duration)
    chunk_dir = args.output_prefix.with_name(args.output_prefix.name + "_chunks")
    chunk_dir.mkdir(parents=True, exist_ok=True)

    index = 0
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + args.chunk_seconds, end)
        prefix = chunk_dir / f"chunk_{index:04d}"
        run_chunk(args, cursor, chunk_end, prefix)
        cursor = chunk_end
        index += 1

    combine_chunks(chunk_dir, args.output_prefix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
