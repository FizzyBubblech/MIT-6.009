# This file has no bugs

def dump(game):
    lines = ["dimensions: {}".format(game["dimensions"]),
             "board: {}".format("\n       ".join(map(str, game["board"]))),
             "mask:  {}".format("\n       ".join(map(str, game["mask"])))]
    print("\n".join(lines))


def new_game(num_rows, num_cols, bombs):
    board = []
    for r in range(num_rows):
        row = []
        for c in range(num_cols):
            if [r,c] in bombs or (r,c) in bombs:
                row.append('.')
            else:
                row.append(0)
        board.append(row)
    mask = []
    for r in range(num_rows):
        row = []
        for c in range(num_cols):
            row.append(False)
        mask.append(row)
    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == 0:
                neighbor_bombs = 0
                if 0 <= r-1 < num_rows:
                    if 0 <= c-1 < num_cols:
                        if board[r-1][c-1] == '.':
                            neighbor_bombs += 1
                if 0 <= r < num_rows:
                    if 0 <= c-1 < num_cols:
                        if board[r][c-1] == '.':
                            neighbor_bombs += 1
                if 0 <= r+1 < num_rows:
                    if 0 <= c-1 < num_cols:
                        if board[r+1][c-1] == '.':
                            neighbor_bombs += 1
                if 0 <= r-1 < num_rows:
                    if 0 <= c < num_cols:
                        if board[r-1][c] == '.':
                            neighbor_bombs += 1
                if 0 <= r < num_rows:
                    if 0 <= c < num_cols:
                        if board[r][c] == '.':
                            neighbor_bombs += 1
                if 0 <= r+1 < num_rows:
                    if 0 <= c < num_cols:
                        if board[r+1][c] == '.':
                            neighbor_bombs += 1
                if 0 <= r-1 < num_rows:
                    if 0 <= c+1 < num_cols:
                        if board[r-1][c+1] == '.':
                            neighbor_bombs += 1
                if 0 <= r < num_rows:
                    if 0 <= c+1 < num_cols:
                        if board[r][c+1] == '.':
                            neighbor_bombs += 1
                if 0 <= r+1 < num_rows:
                    if 0 <= c+1 < num_cols:
                        if board[r+1][c+1] == '.':
                            neighbor_bombs += 1
                board[r][c] = neighbor_bombs
    return {"dimensions": [num_rows, num_cols], "board" : board, "mask" : mask, "state": "ongoing"}


def reveal_squares(game, row, col):
    if game["board"][row][col] != 0:
        if game["mask"][row][col]:
            return 0
        else:
            game["mask"][row][col] = True
            return 1
    else:
        revealed = set()
        for r in range(row - 1, row + 2):
            if r < game["dimensions"][0]:
                if r >= 0:
                    for c in range(col - 1, col + 2):
                        if c < game["dimensions"][1]:
                            if c >= 0:
                                if game["board"][r][c] != '.' and not game["mask"][r][c] == True:
                                    game["mask"][r][c] = True
                                    revealed.add((r, c))
        total = len(revealed)
        for r,c in revealed:
            if game["board"][r][c] != "." :
                total += reveal_squares(game, r, c)
        return total


def dig(game, row, col):
    if game["state"] == "defeat" or game["state"] == "victory":
        return 0

    if game["board"][row][col] == '.':
        game["mask"][row][col] = True
        game["state"] = "defeat"
        return 1
    
    bombs = 0
    coveredSquares = 0
    for r in range(game["dimensions"][0]):
        for c in range(game["dimensions"][1]):
            if game["board"][r][c] == ".":
                if  game["mask"][r][c] == True:
                    bombs += 1
            elif game["mask"][r][c] == False:
                coveredSquares += 1
    if bombs != 0:
        game["state"] = "defeat"
        return 0
    if coveredSquares == 0:
        game["state"] = "victory"
        return 0
    
    revealed = reveal_squares(game, row, col)
    bombs = 0
    coveredSquares = 0
    for r in range(game["dimensions"][0]):
        for c in range(game["dimensions"][1]):
            if game["board"][r][c] == ".":
                if  game["mask"][r][c] == True:
                    bombs += 1
            elif game["mask"][r][c] == False:
                coveredSquares += 1
    badSquares = bombs + coveredSquares
    if badSquares > 0:
        game["state"] = "ongoing"
        return revealed
    else:
        game["state"] = "victory"
        return revealed


def render(game, xray=False):
    nrows, ncols = game['dimensions']
    board = game['board']
    return [['_' if (not xray) and (not game['mask'][r][c]) else
             ' ' if board[r][c] == 0 else str(board[r][c])
             for c in range(ncols)] for r in range(nrows)]


def render_ascii(game, xray=False):
    return "\n".join("".join(r) for r in render(game, xray=xray))
