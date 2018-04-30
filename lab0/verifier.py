import traceback

def verify( result, input_data, gold ):
  ok = True
   
  try:
    ok = ok and (result["height"] == gold["height"])
    ok = ok and (result["width"] == gold["width"])
    ok = ok and (len(result["state"]) == len(gold["state"]))
   
    for i in range(len(gold["state"])):
      result["state"][i].sort()
      gold["state"][i].sort()
      ok = ok and (result["state"][i] == gold["state"][i])
    message = "Your gas is invalid.  Try again."
    if ok:
      message = "Hooray!  Your gas works."
  except:
    traceback.print_exc();
    ok = False
    message = "Alas, your code crashed :(. Stack trace is printed above so you can debug."

  return ok, message
