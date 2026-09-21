#!/usr/bin/env python3
"""
Расшифровка аудио/видео в текст локально, через faster-whisper.

Установка:
    pip install faster-whisper
    (нужен ffmpeg в системе: https://ffmpeg.org/download.html)

Запуск:
    python transcribe.py рыб1.mp3
    python transcribe.py рыб1.mp3 --model large-v3
    python transcribe.py видео.mp4 --model medium --lang ru

На выходе рядом с исходником появятся:
    рыб1.timecodes.txt  — текст с таймкодами
    рыб1.txt            — сплошной текст, абзацами
    рыб1.srt            — субтитры
"""

import argparse
import sys
from pathlib import Path


def hhmmss(seconds: float, srt: bool = False) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if srt:
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def pick_device(requested: str):
    if requested != "auto":
        return requested, ("float16" if requested == "cuda" else "int8")
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"


def main():
    p = argparse.ArgumentParser(description="Локальная расшифровка через faster-whisper")
    p.add_argument("audio", help="путь к аудио- или видеофайлу")
    p.add_argument("--model", default="large-v3",
                   help="tiny | base | small | medium | large-v3 (по умолчанию large-v3)")
    p.add_argument("--lang", default="ru", help="код языка, или 'auto' для автоопределения")
    p.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    p.add_argument("--outdir", default=None, help="куда класть результат (по умолчанию рядом с файлом)")
    args = p.parse_args()

    src = Path(args.audio).expanduser().resolve()
    if not src.exists():
        sys.exit(f"Файл не найден: {src}")

    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else src.parent
    outdir.mkdir(parents=True, exist_ok=True)
    stem = src.stem

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("Не установлен faster-whisper. Выполните: pip install faster-whisper")

    device, compute_type = pick_device(args.device)
    print(f"Устройство: {device} ({compute_type})")
    print(f"Модель: {args.model} — первая загрузка скачает веса, это разово.")

    model = WhisperModel(args.model, device=device, compute_type=compute_type)

    segments, info = model.transcribe(
        str(src),
        language=None if args.lang == "auto" else args.lang,
        beam_size=5,
        vad_filter=True,                       # выкидывает тишину, ускоряет и убирает галлюцинации
        vad_parameters={"min_silence_duration_ms": 500},
        condition_on_previous_text=False,      # меньше зацикливаний на длинных записях
    )

    total = info.duration
    print(f"Язык: {info.language} (уверенность {info.language_probability:.2f})")
    print(f"Длительность: {hhmmss(total)}\n")

    f_tc = open(outdir / f"{stem}.timecodes.txt", "w", encoding="utf-8")
    f_txt = open(outdir / f"{stem}.txt", "w", encoding="utf-8")
    f_srt = open(outdir / f"{stem}.srt", "w", encoding="utf-8")

    paragraph, last_end, idx = [], 0.0, 0
    try:
        for seg in segments:
            idx += 1
            text = seg.text.strip()
            if not text:
                continue

            f_tc.write(f"[{hhmmss(seg.start)} → {hhmmss(seg.end)}] {text}\n")
            f_srt.write(f"{idx}\n{hhmmss(seg.start, True)} --> {hhmmss(seg.end, True)}\n{text}\n\n")

            # новый абзац после паузы длиннее 2 секунд
            if paragraph and seg.start - last_end > 2.0:
                f_txt.write(" ".join(paragraph) + "\n\n")
                paragraph = []
            paragraph.append(text)
            last_end = seg.end

            pct = min(100, seg.end / total * 100) if total else 0
            print(f"\r{pct:5.1f}%  {hhmmss(seg.end)} / {hhmmss(total)}", end="", flush=True)

        if paragraph:
            f_txt.write(" ".join(paragraph) + "\n")
    finally:
        for f in (f_tc, f_txt, f_srt):
            f.close()

    print(f"\n\nГотово. Файлы в {outdir}:")
    for suffix in (".timecodes.txt", ".txt", ".srt"):
        print(f"  {stem}{suffix}")


if __name__ == "__main__":
    main()
