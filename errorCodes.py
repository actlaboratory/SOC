﻿# -*- coding: utf-8 -*-
#error codes

OK=0				#成功(エラーなし)
NOT_SUPPORTED=1		#サポートされていない呼び出し
FILE_NOT_FOUND=2
PARSING_FAILED=3 #ファイル読み込みエラー
IO_ERROR=4 #ファイル入出力エラー
CANCELED=5#ユーザーによるキャンセル
WAITING_USER=6		#ユーザの操作待ち
FILE_NOT_SUPPORTED=7#対応していないファイル
NOT_AUTHORIZED=8#グーグルで認証していない
NET_ERROR=100#通信関連のエラー
GOOGLE_ERROR = 10
CANCELED_BY_USER = 11
CONNECT_TIMEOUT = 12
UPDATER_NEED_UPDATE = 200# アップデートが必要
UPDATER_LATEST = 204# アップデートが無い
UPDATER_VISIT_SITE = 205
UPDATER_BAD_PARAM = 400# パラメーターが不正
UPDATER_NOT_FOUND = 404# アプリケーションが存在しない
UNKNOWN=99999
