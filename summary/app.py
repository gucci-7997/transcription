import openai
import tiktoken
import time
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

# ✅ APIキー確認＆クライアント初期化
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を確認してください。")
client = OpenAI(api_key=api_key)

# ----------- ユーティリティ関数 ---------------

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

def gpt_process(prompt, model="gpt-4", temperature=0.3):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

# ----------- GPTプロンプト生成関数 -------------

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

# ----------- メイン処理部 ---------------------

def main():
    input_path = "interview.txt"
    output_path = "interview_summary.md"

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    chunks = split_text_by_token_limit(raw_text, model="gpt-4", max_tokens=1500, overlap=100)
    all_results = []

    for i, chunk in enumerate(chunks):
        print(f"▶ 処理中: チャンク {i+1}/{len(chunks)}")
        prompt = create_prompt(chunk)
        for attempt in range(2):  # 再試行1回
            try:
                result = gpt_process(prompt)
                all_results.append(f"## チャンク {i+1}\n\n{result}\n")
                break
            except Exception as e:
                print(f"⚠️ エラー発生: {e}（再試行します）")
                time.sleep(10)

        time.sleep(3)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_results))

    print(f"\n✅ 処理完了！ → 結果: {output_path}")

# ----------- 実行 -------------
if __name__ == "__main__":
    main()
