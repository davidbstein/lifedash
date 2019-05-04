import paper
import time
import os


def _write_to(s, file):
  path = os.path.dirname(__file__) + "/../www/" + file
  with open(path, "w") as f:
    f.write(s)


def run_every_15():
  pass


def run_every_minute():
  # TODO
  _write_to(paper.get_html(), "html/todo.html")


def called_every_minute():
  current_minute = int(time.time() // 60)
  run_every_minute()
  if 0 == (current_minute % 15):
    run_every_15()
