# Imports
import chess
from os import system
from Evaluation import alphaBeta, evaluateMoveOnBoard
import Display_board as display

# Convenient board displayer
Playeriswhite = True
def outputboard():
  if Playeriswhite:
    display.displayBoardAsWhite(BOARD)
  else:
    display.displayBoardAsBlack(BOARD)

# Setup board, get the player colour and initial depth
BOARD = chess.Board()
colour = input("What colour are you?").upper()
if colour not in ["WHITE","W"]:
  Playeriswhite = False
outputboard()
depthToSearchAt = 4

# Since sorted is ascending and we want to search the better ones first,
# white player will want the biggest (so lowest if all negative) and black
# will just want the lowest value first so first if all positive
whiteSortingKey = lambda x: - evaluateMoveOnBoard(x, BOARD)
blackSortingKey = lambda x: evaluateMoveOnBoard(x, BOARD)

# If the bot is white and initial boardstate isn't over then the bot starts
if not Playeriswhite and not BOARD.outcome():

  ## Find all legal moves for the Bot and initialise current evaluation
  alpha = -100000
  beta = 100000

  ## Loops through elements, comparing them to find the highest rated move
  for move in sorted(BOARD.generate_legal_moves(), key = blackSortingKey):

    ### Plays the move and evaluates it
    BOARD.push(move)
    rating = -alphaBeta(-beta,- alpha, BOARD, depthToSearchAt)
    print(move, rating)
    ### Replaces the current move and highest rating  
    ### with the new move if it is higher rated 
    if rating > alpha:
      Makemove = move
      alpha = rating

    ### Undoes the move 
    BOARD.pop()

  ## Displays the move played as well as the board afterwards
  BOARD.push(Makemove)
  print("\nAI played:", Makemove.uci(), "\n")
  outputboard()

# Run game while there is no outcome of the game
while not BOARD.outcome():
  
  # Create a parsed list of all legal moves 
  parsedLegalMoves = [x.uci() for x in list(BOARD.generate_legal_moves())]

  # Check if the inputted move is in the list of legal moves
  while (move := input("Enter move: ").lower().strip()) not in parsedLegalMoves:
    print("please enter a legal move")
  
  # Clears the screen then makes the legal move on the board
  system('clear')
  Makemove = chess.Move.from_uci(move)
  BOARD.push(Makemove) 
  outputboard()
  
  if not BOARD.outcome():  

    alpha = -100000
    beta  =  100000
    for move in sorted(BOARD.generate_legal_moves(), key = blackSortingKey):

      ### Plays the move and evaluates it
      BOARD.push(move)
      rating = -alphaBeta(-beta,- alpha, BOARD, depthToSearchAt)
      print(move, rating)

      ### Replaces the current move and highest rating  
      ### with the new move if it is higher rated 
      if rating > alpha:
        Makemove = move
        alpha = rating

      ### Undoes the move 
      BOARD.pop()
    
    ### Displays the move played as well as the board afterwards
    BOARD.push(Makemove)
    print("\nAI played:", Makemove.uci(), "\n")
    outputboard()

# Display a message to show who won the game
outcome = BOARD.outcome()
if outcome.winner == True:
  print("Congratulations player you won!")
elif outcome.winner == False:
  print("I'm afraid the computer won this time")
else:
  print("This game is a draw")
