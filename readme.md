# SOCソースコード
## セットアップ
python -m pip install -r requirements.txt
## 実行
python soc.py
## build
python -m venv pyenv
pyenv/scripts/activate
python -m pip install -r requirements.txt
pyenv/Lib/site-packages/PyInstaller/hooksにtools/hook-googleapiclient.pyをコピー
python tools/build.py
pyenvはビルド以外では必要ないのでビルドが終わったら削除しても問題ない。

