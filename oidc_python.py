import requests
import base64
import hashlib
import html
import json
import os
import re
import urllib.parse
import requests



code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
code_challenge = code_challenge.replace('=', '')


# base_url = "https://localhost:9443/oauth2/authorize?scope=openid&response_type=code&redirect_uri=https://localhost/callback&client_id=oVxWz_NwghyPUxgWsZ0Ke_NMdL8a"

# base_url = base_url+"&code_challenge=" +code_challenge + "&code_challenge_method=S256"
	

# # import pdb;pdb.set_trace()

# res = requests.get(base_url, verify=False)

# print(res.status_code)
# print(res.json())


client_id = "oVxWz_NwghyPUxgWsZ0Ke_NMdL8a"
# state = "fooobarbaz"
redirect_uri = "https://localhost/callback"
username = "admin"
password = "admin"
# import pdb;pdb.set_trace()


resp = requests.get(
    url="https://localhost:9443/oauth2/authorize",
    params={
        "response_type": "code",
        "client_id": client_id,
        "scope": "openid",
        "redirect_uri": redirect_uri,
        # "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    },verify=False,
    # allow_redirects=False
)

import pdb;pdb.set_trace()

# allow_redirects=False,

print("STATUS code:{0}".format(resp.status_code))



cookie = resp.headers['Set-Cookie']
cookie = '; '.join(c.split(';')[0] for c in cookie.split(', '))
print("Cookie Saved: {0}".format(cookie))


page = resp.text
# form_action = html.unescape(re.search('<form\s+.*?\s+action="(.*?)"', page, re.DOTALL).group(1))
# print("Form Action :::", form_action)



print("Login Starts here-----------")



# resp = requests.post(
#     url="https://localhost:9443/commonauth", 
#     data={
#         "username": username,
#         "password": password,
#     }, 
#     headers={"Cookie": cookie},
#     allow_redirects=False,
#     verify=False
# )
# resp.status_code




