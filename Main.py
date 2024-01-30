# Imports
import chess
from os import system
from Evaluation import ABmaxi, ABmini
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
if colour not in ["WHITE","W"]:Playeriswhite = False
outputboard()
depthToSearchAt = 2

# If the bot is white and initial boardstate isn't over then the bot starts
if not Playeriswhite and not BOARD.outcome():

  ## Find all legal moves for the Bot and initialise current evaluation
  currentBestEvaluation = -100000

  ## Loops through elements, comparing them to find the highest rated move
  for move in list(BOARD.generate_legal_moves()):

    ### Plays the move and evaluates it
    BOARD.push(move)
    rating = ABmaxi(-10000,10000, BOARD, depthToSearchAt)

    ### Replaces the current move and highest rating  
    ### with the new move if it is higher rated 
    if rating > currentBestEvaluation:
      Makemove = move
      currentBestEvaluation = rating

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
  
  # Generates a random move if there is no game outcome
  if not BOARD.outcome():  
    if Playeriswhite:
      ## Initialise current evaluation
      currentBestEvaluation = 100000

      ## Loops through elements, comparing them to find the lowest rated move
      for move in list(BOARD.generate_legal_moves()):

        ### Plays the move and evaluates it
        BOARD.push(move)
        rating = ABmini(-10000, 10000, BOARD, depthToSearchAt)

        ### Replaces the current move and lowest rating  
        ### with the new move if it is lower rated 
        if rating < currentBestEvaluation:
          Makemove = move
          currentBestEvaluation = rating

        ### Undoes the move 
        BOARD.pop()

    else:
      
      ### Find all legal moves for the Bot and initialise current evaluation
      currentBestEvaluation = -100000

      ### Loops through elements, comparing them to find the highest rated move
      for move in list(BOARD.generate_legal_moves()):

        #### Plays the move and evaluates it
        BOARD.push(move)
        rating = ABmaxi(-10000, 10000, BOARD, depthToSearchAt)

        #### Replaces the current move and highest rating  
        #### with the new move if it is higher rated 
        if rating > currentBestEvaluation:
          Makemove = move
          currentBestEvaluation = rating

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
