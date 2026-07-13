# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
import subprocess
import sys

def clean_markdown(text):
    """
    Cleans markdown formatting to leave only text for TTS.
    """
    # Remove lines starting with # (Headings)
    # text = re.sub(r'^#.*$', '', text, flags=re.MULTILINE)
    
    # Remove metadata lines like *Thể loại...* or ---
    text = re.sub(r'^\*Thể loại.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---.*$', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markdown symbols
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Remove extra blank lines
    text = re.sub(r'\n+', ' ', text)
    
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown script to Audio using OmniVoice")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file path")
    parser.add_argument("--output_dir", "-o", default="/Users/truongdv/Documents/projects/video-audio/results", help="Output directory for audio files")
    parser.add_argument("--model", "-m", default="k2-fsa/OmniVoice", help="Model checkpoint path or HF repo id")
    parser.add_argument("--language", "-l", default="vi", help="Language ID (e.g. 'vi', 'en')")
    parser.add_argument("--ref_audio", "-r", default="/Users/truongdv/Library/Application Support/OmniVoice/voices/cd18666c_clean.wav", help="Optional reference audio for voice cloning")
    
    # Text chuẩn xác đã được trích xuất từ 15s audio để alignment
    clean_text = "Anh sẽ cưới ai? Không ai cả. Anh ngáp một cái, sống một mình. Tại sao? Một mình vẫn ổn mà, biết đặt đồ ăn, biết dùng máy giặt. Tôi nhìn anh, vậy anh có thể đi đón Tiểu Điền tan học không? Cả người anh khựng lại trong thoáng chốc. Sau đó, anh nói ra câu nói mà đến tận bây giờ tôi vẫn không thể quên. Điều duy nhất khiến anh còn lưu luyến ở em là vì em đã sinh cho..."
    parser.add_argument("--ref_text", "-t", default=clean_text, help="Optional reference text for voice cloning")
    
    parser.add_argument("--speed", "-s", type=float, default=1.1, help="Reading speed multiplier")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Read the markdown file
    with open(args.input, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    # Clean up the markdown content
    clean_text = clean_markdown(md_content)
    
    if not clean_text:
        print("Error: Extracted text is empty.")
        sys.exit(1)
        
    # Prepare JSONL entry
    base_name = os.path.splitext(os.path.basename(args.input))[0]
    jsonl_path = os.path.join(args.output_dir, f"{base_name}.jsonl")
    
    entry = {
        "id": base_name,
        "text": clean_text,
        "language_id": args.language,
        "speed": args.speed
    }
    
    if args.ref_audio:
        entry["ref_audio"] = args.ref_audio
    if args.ref_text is not None:
        entry["ref_text"] = args.ref_text
        
    with open(jsonl_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
    print(f"Generated JSONL file at: {jsonl_path}")
    print("Starting OmniVoice inference...")
    
    # Define omnivoice-infer-batch path
    omnivoice_bin = "/Users/truongdv/omnivoice-env/project/.venv/bin/omnivoice-infer-batch"
    
    if not os.path.exists(omnivoice_bin):
        print(f"Error: OmniVoice executable not found at {omnivoice_bin}")
        sys.exit(1)
        
    # Build command
    cmd = [
        omnivoice_bin,
        "--test_list", jsonl_path,
        "--res_dir", args.output_dir,
        "--lang_id", args.language,
        "--model", args.model
    ]
    
    # Fix macOS no_proxy IPv6 httpx parsing bug by cleaning env
    run_env = os.environ.copy()
    run_env["no_proxy"] = "localhost,127.0.0.1"
    run_env["NO_PROXY"] = "localhost,127.0.0.1"
    
    # Run the command
    try:
        subprocess.run(cmd, check=True, env=run_env)
        print(f"\nSuccess! Audio should be saved in the '{args.output_dir}' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running OmniVoice: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
