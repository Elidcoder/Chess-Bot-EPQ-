# Imports
import chess
from os import system
from Evaluation import alphaBeta, evaluateMoveOnBoard
import Display_board as display

# Define the depth to search at
depthToSearchAt = 4

# Convenient board displayer
playerIsWhite = True
def outputboard():
  if playerIsWhite:
    display.displayBoardAsWhite(BOARD)
  else:
    display.displayBoardAsBlack(BOARD)

# Setup board, get the player colour and display the board 
BOARD = chess.Board()
colour = input("What colour are you?").upper()
if colour not in ["WHITE","W"]:
  playerIsWhite = False
outputboard()


# Assign each move its immediate value from whites perspective, 
# this is flipped with reverse if the bot is black
sortingKey = lambda move: - evaluateMoveOnBoard(move, BOARD)

# If the bot is white and initial boardstate isn't over then the bot starts
if not playerIsWhite and not BOARD.outcome():
  alpha, beta = -100000, 100000

  ## Loops through elements, comparing them to find the highest rated move
  for move in sorted(BOARD.generate_legal_moves(), key = sortingKey, reverse = playerIsWhite):

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
  
  ## Create a parsed list of all legal moves 
  parsedLegalMoves = [x.uci() for x in list(BOARD.generate_legal_moves())]

  ## Check if the inputted move is in the list of legal moves
  while (move := input("Enter move: ").lower().strip()) not in parsedLegalMoves:
    print("please enter a legal move")
  
  ## Clears the screen then makes the legal move on the board
  system('clear')
  Makemove = chess.Move.from_uci(move)
  BOARD.push(Makemove) 
  outputboard()
  
  ## If the game isn't over the bot takes a turn, initialising variables
  ## and then looping through the legal moves
  if not BOARD.outcome():  

    alpha, beta = -100000, 100000
    for move in sorted(BOARD.generate_legal_moves(), key = sortingKey, reverse = playerIsWhite):

      #### Plays the move and evaluates it
      BOARD.push(move)
      rating = -alphaBeta(-beta,- alpha, BOARD, depthToSearchAt)
      print(move, rating)

      #### Replaces the current move and highest rating  
      #### with the new move if it is higher rated 
      if rating > alpha:
        Makemove = move
        alpha = rating

      #### Undoes the move 
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
