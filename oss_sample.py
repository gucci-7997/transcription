import time
import whisper
import os

input_file = "voice_sample.m4a"
output_file = "transcription.txt"

if not os.path.exists(input_file):
    raise FileNotFoundError(f"指定されたファイルが存在しません: {input_file}")

print("モデルを読み込み中...")
model = whisper.load_model("medium")

start_time = time.time()
try:
    # 言語を日本語に固定
    result = model.transcribe(input_file, fp16=False, language="ja")
    print("文字起こし結果:")
    print(result["text"])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"文字起こし内容を '{output_file}' に保存しました。")
except Exception as e:
    print(f"文字起こし中にエラーが発生しました: {e}")
end_time = time.time()
print(f'実行時間: {end_time - start_time:.2f}秒')
