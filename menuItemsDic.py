
import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"NEW": _("新しく文字認識を開始(&N)"),
	"EXIT": _("終了(&X)"),
	"GOOGLE": _("Googleと連携する(&G)"),
	"SENDREGIST": _("送るメニューにショートカットを作成(&S)"),
	"SETTINGS": _("設定画面を開く(&W)"),
	"HOMEPAGE": _("ACT Laboratoryのホームページを開く(&P)"),
	"ABOUT": _("このソフトについて(&A)"),
	"UPDATE": _("最新バージョンを確認(&U)"),
	# for Context Menu
	"COPY_TEXT": _("本文のコピー(&C)"),
	"SAVE": _("表示中のテキストをファイルに保存(&S)"),
}
