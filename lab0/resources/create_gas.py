#!/usr/bin/env python2.7

import json, sys, re, string, random

def print_usage():
  print "WIDTH HEIGHT [features]*"
  print "Features (one or more may be added):"
  print "Rx[0-9]+y[0-9]+w[0-9]+h[0-9]+a[UDLRW]+ : set hollow rectangle"
  print "Fx[0-9]+y[0-9]+w[0-9]+h[0-9]+a[UDLRW]+ : set filled rectangle"
  print "Ex[0-9]+y[0-9]+w[0-9]+h[0-9]+a[0-100] : set random-filled rectangle with density 0-100 %"
  print "For example, \"./create_gas.py 16 16 Fx6y6w4h4aULRD Rx0y0w16h16aW > ./cases/ripple_small.gas\" is exactly what we used to generate the ripple_small test"
  print "Likewise, \"./create_gas.py 64 64 Ex1y1w62h62a10 Fx24y24w8h8aULRD Rx0y0w64h64aW\" generates a large ripple in a randomly filled gas of 10% density."
  print "Have fun!"

def main():
  if len(sys.argv) < 3:
    print_usage()
    return

  width = string.atoi(sys.argv[1]);
  height = string.atoi(sys.argv[2]);
  state = [[] for _ in range(width*height)];

  for feature in sys.argv[3:]:
    #pdb.set_trace()

    match = re.match(r"([RFE])x([0-9]+)y([0-9]+)w([0-9]+)h([0-9]+)a([UDLRW]*[0-9]*)", feature)
    if not match:
      print "Badly formatted feature! : " + feature
      print_usage()

    (f, x, y, w, h, s) = match.groups()
    x = string.atoi(x)
    y = string.atoi(y)
    w = string.atoi(w)
    h = string.atoi(h)

    chance = 100
    if (f == "E"):
        chance = string.atoi(s)

    s = (["u"] if "U" in s else []) + \
        (["d"] if "D" in s else []) + \
        (["l"] if "L" in s else []) + \
        (["r"] if "R" in s else []) + \
        (["w"] if "W" in s else [])
    for i in range(w):
      for j in range(h):
        if (f == "R") and (i > 0) and (i < (w-1)) and (j != 0) and (j != (h-1)):
            continue

        if (f == "E"):
            # This is a randomized fill. Randomize s.
            s = ["u","d","l","r"]
            # randomly permute S
            random.shuffle(s)
            for _ in range(4):
                r = random.randint(0,100)
                if r >= chance:
                    s.pop()

        state[(x+i)+(y+j)*width]  = list(set(s))


  print json.dumps({"width": width, "height": height, "state": state})


if __name__ == "__main__":
  main()

