import CredentialManager
from apiclient import discovery

credential = CredentialManager.CredentialManager(True)
credential.Authorize()
service = discovery.build("drive", "v3", credentials=credential.credential)
print(type(service))