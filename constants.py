# -*- coding: utf-8 -*-
#constant values
#Copyright (C) 2020 guredora <contact@guredora.com>

import wx
import os
#アプリケーション基本情報
APP_NAME="SOC"
APP_VERSION="0.5.0"
APP_COPYRIGHT_YEAR="2020"
APP_DEVELOPERS="Guredora"
SUPPORTING_LANGUAGE={"ja_JP": "日本語","en_US": "English"}# 対応言語一覧
AVAILABLE_FORMATS = (".jpg", ".png", ".gif", ".pdf")# 対応フォーマット一覧
#各種ファイル名
LOG_PREFIX="app"
LOG_FILE_NAME="application.log"
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

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"

#pipe関係
PIPE_NAME = "SocPdfTextCheck"