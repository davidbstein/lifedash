import time
import requests
import mistune
from secrets import SECRETS

_paper_secrets = SECRETS['DROPBOX_PAPER']
_dropbox_cookie = ";".join('{}={}'.format(k, v) for k, v in _paper_secrets['cookie'].items())

def _request_md_generation():
  """ returns the url where the document can be downloaded from once compiled """
  compile_resp = requests.post(
    "https://paper.dropbox.com/pad/export2",
    data={
      "localPadId": _paper_secrets['pad_id'],
      "mode": 1,
      "format": 2,
      "xsrf": _paper_secrets['xsrf']
    },
    headers={
      'Cookie': _dropbox_cookie,
    }
  )
  return compile_resp.json()['url']

def _get_md_text(url):
  file_resp = requests.get(
      url,
      headers={
          'Cookie': _dropbox_cookie
      }
  )
  if (file_resp.status_code == 400):
    return None
  if (file_resp.status_code == 200):
    return(file_resp.text)
  raise Exception("{}: {}".format(file_resp.status_code, file_resp.reason))

def get_paper_md():
  url = _request_md_generation()
  for _ in range(5):
    time.sleep(1)
    md = _get_md_text(url)
    if md:
      break
  return (md
    ).replace("\n#", "\n\n#"
    ).replace("[ ]", "- ![](/img/uncheck.png)"
    ).replace("[x]", "- ![](/img/check.png)")

def get_paper_html():
  md = get_paper_md()
  html = """
  <html>
  <head>
  <link rel="stylesheet" href="/css/chrome.css" />
  <link rel="stylesheet" href="/css/todo.css" />
  </head>
  <body>{}</body>
  </html>
  """.format(mistune.markdown(md))
  return html
