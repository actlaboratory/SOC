
import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"OPEN": _("変換ファイルの追加(&o)"),
	"NEW": _("新しく文字認識を開始(&N)"),
	"EXIT": _("終了(&x)"),
	"GOOGLE": _("Googleと連携する(&g)"),
	"SENDREGIST": _("送るメニューにショートカットを作成(&s)"),
	"OPENVIEW": "OCRダイアログを開く（テスト用）",
	"SETTINGS": _("設定画面を開く(&w)"),
	"HOMEPAGE": _("ACT Laboratoryのホームページを開く(&p)"),
	"ABOUT": _("このソフトについて"),
	"UPDATE": _("最新バージョンを確認"),
	# for Context Menu
	"COPY_TEXT": _("本文のコピー(&C)"),
	"SAVE": _("表示中のテキストをファイルに保存(&S)"),
}
