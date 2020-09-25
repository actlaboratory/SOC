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

## バージョンの上げ方

python tools\bumpup.py major でメジャーバージョンを上げる。互換性がなくなるアップデートをするときに使う。

python tools\bumpup.py minor でマイナーバージョンを上げる。互換性は保たれるが、新機能を追加したときに使う。

python tools\bumpup.py patch でパッチバージョンを上げる。バグ修正したときに使う。

リリース日は、 yyyy-mm-dd の形式で入力する。そのままエンターを押すと、今日の日付になる。

これらを実行すると、アプリケーションに組み込まれるバージョン情報、著作権表記、public/readme.txtのバージョン番号やlast updateが自動で書き換えられるので、それらをコミットする。version.jsonは、CIやバージョン管理ツールが使うので、これもコミットする。

