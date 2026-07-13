import os
import sys
import uuid
import time
import shutil
import sqlite3
import subprocess

sys.path.insert(0, '/Users/truongdv/omnivoice-env/project/backend')
from core.config import DB_PATH, VOICES_DIR

def extract_audio(video_path, output_wav):
    print(f"Extracting 15s audio clip from {video_path}...")
    # Extract 15 seconds starting at 10 seconds to avoid intro silence
    cmd = [
        "ffmpeg", "-y", "-i", video_path, 
        "-ss", "00:00:10", "-t", "15",
        "-vn", "-acodec", "pcm_s16le", "-ar", "24000", "-ac", "1", 
        output_wav
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Audio extracted successfully.")

def transcribe_clip(audio_path):
    print("Transcribing audio using OmniVoice ASR backend...")
    from services.asr_backend import transcribe_reference
    text = transcribe_reference(audio_path)
    if not text:
        print("Warning: Could not transcribe any text from the audio. Proceeding with empty text.")
        return ""
    print(f"Transcription: {text}")
    return text

def add_voice_to_db(name, ref_audio_src, ref_text):
    profile_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(ref_audio_src)[1]
    audio_filename = f"{profile_id}{ext}"
    
    os.makedirs(VOICES_DIR, exist_ok=True)
    audio_dest = os.path.join(VOICES_DIR, audio_filename)
    
    # Copy audio to voices directory
    shutil.copy2(ref_audio_src, audio_dest)
    print(f"Copied audio to {audio_dest}")
    
    # Insert into DB
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        current_time = time.time()
        
        # Base query mimicking OmniVoice's schema
        cursor.execute("""
            INSERT INTO voice_profiles (
                id, name, ref_audio_path, ref_text, instruct, language, 
                kind, is_demo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id, 
            name, 
            audio_filename, 
            ref_text, 
            "", 
            "Auto", 
            "clone", 
            0, 
            current_time
        ))
        
        conn.commit()
        print(f"Successfully added voice profile '{name}' (ID: {profile_id}) to OmniVoice database.")
    except Exception as e:
        print(f"Failed to add voice to database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    video_file = "/Users/truongdv/Downloads/a0be0f26-5451-4bdb-9995-b67cc73e0743.mp4"
    voice_name = "giọng-audio"
    
    temp_wav = "/tmp/omnivoice_temp_ref.wav"
    
    try:
        extract_audio(video_file, temp_wav)
        transcript = transcribe_clip(temp_wav)
        add_voice_to_db(voice_name, temp_wav, transcript)
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
