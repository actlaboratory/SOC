import os
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client import client
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io
def get_credentials(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   "drive-python-quickstart.json")

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print("Storing credentials to " + credential_path)
    return credentials
def text_ocr(local_file_path, service):
    MIME_TYPE = "application/vnd.google-apps.document"
    media_body = MediaFileUpload(local_file_path, mimetype=MIME_TYPE, resumable=True)
    
    body = {
    # 拡張子付、パスなしのファイル名を与える
    # 拡張子なし(file_path.stem)だと、HTTP400エラーになる
    "name": local_file_path.name,
    "mimeType": MIME_TYPE,
    }
    
    file = service.files().create(
    body=body,
    media_body=media_body,
    # OCRの言語コードは、ISO 639-1 codeで指定
    # https://developers.google.com/drive/v3/web/manage-uploads
    ocrLanguage="ja",
    fields="id"
    )
    print(type(file))

    ID = file.get("id")
    
    request = service.files().export_media(fileId=ID,
    mimeType="text/plain")
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return fh.getvalue().decode("utf-8")
