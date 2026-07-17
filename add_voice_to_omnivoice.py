import argparse
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path


K2FSA_OMNIVOICE_ROOT = Path(
    os.environ.get("K2FSA_OMNIVOICE_ROOT", os.path.expanduser("~/k2fsa-omnivoice311"))
)
K2FSA_OMNIVOICE_DATA_DIR = Path(
    os.environ.get("K2FSA_OMNIVOICE_DATA_DIR", os.path.expanduser("~/k2fsa-omnivoice-data"))
)
VOICES_DIR = K2FSA_OMNIVOICE_DATA_DIR / "voices"
VOICE_PROFILES_DIR = K2FSA_OMNIVOICE_DATA_DIR / "voice_profiles"
MLX_WHISPER_BIN = K2FSA_OMNIVOICE_ROOT / ".venv" / "bin" / "mlx_whisper"


def extract_audio(video_path, output_wav):
    print(f"Extracting 15s audio clip from {video_path}...")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ss",
        "00:00:10",
        "-t",
        "15",
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "24000",
        "-ac",
        "1",
        output_wav,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Audio extracted successfully.")


def transcribe_clip(audio_path, model):
    print("Transcribing audio using mlx_whisper...")
    if not MLX_WHISPER_BIN.exists():
        raise FileNotFoundError(f"mlx_whisper not found at {MLX_WHISPER_BIN}")

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            str(MLX_WHISPER_BIN),
            audio_path,
            "--model",
            model,
            "--language",
            "vi",
            "--output-dir",
            tmpdir,
            "--output-format",
            "txt",
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        txt_path = Path(tmpdir) / f"{Path(audio_path).stem}.txt"
        if not txt_path.exists():
            print("Warning: Could not transcribe any text from the audio. Proceeding with empty text.")
            return ""
        text = txt_path.read_text(encoding="utf-8").strip()
        print(f"Transcription: {text}")
        return text


def add_voice_profile(name, ref_audio_src, ref_text):
    profile_id = str(uuid.uuid4())[:8]
    ext = Path(ref_audio_src).suffix or ".wav"
    audio_filename = f"{profile_id}{ext}"

    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    VOICE_PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    audio_dest = VOICES_DIR / audio_filename
    shutil.copy2(ref_audio_src, audio_dest)
    print(f"Copied audio to {audio_dest}")

    profile = {
        "id": profile_id,
        "name": name,
        "engine": "k2-fsa/OmniVoice",
        "ref_audio": str(audio_dest),
        "ref_text": ref_text,
        "language_id": "vi",
        "created_from": "add_voice_to_omnivoice.py",
    }
    profile_path = VOICE_PROFILES_DIR / f"{name}.json"
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved voice profile to {profile_path}")


def main():
    parser = argparse.ArgumentParser(description="Create a local k2-fsa OmniVoice voice profile.")
    parser.add_argument("input", help="Input video or wav file.")
    parser.add_argument("--voice-name", required=True, help="Voice profile name.")
    parser.add_argument(
        "--model",
        default="mlx-community/whisper-large-v3-turbo",
        help="mlx_whisper model used to transcribe the reference clip.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        if input_path.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
            ref_audio = str(input_path)
        else:
            ref_audio = str(Path(tmpdir) / "omnivoice_temp_ref.wav")
            extract_audio(str(input_path), ref_audio)
        transcript = transcribe_clip(ref_audio, args.model)
        add_voice_profile(args.voice_name, ref_audio, transcript)


if __name__ == "__main__":
    main()
