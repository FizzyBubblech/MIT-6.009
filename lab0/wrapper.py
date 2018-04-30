import lab, json
from importlib import reload
reload(lab) # this forces the student code to be reloaded when page is refreshed

def run_test( input_data ):
  f = getattr(lab, input_data["function"])
  return f(**input_data["input"])

def init():
  p = False
  # We don't need to init anything, but we do need to have something here
  # else python complains. 

def next( d ):
  r = None
  # MUX
  r = lab.step(d["gas"])
  return r

init()
