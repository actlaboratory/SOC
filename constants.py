# -*- coding: utf-8 -*-
#constant values
#Copyright (C) 2020 guredora <contact@guredora.com>

import os

import wx

#アプリケーション基本情報
APP_NAME="SOC"#アプリケーションの名前
APP_FULL_NAME = "Simple Ocr Controller"#アプリケーションの完全な名前
APP_ICON = None
APP_VERSION="0.5.1"
APP_LAST_RELEASE_DATE="2021-01-07"
APP_COPYRIGHT_YEAR="2019-2021"
APP_LICENSE="GPL v2(or later)"
APP_DEVELOPERS="guredora, ACT Laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL="https://actlab.org/software/SOC"
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All lights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

SUPPORTING_LANGUAGE={"ja-JP": "日本語","en-US": "English"}# 対応言語一覧
AVAILABLE_FORMATS = (".jpg", ".png", ".gif", ".pdf")# 対応フォーマット一覧
#各種ファイル名
LOG_PREFIX="SOC"
LOG_FILE_NAME="SOC.log"
SETTING_FILE_NAME="settings.ini"
KEYMAP_FILE_NAME="keymap.ini"
#フォントの設定可能サイズ範囲
FONT_MIN_SIZE=5
FONT_MAX_SIZE=35

#３ステートチェックボックスの状態定数
NOT_CHECKED=wx.CHK_UNCHECKED
HALF_CHECKED=wx.CHK_UNDETERMINED
FULL_CHECKED=wx.CHK_CHECKED

# google関連定数
GOOGLE_DIR = ".credential"
GOOGLE_FILE_NAME = "credential.json"
GOOGLE_CLIENT_ID = "700286679735-4bssuo7bsen9o7sua8joacl18bhms6nd.apps.googleusercontent.com"
GOOGLE_NEED_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
GOOGLE_CALLBACK_URL = "http://localhost:8080"
GOOGLE_CLIENT_SECRET = '{"installed":{"client_id":"700286679735-4bssuo7bsen9o7sua8joacl18bhms6nd.apps.googleusercontent.com","project_id":"simple-ocr-controller","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"607kPxH25Wba68T3mJmoxrKD","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}'

#画像ファイル形式定数
FORMAT_UNKNOWN = 0
FORMAT_PNG = 0x1
FORMAT_JPEG = 0x2
FORMAT_BMP = 0x4
FORMAT_GIF = 0x8
FORMAT_TIFF = 0x10
FORMAT_PDF_UNKNOWN = 0x20
FORMAT_PDF_TEXT = 0x40
FORMAT_PDF_IMAGE = 0x80
FORMAT_PDF_MULTI_PAGE = 0x100
# 単一ページPDFなら何でもOK
FORMAT_PDF_ALL = FORMAT_PDF_TEXT | FORMAT_PDF_IMAGE

#対応形式一覧
#定数を優先順位準に並べる

IMAGE_FORMAT_LIST = [
	FORMAT_BMP,
	FORMAT_PNG,
	FORMAT_GIF,
	FORMAT_JPEG,
]
#ファイル形式と拡張子の辞書
EXT_TO_FORMAT = {
	"bmp": FORMAT_BMP,
	"png": FORMAT_PNG,
	"gif": FORMAT_GIF,
	"jpg": FORMAT_JPEG,
	"tif": FORMAT_TIFF,
	"pdf": FORMAT_PDF_UNKNOWN
}

#build関連定数
BASE_PACKAGE_URL = "https://github.com/actlaboratory/SOC/releases/download/0.5.0/SOC-0.5.0.zip"
PACKAGE_CONTAIN_ITEMS = ("tesseract-ocr", "poppler")
NEED_HOOKS = ("tools/hook-googleapiclient.py",)
STARTUP_FILE = "SOC.py"

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_VERSION = "1.0.0"
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"
UPDATER_WAKE_WORD = "hello"
#pipe関係
PIPE_NAME = "SocPdfTextCheck"
