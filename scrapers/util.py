import os

def get_template(name):
  path = os.path.dirname(__file__) + "/../templates/{}.tmpl.html".format(name)
  return open(path).read();


def write_to_www(content, filename):
  path = os.path.dirname(__file__) + "/../www/" + filename
  with open(path, "w") as f:
    f.write(content)