import paper
import location
import time
from util import write_to_www


def run_every_15():
  pass


def run_every_minute():
  write_to_www(paper.get_paper_html(), "html/todo.html")
  write_to_www(location.get_locations_json(), "data/locations.json")
  write_to_www(location.get_locations_html(), "html/map.html")


def called_every_15():
  pass


def called_every_minute():
  current_minute = int(time.time() // 60)
  run_every_minute()
  if 0 == (current_minute % 15):
    run_every_15()


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--freq",
    help="what frequency is this call? valid values: [1, 15, 60]",
    type=int,
    default=1
  )
  args = parser.parse_args()
  if (args.freq == 1):
    called_every_minute()
  elif (args.freq == 15):
    called_every_15()
  else:
    print(parser.usage)
