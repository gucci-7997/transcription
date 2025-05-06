# recognizer.py
import sounddevice as sd
import vosk
import queue
import json
import os
import sys
import time


model_path = "/Users/gucci/Documents/transcription/realtime/model"
model = vosk.Model(model_path)
q = queue.Queue()
result_file = "recognized.jsonl"
control_file = "control.txt"  # ストップコマンド用


def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("🎙 音声認識を開始（Ctrl+Cで終了）")
        rec = vosk.KaldiRecognizer(model, 16000)

        try:
            while True:
                if os.path.exists(control_file) and open(control_file, 'r').read().strip() == "STOP":
                    print("🛑 音声認識を停止します")
                    break
                
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    with open(result_file, "a") as f:
                        json.dump(result, f, ensure_ascii=False)
                        f.write("\n")
                    print("📝", result.get("text", ""))
        except KeyboardInterrupt:
            print("\n🛑 停止しました")

if __name__ == "__main__":
    listen()
