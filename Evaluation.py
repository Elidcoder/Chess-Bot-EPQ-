# Assign each piece its value with sign of its player
scoremap = {"p":-1, "b":-3, "n":-3, "r": -5, "q": -9, "k":0, "8":0, "/":0, "1":0, "2":0,"3":0, "4":0, "5":0,"6":0, "7":0, "8":0,"9":0, "P":1, "B":3, "N":3, "R": 5, "Q": 9, "K":0}

# Function to figure out the numeric value of a board
def evaluateBoard(board):
  
  # Since the player is white, if it is checkmate after the 
  # Bot's move, then it should be a very low score (good)
  if board.is_checkmate():
    return -10000
  
  # Otherwise sum the values of each piece on the board
  resultstring = board.board_fen()
  score = sum (map ((lambda x: scoremap[x]), resultstring))

  # Return the boards evaluation
  return score