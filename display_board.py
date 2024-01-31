# Setup constants for each colour 
GOLD  = "\u001b[0m" + "\u001b[33;1m" 
RED   = "\u001b[31m" 
BLUE  = "\u001b[34m" 
GREEN = "\u001b[42m"
WHITE = "\u001b[47m"
white = "\u001b[37m"

# Define the square colours, piece colours and linenumber
SQUARE_COLOURS = [WHITE, GREEN]
UNICODE_DICT = {"p":RED + "♟", "b":RED + "♝", "n":RED + "♞", "r": RED + "♜", "q": RED + "♛", "k":RED + "♚", "P": BLUE +"♙", "B": BLUE +"♗", "N":BLUE+"♘", "R": BLUE +"♖", "Q": BLUE +"♕", "K": BLUE +"♔"}

# Generates a neater output for a board than regular printing
def display_board_as_white(board):

  ## Initial print and initialises remaining vars so everything else lines up
  print(GOLD + "8  ", end = "")
  line_number = 7
  colour_enum = 1
  
  ## Loop through the board FEN turning it into a good output string
  for character in board.board_fen():
    if character == "/" :
      print("\n" + GOLD + str(line_number) + "  ", end = "")
      line_number -= 1
    elif character in {"1", "2","3", "4", "5", "6", "7", "8"}:     
      for x in range(int(character)):
        print(SQUARE_COLOURS[colour_enum] + " ", end = "  ")
        colour_enum = 1 - colour_enum
      colour_enum = 1 - colour_enum
    else:
      print(SQUARE_COLOURS[colour_enum] + UNICODE_DICT[character], end = "  ")
    colour_enum = 1 - colour_enum

  ## Print the column letters
  print(GOLD + "\n   A  B  C  D  E  F  G  H", end = white + "\n")

def display_board_as_black(board):
  
  ## Initial print and initialises remaining vars so everything else lines up
  print(GOLD + "1  ", end = "")
  line_number = 2
  colour_enum = 1
  
  ## Loop through the board FEN turning it into a good output string
  for character in board.board_fen()[::-1]:
    if character == "/" :
      print("\n" + GOLD + str(line_number) + "  ", end = "")
      line_number += 1
    elif character in {"1", "2","3", "4", "5", "6", "7", "8"}:     
      for x in range(int(character)):
        print(SQUARE_COLOURS[colour_enum] + " ", end = "  ")
        colour_enum = 1 - colour_enum
      colour_enum = 1 - colour_enum
    else:
      print(SQUARE_COLOURS[colour_enum] + UNICODE_DICT[character], end = "  ")
    colour_enum = 1 - colour_enum

  ## Print the column letters
  print(GOLD + "\n   H  G  F  E  D  C  B  A", end = white + "\n")
