# transcription

## sound-file
音声ファイルを文字起こし、結果をダウンロードするGUI
* 使用モデル：Whisper
* フレームワーク：streamlit

## realtime
リアルタイムで文字起こし、結果をダウンロードするGUI
* 使用モデル：vosk
* フレームワーク：streamlit
```
wget https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip
unzip vosk-model-small-ja-0.22.zip
mv vosk-model-small-ja-0.22 model
```

## summary
話者分離、要約、改善案出力
