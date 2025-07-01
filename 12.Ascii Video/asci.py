import cv2
import os
import sys
import shutil
import time
import numpy as np
import subprocess
import threading

# More ASCII characters for higher quality
ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def get_terminal_size():
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines

def resize_frame(frame, new_width, new_height):
    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

def frame_to_ascii(frame, color_frame=None):
    ascii_str = ""
    n_chars = len(ASCII_CHARS)
    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            char = ASCII_CHARS[int(pixel / 256 * n_chars)]
            if color_frame is not None:
                b, g, r = color_frame[y, x]
                ascii_str += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            else:
                ascii_str += char
        ascii_str += "\n"
    return ascii_str

def play_audio(video_path):
    # ffplay plays audio only, -nodisp disables video, -autoexit closes when done
    subprocess.run(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', video_path])

def play_ascii_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = 1.0 / (fps if fps > 0 else 24)

    # Start audio in a separate thread
    audio_thread = threading.Thread(target=play_audio, args=(video_path,), daemon=True)
    audio_thread.start()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            term_width, term_height = get_terminal_size()
            # Each ASCII char is taller than wide, so adjust height
            new_width = term_width
            new_height = int(term_height * 1.9)  # 1.9 empirically fits most fonts

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized_gray = resize_frame(gray, new_width, new_height)
            resized_color = resize_frame(frame, new_width, new_height)

            ascii_frame = frame_to_ascii(resized_gray, resized_color)

            os.system('cls' if os.name == 'nt' else 'clear')
            print(ascii_frame, end="")
            time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python asci.py <video_file>")
    else:
        play_ascii_video(sys.argv[1])