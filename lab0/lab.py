def step(gas):
    # Put your solution here.  Good luck!
    
    state = gas["state"]
    width = gas["width"]
    height = gas["height"]
    
    # resolve collusions
    for cell in state:
        # with walls
        if ("w" in cell):
            for i in range(len(cell)):
                if cell[i] == 'r':
                    cell[i] = 'l'
                elif cell[i] == 'l':
                    cell[i] = 'r'
                elif cell[i] == 'u':
                    cell[i] = 'd'
                elif cell[i] == 'd':
                    cell[i] = 'u'
        # among particles
        else:
            if cell == ['r', 'l'] or cell == ['l', 'r']:
                cell.remove('r')
                cell.remove('l')
                cell.append('d')
                cell.append('u')
            elif cell == ['u', 'd'] or cell == ['d', 'u']:
                cell.remove('u')
                cell.remove('d')
                cell.append('r')
                cell.append('l')
    
    # propagate
    newState = [[] for x in range(height*width)]
    for i in range(len(state)):
        if "w" in state[i]:
            newState[i].append("w")
        if "u" in state[i]:
            newState[i-width].append("u")
        if "d" in state[i]:
            newState[i+width].append("d")
        if "r" in state[i]:
            newState[i+1].append("r")
        if "l" in state[i]:
            newState[i-1].append("l")
    gas["state"] = newState
    
    return gas
