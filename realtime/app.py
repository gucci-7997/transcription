import streamlit as st
import subprocess
import os
import time
import json
import sys


st.set_page_config(page_title="🎧 リアルタイム音声認識", layout="wide")

st.title("🎤 リアルタイム音声認識（Streamlit表示）")
st.markdown("音声認識の結果がリアルタイムで表示されます。")

output_file = "recognized.jsonl"
control_file = "control.txt"

# 初回だけ recognized.jsonl を初期化する（セッション状態にフラグを保持）
if 'initialized' not in st.session_state:
    with open(output_file, "w") as f:
        pass  # 中身を空にする
    st.session_state.initialized = True

# 状態の表示
status_placeholder = st.empty()

# 録音中、停止中、待機中の状態表示を行う
if 'recording_state' not in st.session_state:
    st.session_state.recording_state = 'IDLE'  # 'IDLE' = 録音されていない状態

# 状態表示を色付きで更新
def update_status_display():
    if st.session_state.recording_state == 'START':
        status_placeholder.markdown('<p style="color:green;">🟢 録音中...</p>', unsafe_allow_html=True)
    elif st.session_state.recording_state == 'STOP':
        status_placeholder.markdown('<p style="color:red;">🛑 停止中...</p>', unsafe_allow_html=True)
    elif st.session_state.recording_state == 'IDLE':
        status_placeholder.markdown('<p style="color:orange;">🟠 待機中...</p>', unsafe_allow_html=True)

# ボタンを横並びに配置
col1, col2, col3 = st.columns([1, 1, 1])

# 録音開始ボタン（▶️ 録音開始）
with col1:
    if st.button('▶️ 録音開始'):
        # 録音開始
        if st.session_state.recording_state == 'IDLE'or'STOP':  # IDLEの時にのみ録音を開始する
            st.session_state.recording_state = 'START'
            with open(control_file, 'w') as f:
                f.write("START")
        
            # recognizer.py 起動（サブプロセスで実行）
            if 'process' not in st.session_state or st.session_state.process.poll() is not None:
                st.session_state.process = subprocess.Popen([sys.executable, '/Users/gucci/Documents/transcription/realtime/recognizer.py'])

            # 状態更新
            update_status_display()
        else:
            st.warning("既に録音中です。")

# 録音停止ボタン（⏹ 録音停止）
with col2:
    if st.button('⏹ 録音停止'):
        # 録音停止コマンド書き込み
        st.session_state.recording_state = 'STOP'
        with open(control_file, 'w') as f:
            f.write("STOP")
        
        # サブプロセスを停止
        if 'process' in st.session_state:
            st.session_state.process.terminate()
            st.session_state.process.wait()
        
        # 状態更新
        update_status_display()

# 認識結果のクリアボタン
with col3:
    if st.button("🗑 認識結果をクリア"):
        with open(output_file, "w") as f:
            pass
        st.empty()
        st.success("認識結果をクリアしました。")

        # 現在の状態を表示し直す
        update_status_display()

# 音声認識結果を逐次表示
def read_results():
    if not os.path.exists(output_file):
        return []
    with open(output_file, "r") as f:
        return [json.loads(line)["text"] for line in f if line.strip()]

# ボタンの下にリアルタイムで認識結果を表示するために、結果表示のためのプレースホルダーを作成
results_placeholder = st.empty()

# 録音中はリアルタイムで結果表示
prev_line_count = 0

while True:
    if st.session_state.recording_state == 'START':
        # 録音中、リアルタイムで結果表示
        results = read_results()
        if len(results) != prev_line_count:
            text = "\n".join(f"📝 {r}" for r in results)
            results_placeholder.text(text)
            prev_line_count = len(results)
    elif st.session_state.recording_state == 'STOP':
        # 録音停止後に結果を表示
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r") as f:
                results = [json.loads(line)["text"] for line in f if line.strip()]
            
            # 結果表示
            st.subheader("📝 音声認識結果")
            st.write("\n".join(results))

            # 結果をファイルとしてダウンロードできるようにする
            result_text = "\n".join(results)
            st.download_button(
                label="結果をダウンロード",
                data=result_text,
                file_name="recognized_results.txt",
                mime="text/plain"
            )
        break
    else:
        # 録音開始前（状態IDLE）では結果を表示しない
        time.sleep(1)
