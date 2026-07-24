#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import argparse
import shutil

def setup_separator_env():
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".separator_env")
    separator_bin = os.path.join(venv_dir, "bin", "audio-separator")
    
    if not os.path.exists(separator_bin):
        print(">> Đang cài đặt môi trường ảo cho AI Audio Separator (MDX-Net) (chỉ chạy lần đầu)...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        pip_bin = os.path.join(venv_dir, "bin", "pip")
        # Cài đặt audio-separator với onnx cho Mac
        subprocess.run([pip_bin, "install", "audio-separator[onnx]"], check=True)
    return separator_bin

def extract_bgm(separator_bin, video_path, output_dir):
    print(f"\n>> Đang dùng AI MDX-Net siêu sạch để bóc tách nhạc nền từ: {video_path} ...")
    print(">> (Tiến trình này sẽ tự tải Model nếu chưa có, thời gian tùy thuộc độ dài video)\n")
    
    # Chạy lệnh tách nhạc
    cmd = [
        separator_bin,
        video_path,
        "--model_filename", "UVR-MDX-NET-Inst_HQ_3.onnx",
        "--output_dir", output_dir,
        "--output_format", "WAV"
    ]
    subprocess.run(cmd, check=True)
    
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Audio-separator mặc định sinh ra file chứa chữ (Instrumental) và (Vocals)
    final_bgm_path = os.path.join(output_dir, f"{base_name}_bgm.wav")
    
    for filename in os.listdir(output_dir):
        if "(Instrumental)" in filename and base_name in filename:
            instrumental_path = os.path.join(output_dir, filename)
            os.rename(instrumental_path, final_bgm_path)
        elif "(Vocals)" in filename and base_name in filename:
            vocals_path = os.path.join(output_dir, filename)
            os.remove(vocals_path)
        
    print(f"\n✅ Đã trích xuất nhạc nền nguyên bản thành công!")
    print(f"📁 Nhạc sạch được lưu tại: {final_bgm_path}\n")
    return final_bgm_path

def mix_audio(voice_path, bgm_path, output_path, bgm_volume=0.15):
    print(f">> Đang mix giọng đọc VoxCPM với nhạc nền...")
    
    # -stream_loop -1: Lặp lại nhạc nền vô tận nếu nó ngắn hơn giọng đọc
    # amix=duration=first: Cắt kết quả cho bằng độ dài của file giọng đọc (file 0)
    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-stream_loop", "-1", "-i", bgm_path,
        "-filter_complex", f"[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Mix nhạc hoàn tất!")
    print(f"🎧 File thành phẩm nằm tại: {output_path}\n")

def main():
    parser = argparse.ArgumentParser(description="Tách nhạc nền từ video và mix với audio giọng đọc")
    parser.add_argument("-v", "--video", required=True, help="Đường dẫn đến file video (để tách nhạc)")
    parser.add_argument("-a", "--audio", required=False, help="Đường dẫn đến file audio giọng đọc (để mix, nếu có)")
    parser.add_argument("-o", "--output", required=False, help="Đường dẫn file kết quả sau khi mix (mặc định: results/mixed_<tên_audio>.m4a)")
    parser.add_argument("--volume", type=float, default=0.10, help="Âm lượng nhạc nền (mặc định: 0.10 ~ 10%%)")
    
    args = parser.parse_args()
    
    # Tạo thư mục musics
    root_dir = os.path.dirname(os.path.abspath(__file__))
    musics_dir = os.path.join(root_dir, "musics")
    os.makedirs(musics_dir, exist_ok=True)
    
    # 1. Cài đặt tự động MDX-Net nếu chưa có
    separator_bin = setup_separator_env()
    
    # 2. Bóc tách nhạc từ video
    bgm_path = extract_bgm(separator_bin, args.video, musics_dir)
    
    # 3. Mix nhạc nếu người dùng có truyền file audio
    if args.audio:
        if not os.path.exists(args.audio):
            print(f"❌ Không tìm thấy file audio: {args.audio}")
            sys.exit(1)
            
        output_file = args.output
        if not output_file:
            results_dir = os.path.join(root_dir, "results")
            os.makedirs(results_dir, exist_ok=True)
            # Tạo tên file output tự động
            audio_base = os.path.splitext(os.path.basename(args.audio))[0]
            output_file = os.path.join(results_dir, f"{audio_base}_mixed.m4a")
            
        mix_audio(args.audio, bgm_path, output_file, args.volume)

if __name__ == "__main__":
    main()
