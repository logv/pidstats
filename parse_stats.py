import sys
import json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("interval", nargs='?', default=1,help="interval stats are being collected at")
args = parser.parse_args()


# FIELDS THAT CAN BE ADDED TOGETHER FOR COMBINING THEM ACROSS PROCESSES
COMBINEABLE_FIELDS = [ "vsz", "minflt_s", "majflt_s", "rss" ]

previous_samples = {}
def print_previous():
    for command in previous_samples:
        print json.dumps(previous_samples[command])

def combine_or_update(sample):
    command = "%s:%s" % (sample["command"], sample.get("args", ""))
    if command in previous_samples:
        prev_sample = previous_samples[command]

        for field in sample:
            combineable = field in COMBINEABLE_FIELDS or field[0] == "%"
            if field in prev_sample and combineable:
                prev_sample[field] += sample[field]

    else:
        previous_samples[command] = sample


ADD_ARGS=True
def parse_sample(fields, values):

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

    if ADD_ARGS:
        cmd_val = []
        while len(values) > len(fields):
            cmd_val.append(values.pop())

        sample["args"] = " ".join(reversed(cmd_val))

    return sample


is_header = False
fields = None
def process_line(line):
  global fields, is_header
  if line.strip() == "":
    # empty line handling
    is_header = True
    print_previous()
  else:
    if is_header or line[0] == "#":
      is_header = False
      line = line.replace("#", "")
      fields = [f.lower() for f in line.split()]
    else:
      values = line.split()
      if fields:
        sample = parse_sample(fields, values)
        sample["weight"] = int(args.interval)

        combine_or_update(sample)


if __name__ == "__main__":
    while True:
      line = sys.stdin.readline()
      if not line:
        break

      process_line(line)

    print_previous()
