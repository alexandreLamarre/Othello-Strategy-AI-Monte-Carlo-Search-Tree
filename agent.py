"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

CACHE = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)
    #light
    if color == 2:
        return score[1] - score[0]
        #dark
    elif color == 1:
        return score[0] - score[1]


# Better heuristic value of board
#stable disks and wedges
def compute_heuristic(board, color): #not implemented, optional
    value = compute_utility(board,color)
    pid = color

    # assign corners high values, about of 3 because you'll be able to usually play
    # 3 pieces in that vicinity that cannot be flipped
    c_value = 3
    if board[0][0] == pid:
        base += c_value
    if board[-1][-1] == pid:
        base += c_value
    if board[-1][0] == pid:
        base += c_value
    if board[0][-1] == pid:
        base += c_value

    # avoid playing on non-corner diagonals "X's"
    c_value = -4
    #avoid playing in C-squares
    if pid == board[2][0]:
        base += c_value
    if pid == board[6][0]:
        base -= c_value
    if pid == board[0][6]:
        base -= c_value
    if pid == board[2][-1]:
        base -= c_value
    if pid == board[6][-1]:
        base -= c_value
    if pid == board[-1][2]:
        base -= c_value
    if pid == board[-1][6]:
        base -= c_value

    return base #change this!

############ MINIMAX ###############################
def switch_player(player):
    return 1 if player == 2 else 2

def minimax_min_node(board, color, limit, caching = 0): #returns lowest possible utility
    if caching and board in CACHE:
        return CACHE[board]

    # Other player plays
    color = switch_player(color)
    next = get_possible_moves(board,color)

    if next == [] or limit == 0:
        value = -compute_utility(board,color)
        if caching:
            CACHE[board] = [None,value]
        return [None, value]
    else:
        #Switch back to original player
        other = switch_player(color)
        value = None
        move = None
        for n in next:
            (new_move,new_value) = minimax_max_node(play_move(board,color,n[0], n[1]), other, limit-1, caching)
            if value == None:
                value = new_value
                move = n
            elif new_value < value:
                value = new_value
                move = n
        if caching:
            CACHE[board] = [move, value]
        return [move, value]

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility

    if caching and board in CACHE:
        return CACHE[board]
    next = get_possible_moves(board,color)

    if next == [] or limit == 0:
        value = compute_utility(board,color)
        if caching:
            CACHE[board] = [None, value]
        return [None, value]

    else:
        move = None
        value = None
        for n in next:
            (new_move, new_value) = minimax_min_node(play_move(board, color, n[0], n[1]), color, limit-1, caching)
            if value == None:
                value = new_value
                move = n
            elif new_value > value:
                value = new_value
                move = n

        if caching:
            CACHE[board] = [move, value]
        return [move, value]


def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    board = tuple([tuple(row) for row in board])
    CACHE.clear()
    (move,value) = minimax_max_node(board,color,limit,caching)
    CACHE.clear()
    return move


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    if caching and board in CACHE:
        return CACHE[board]

    color = switch_player(color)
    next  = get_possible_moves(board,color)


    if ordering:
        explore = []
        for n in next:
            other = switch_player(color)
            v = compute_utility(play_move(board,color,n[0], n[1]), other)
            explore.append([n,v])
        explore.sort(key = lambda x: x[1], reverse = False)
        next = [i[0] for i in explore]


    if next == [] or limit == 0:
        value = -compute_utility(board,color)
        if caching:
            CACHE[board] = [None,value]
        return [None, value]
    else:
        move = None
        for n in next:
            other = switch_player(color)
            new_beta = alphabeta_max_node(play_move(board,color,n[0],n[1]), other, alpha, beta, limit-1, caching, ordering)[1]
            if new_beta < beta:
                beta = new_beta
                move = n
            if beta<= alpha:
                break
        if caching:
            CACHE[board] = [move,beta]
        return [move,beta]

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching and board in CACHE:
        return CACHE[board]

    next = get_possible_moves(board,color)

    if ordering:
        explore = []
        for n in next:
            v = compute_utility(play_move(board,color,n[0],n[1]),color)
            explore.append([n,v])
        explore.sort(key = lambda x: x[1], reverse = True)
        next = [i[0] for i in explore]


    if next == [] or limit == 0:
        value = compute_utility(board, color)
        if caching:
            CACHE[board] = [None,value]
        return [None,value]
    else:
        move = None
        for n in next:
            new_alpha = alphabeta_min_node(play_move(board,color,n[0], n[1]), color, alpha, beta,limit-1, caching, ordering)[1]
            if new_alpha > alpha:
                alpha = new_alpha
                move = n
            if beta <= alpha:
                break
        if caching:
            CACHE[board] = [move,alpha]
        return [move,alpha]

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    board = tuple([tuple(row) for row in board])
    alpha = float("-inf")
    beta = float("inf")
    CACHE.clear()
    (move,value) = alphabeta_max_node(board,color,alpha,beta, limit, caching, ordering)
    CACHE.clear()
    return move


####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Max") # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
