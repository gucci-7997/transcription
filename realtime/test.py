import tkinter as tk
from tkinter import scrolledtext
import sounddevice as sd
import queue
import vosk
import json
import threading

# モデルの読み込み（事前に vosk-model をダウンロードして解凍しておくこと）
model = vosk.Model("model")
q = queue.Queue()

# 音声認識用の関数
def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))

def recognize_audio(text_widget, stop_event):
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        text_widget.insert(tk.END, "🎙 リアルタイム音声認識を開始...\n")

        while not stop_event.is_set():
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    text_widget.insert(tk.END, f"📝 {text}\n")
                    text_widget.see(tk.END)
            else:
                partial = json.loads(rec.PartialResult())
                text_widget.insert(tk.END, f"⌛ {partial.get('partial', '')}\r")
                text_widget.see(tk.END)

# GUI構築
def start_gui():
    root = tk.Tk()
    root.title("🎧 リアルタイム音声認識")

    text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
    text_widget.pack(padx=10, pady=10)

    stop_event = threading.Event()

    def start_recognition():
        text_widget.delete(1.0, tk.END)
        stop_event.clear()
        threading.Thread(target=recognize_audio, args=(text_widget, stop_event), daemon=True).start()

    def stop_recognition():
        stop_event.set()
        text_widget.insert(tk.END, "\n🛑 音声認識を停止しました\n")

    start_button = tk.Button(root, text="▶️ 開始", command=start_recognition)
    start_button.pack(side=tk.LEFT, padx=10, pady=5)

    stop_button = tk.Button(root, text="⏹ 停止", command=stop_recognition)
    stop_button.pack(side=tk.RIGHT, padx=10, pady=5)

    root.mainloop()

# 実行
if __name__ == "__main__":
    start_gui()
