import os

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("APIキーが設定されています。")
else:
    print("APIキーが設定されていません。")
