# Generates a neater output for a board than regular printing
def displayBoard(Board):
  
  ## Setup constants for each colour 
  GOLD  = "\u001b[0m" +"\u001b[33;1m" 
  RED   = "\u001b[31m" 
  BLUE  = "\u001b[34m" 
  GREEN = "\u001b[42m"
  WHITE = "\u001b[47m"
  white = "\u001b[37m"

  ## Define the square colours, piece colours and linenumber
  squareColours = [WHITE, GREEN]
  unicode_table = {"p":RED + "♟", "b":RED + "♝", "n":RED + "♞", "r": RED + "♜", "q": RED + "♛", "k":RED + "♚", "P": BLUE +"♙", "B": BLUE +"♗", "N":BLUE+"♘", "R": BLUE +"♖", "Q": BLUE +"♕", "K": BLUE +"♔"}
  linenumber    = 7

  ## Initial print so everything else lines up
  print(GOLD + "8  ", end = "")
  colourEnum = 1

  ## Loop through the board FEN turning it into a good output string
  for l in Board.board_fen():
    if l == "/" :
      print("\n" + GOLD + str(linenumber) + "  ", end = "")
      linenumber -= 1
    elif l in {"1", "2","3", "4", "5", "6", "7", "8"}:     
      for x in range(int(l)):
        print(squareColours[colourEnum] + " ", end = "  ")
        colourEnum = 1 - colourEnum
      colourEnum = 1 - colourEnum
    else:
      print(squareColours[colourEnum] + unicode_table[l], end = "  ")
    colourEnum = 1 - colourEnum

  ## Print the column letters
  print(GOLD+"\n   A  B  C  D  E  F  G  H", end = white + "\n")
