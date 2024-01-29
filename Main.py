# Imports
import chess
from os import system
from random import randint as Random_number
from Evaluation import evaluateBoard

# Setup board 
BOARD = chess.Board()
print(BOARD)

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
    Legal = list(BOARD.generate_legal_moves())

    currentBestEvaluation = 100000

    ## Loops through elements, comparing them to find the highest rated move
    for m in Legal:

      ### Plays the move and evaluates it
      BOARD.push(m)
      rating = evaluateBoard(BOARD)

      ### Replaces the current move and highest rating  
      ### with the new move if it is higher rated 
      if rating < currentBestEvaluation:
        Makemove = m
        currentBestEvaluation = rating

      ### Undoes the move 
      BOARD.pop()

    ## Displays the move played as well as the board afterwards
    BOARD.push(Makemove)
    print("\nAI played:", Makemove.uci(), "\n")
    print(BOARD)
