import os
import time
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tiktoken
import tkinter.ttk as ttk
from pathlib import Path

from openai import OpenAI, RateLimitError  # ✅ 新インターフェース対応

# ✅ APIキー確認＆クライアント初期化
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を確認してください。")
client = OpenAI(api_key=api_key)

# GPTのプロンプト生成
def create_prompt(text):
    return f"""
次のインタビューの文字起こしがあります。以下の4つのステップを実行してください：

1. 話者を明確に分離（例：「インタビュアー: ...」「被面接者: ...」）かつ文法や表現の誤りを修正し、読みやすく校正
2. 要点を5行程度に要約
3. 議論や回答の中に見られる重要な課題点・論点を箇条書きで抽出
4. 被面接者の面接としての改善点（例：論理展開、説得力、話し方、態度などの面）

--- 以下テキスト ---
{text}
"""

# テキスト分割
def split_text_by_token_limit(text, model="gpt-4", max_tokens=1500, overlap=100):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks

# ChatGPT処理関数（新API）
def gpt_process(prompt, model="gpt-4", temperature=0.3):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

# スレッド間通信
message_queue = queue.Queue()

def process_file(file_path, result_buffer):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    chunks = split_text_by_token_limit(raw_text)
    all_results = []

    for i, chunk in enumerate(chunks):
        message_queue.put(f"▶ チャンク {i+1}/{len(chunks)} 処理中...\n")
        prompt = create_prompt(chunk)
        try:
            result = gpt_process(prompt)
        except RateLimitError:
            message_queue.put("⚠️ レート制限。10秒待機...\n")
            time.sleep(10)
            result = gpt_process(prompt)
        all_results.append(f"## チャンク {i+1}\n\n{result}\n")
        time.sleep(3)

    result_buffer.set("\n\n".join(all_results))
    message_queue.put("\n✅ 処理完了！「出力結果を保存」ボタンで保存できます。\n")

# GUI起動
def start_gui():
    root = tk.Tk()
    root.title("面接要約ツール")
    root.geometry("750x560")

    result_buffer = tk.StringVar()

    def update_log_area():
        while not message_queue.empty():
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, message_queue.get())
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)
        log_text.after(100, update_log_area)

    def select_file():
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, path)

    def run_process():
        path = file_entry.get()
        if not path or not os.path.isfile(path):
            messagebox.showerror("エラー", "正しいテキストファイルを選択してください。")
            return
        progress_bar["value"] = 0
        progress_bar["maximum"] = 100
        log_text.config(state=tk.NORMAL)
        log_text.delete("1.0", tk.END)
        log_text.config(state=tk.DISABLED)
        threading.Thread(target=process_file_with_progress, args=(path, result_buffer), daemon=True).start()

    def process_file_with_progress(file_path, result_buffer):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        chunks = split_text_by_token_limit(raw_text)
        all_results = []

        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            message_queue.put(f"▶ チャンク {i+1}/{total_chunks} 処理中...\n")
            prompt = create_prompt(chunk)
            try:
                result = gpt_process(prompt)
            except RateLimitError:
                message_queue.put("⚠️ レート制限。10秒待機...\n")
                time.sleep(10)
                result = gpt_process(prompt)
            all_results.append(f"## チャンク {i+1}\n\n{result}\n")
            progress = int(((i + 1) / total_chunks) * 100)
            progress_bar["value"] = progress
            time.sleep(3)

        result_buffer.set("\n\n".join(all_results))
        message_queue.put("\n✅ 処理完了！「出力結果を保存」ボタンで保存できます。\n")

    def save_result_to_file():
        downloads_path = str(Path.home() / "Downloads" / "summary.md")
        try:
            with open(downloads_path, "w", encoding="utf-8") as f:
                f.write(result_buffer.get())
            messagebox.showinfo("保存完了", f"summary.md をダウンロードフォルダに保存しました：\n{downloads_path}")
        except Exception as e:
            messagebox.showerror("保存エラー", f"保存に失敗しました: {e}")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Button(frame, text="📂 テキストファイルを選択", command=select_file).pack(side=tk.LEFT)
    file_entry = tk.Entry(frame, width=60)
    file_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(root, text="🚀 変換開始", command=run_process).pack(pady=5)
    tk.Button(root, text="💾 出力結果を保存", command=save_result_to_file).pack(pady=5)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=700, mode="determinate")
    progress_bar.pack(pady=5)

    global log_text
    log_text = scrolledtext.ScrolledText(root, width=90, height=20)
    log_text.pack()
    log_text.config(state=tk.DISABLED)

    log_text.after(100, update_log_area)
    root.mainloop()

# 実行
if __name__ == "__main__":
    start_gui()
