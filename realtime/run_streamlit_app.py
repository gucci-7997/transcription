import subprocess
import sys

def start_recognizer():
    # Pythonのフルパスを使って実行
    subprocess.Popen(['/Users/gucci/.pyenv/shims/python3', '/Users/gucci/Documents/transcription/realtime/recognizer.py'])

def start_streamlit():
    subprocess.run(['/Users/gucci/.pyenv/shims/python3', '-m', 'streamlit', 'run', '/Users/gucci/Documents/transcription/realtime/app.py'])

if __name__ == "__main__":
    start_recognizer()  # recognizer.py を起動
    start_streamlit()   # Streamlit アプリを起動