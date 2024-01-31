# Imports
import chess
from os import system
from Evaluation import alpha_beta, evaluate_move_on_board
import Display_board as display

# Define the depth to search at
SEARCH_DEPTH = 4

# Convenient board displayer
USER_IS_WHITE = True
def outputboard():
  if USER_IS_WHITE:
    display.display_board_as_white(BOARD)
  else:
    display.display_board_as_black(BOARD)

# Setup board, get the player colour and display the board 
BOARD = chess.Board()
colour = input("What colour are you?").upper()
if colour not in ["WHITE","W"]:
  USER_IS_WHITE = False
outputboard()


# Assign each move its immediate value from whites perspective, 
# this is flipped with reverse if the bot is black
SORTING_KEY = lambda move: - evaluate_move_on_board(move, BOARD)

# If the bot is white and initial boardstate isn't over then the bot starts
if not USER_IS_WHITE and not BOARD.outcome():

  ## Set alpha & beta to lowest and highest possible values. This
  ## makes alpha_beta work and ensures that move_to_make is always defined
  alpha, beta = -100000, 100000

  ## Loops through elements, comparing them to find the highest rated move
  for move in sorted(BOARD.generate_legal_moves(), 
                     key = SORTING_KEY, reverse = USER_IS_WHITE):

    ### Plays the move and evaluates it
    BOARD.push(move)
    rating = -alpha_beta(-beta,- alpha, BOARD, SEARCH_DEPTH)
    print(move, rating)
    ### Replaces the current move and highest rating  
    ### with the new move if it is higher rated 
    if rating > alpha:
      move_to_make = move
      alpha = rating

    ### Undoes the move 
    BOARD.pop()

  ## Displays the move played as well as the board afterwards
  BOARD.push(move_to_make)
  print("\nAI played:", move_to_make.uci(), "\n")
  outputboard()

# Run game while there is no outcome of the game
while not BOARD.outcome():
  
  ## Create a parsed list of all legal moves 
  parsed_legal_moves = [x.uci() for x in list(BOARD.generate_legal_moves())]

  ## Check if the inputted move is in the list of legal moves
  while ((move := input("Enter move: ").lower().strip()) 
                              not in parsed_legal_moves):
    print("please enter a legal move")
  
  ## Clears the screen then makes the legal move on the board
  system('clear')
  move_to_make = chess.Move.from_uci(move)
  BOARD.push(move_to_make) 
  outputboard()
  
  ## If the game isn't over the bot takes a turn, initialising variables
  ## and then looping through the legal moves
  if not BOARD.outcome():  

    ## Set alpha & beta to lowest and highest possible values. This
    ## makes alpha_beta work and ensures that move_to_make is always defined
    alpha, beta = -100000, 100000
    for move in sorted(BOARD.generate_legal_moves(), 
                       key = SORTING_KEY, reverse = USER_IS_WHITE):

      #### Plays the move and evaluates it
      BOARD.push(move)
      rating = -alpha_beta(-beta,- alpha, BOARD, SEARCH_DEPTH)
      print(move, rating)

      #### Replaces the current move and highest rating  
      #### with the new move if it is higher rated 
      if rating > alpha:
        move_to_make = move
        alpha = rating

      #### Undoes the move 
      BOARD.pop()
    
    ### Displays the move played as well as the board afterwards
    BOARD.push(move_to_make)
    print("\nAI played:", move_to_make.uci(), "\n")
    outputboard()

# Display a message to show who won the game
outcome = BOARD.outcome()
if outcome.winner == True:
  print("Congratulations player you won!")
elif outcome.winner == False:
  print("I'm afraid the computer won this time")
else:
  print("This game is a draw")
