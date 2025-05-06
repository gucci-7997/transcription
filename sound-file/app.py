import streamlit as st
import whisper
import tempfile
import os
import time

st.set_page_config(page_title="Whisper文字起こしツール", layout="centered")
st.title("🎙 Whisper文字起こしツール（アップロード専用）")
st.caption("音声ファイルをアップロードして文字起こしを行います。")

# モデル選択
model_size = st.selectbox("使用するWhisperモデルを選択", ["tiny", "base", "small", "medium", "large"])
st.info("モデルが大きいほど精度が上がりますが、処理時間とメモリ使用量も増えます。")

# 音声ファイルのアップロード
uploaded_file = st.file_uploader("音声ファイルを選択（mp3, wav, m4a）", type=["mp3", "wav", "m4a"])

if uploaded_file:
    st.success(f"{uploaded_file.name} を読み込みました。")
    if st.button("▶️ 文字起こしを実行"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.read())
            audio_path = tmp.name

        st.info("モデルを読み込み中...")
        model = whisper.load_model(model_size)

        start_time = time.time()
        try:
            with st.spinner("文字起こし中..."):
                result = model.transcribe(audio_path, fp16=False, language="ja")
                transcription = result["text"]
                st.success("✅ 文字起こし完了！")

                st.subheader("📝 出力結果")
                st.text_area("文字起こしテキスト", transcription, height=300)

                st.download_button("📥 ダウンロード", transcription, file_name="transcription.txt", mime="text/plain")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

        end_time = time.time()
        st.info(f"実行時間: {end_time - start_time:.2f}秒")
