import os
import importlib, importlib.util
import json

try:
    import lab
    importlib.reload(lab)
except ImportError:
    import solution
    lab = solution

data = {}
for i in os.listdir('test_inputs'):
    if not i.endswith('.json'):
        continue

    x = i.rsplit('.', 1)[0]
    
    with open('./test_inputs/%s.json' % x, 'r') as f:
        js = json.load(f)
        if type(js[0]) == dict:
            # Only add the test cases formatted as scheduling problems.
            data[x] = js

def load_data(d):
    return data

import traceback
def ui_assign(case):
    def trim(val, lim=400):
        val_str = str(val)
        return val_str if len(val_str)<lim else val_str[0:lim]+' ...'

    try:
        sat = lab.boolify_scheduling_problem(case[0], case[1])
        print("lab.boolify_scheduling_problem returned: " + trim(sat), flush=True)
        assign = lab.satisfying_assignment(sat)
        print("lab.satisfying_assignment returned: " + trim(assign), flush=True)
        return assign
    except:
        print(traceback.format_exc(), flush=True)
        return {}
