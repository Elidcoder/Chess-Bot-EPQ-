# Imports
import chess
from os import system
from random import randint as Random_number
from Evaluation import evaluateBoard
from Display_board import displayBoard

# Setup board 
BOARD = chess.Board()
displayBoard(BOARD)

# Run game while there is no outcome of the game
while not BOARD.outcome():
  
  # Create a list of all legal moves 
  legalMoves = list(BOARD.generate_legal_moves())
  parsedLegalMoves = [x.uci() for x in legalMoves]

  # Check if the inputted move is in the list of legal moves
  while (move := input("Enter move: ").lower().strip()) not in parsedLegalMoves:
    print("please enter a legal move")
  
  # Clears the screen then makes the legal move on the board
  system('clear')
  Makemove = chess.Move.from_uci(move)
  BOARD.push(Makemove) 
  
  # Generates a random move if there is no game outcome
  if not BOARD.outcome():  

    ## Find all legal moves for the Bot
    legalMoves = list(BOARD.generate_legal_moves())

    currentBestEvaluation = 100000

    ## Loops through elements, comparing them to find the highest rated move
    for move in legalMoves:

      ### Plays the move and evaluates it
      BOARD.push(move)
      rating = evaluateBoard(BOARD)

      ### Replaces the current move and highest rating  
      ### with the new move if it is higher rated 
      if rating < currentBestEvaluation:
        Makemove = move
        currentBestEvaluation = rating

      ### Undoes the move 
      BOARD.pop()

    ## Displays the move played as well as the board afterwards
    BOARD.push(Makemove)
    print("\nAI played:", Makemove.uci(), "\n")
    displayBoard(BOARD)

# Display a message to show who won the game
outcome = BOARD.outcome()
if outcome.winner == True:
  print("Congratulations player you won!")
elif outcome.winner == False:
  print("I'm afraid the computer won this time")
else:
  print("This game is a draw")

