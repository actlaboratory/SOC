
import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"OPEN": _("変換ファイルの追加(&o)"),
	"EXIT": _("終了(&x)"),
	"GOOGLE": _("Googleと連携する(&g)"),
	"SENDREGIST": _("送るメニューにショートカットを作成(&s)"),
	"SETTINGS": _("設定画面を開く(&w)"),
	"HOMEPAGE": _("ACT Laboratoryのホームページを開く(&p)"),
	"ABOUT": _("このソフトについて"),
	"UPDATE": _("最新バージョンを確認"),
}
