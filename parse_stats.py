import sys
import json

is_header = False
fields = None

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("interval", help="interval stats are being collected at")
args = parser.parse_args()

while True:
  line = sys.stdin.readline()
  if not line:
    break

  if line.strip() == "":
    # empty line handling
    is_header = True
    continue
  else:
    if is_header or line[0] == "#":
      is_header = False
      line = line.replace("#", "")
      fields = [f.lower() for f in line.split()]
    else:
      values = line.split()
      if fields:
        sample = zip(fields, values)
        for i,f in enumerate(fields):
          val = values[i]

          f = f.replace("/", "_")
          fields[i] = f

          try:
            val = float(values[i])
            values[i] = int(val)

          except ValueError:
            pass


        sample = dict(zip(fields, values))
        sample["weight"] = args.interval
        print json.dumps(sample)
