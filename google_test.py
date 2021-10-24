import CredentialManager
from apiclient import discovery
import proxyUtil

proxyEnviron = proxyUtil.virtualProxyEnviron()
proxyEnviron.set_environ()
credential = CredentialManager.CredentialManager(True)
credential.Authorize()
service = discovery.build("drive", "v3", credentials=credential.credential)
print(type(service))