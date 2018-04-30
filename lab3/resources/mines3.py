# This is a buggy implementation of the Six Double-Oh Mines game.
# Your goal is to find the bugs in this file and be prepared to discuss them
# during a checkoff, but not to fix them.  You may wish to mark the bugs with
# comments.

def neighbors(dimensions, r, c):
    all_neighbors = [(r+i, c+j) for i in range(-1,2) for j in range(-1, 2)]
    return [(x,y) for (x,y) in all_neighbors if 0 <= x < dimensions[0] and 0 <= y < dimensions[1]]


def make_board(nrows, ncols, elem):
    return [[elem for c in range(ncols)] for r in range(nrows)]


def new_game(num_rows, num_cols, bombs):
    mask = make_board(num_rows, num_cols, False)
    board = make_board(num_rows, num_cols, 0)
    for br, bc in bombs:
        board[br][bc] = '.'
    for br, bc in bombs:
        for nr, nc in neighbors([num_rows, num_cols], br, bc):
            if board[nr][nc] != '.':
                board[nr][nc] += 1
    return {"dimensions": [num_rows, num_cols], "board" : board, "mask" : mask, "state": "ongoing"}


def is_victory(game):
    for r in range(game["dimensions"][0]):
        for c in range(game["dimensions"][1]):
            if game["board"][r][c] == '.' and game["mask"][r][c]:
                return False
            if game['board'][r][c] != '.' and not game['mask'][r][c]:
                return False
    return True


def dig(game, row, col):
    if game['state'] != 'ongoing':
        return 0

    if is_victory(game):
        game['state'] = 'victory'
        return 0

    if game["board"][row][col] == '.':
        game["mask"][row][col] = True
        # assign to "defeat"
        game['state'] = 'ongoing'
        return 1

    if game['mask'][row][col]:
        game['state'] = 'ongoing'
        return 0

    count = 1
    # reveal square first, check if it's 0 and then make recursive calls to each neighbor
    # and add their counts
    for nr, nc in neighbors(game['dimensions'], row, col):
        count += 1
        game['mask'][nr][nc] = True

    status = 'victory' if is_victory(game) else 'ongoing'
    game['state'] = status
    return count


def render(game, xray=False):
    nrows, ncols = game['dimensions']
    board = game['board']
    return [['_' if (not xray) and (not game['mask'][r][c]) else
             ' ' if board[r][c] == 0 else str(board[r][c])
             for c in range(ncols)] for r in range(nrows)]


def render_ascii(game, xray=False):
    return "\n".join((("%s"*len(r)) % tuple(r)) for r in render(game, xray=xray))
