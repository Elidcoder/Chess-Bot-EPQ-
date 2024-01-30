# Imports
import chess

# Define pieces
pawn = chess.Piece(1, False)
PAWN = chess.Piece(1, True)
knight = chess.Piece(2, False)
KNIGHT = chess.Piece(2, True)
bishop = chess.Piece(3, False)
BISHOP = chess.Piece(3, True)
rook = chess.Piece(4, False)
ROOK = chess.Piece(4, True)
queen = chess.Piece(5, False)
QUEEN = chess.Piece(5, True)
king = chess.Piece(6, False)
KING = chess.Piece(6, True)

#Evaluation function and its constant
pieceValues = {PAWN: {0:0.0,   1:0.0,   2:0.0,   3:0.0,   4:0.0,   5:0.0,   6:0.0,   7:0.0,   8:9.5,   9:9.5,  10:9.0,  11:8.5,  12:8.5,  13:9.0,  14:9.5,  15:9.5,  16:10.75,  17:10.0,  18:10.5,  19:9.5,  20:9.5,  21:10.5,  22:10.0,  23:10.75,  24:10.75,  25:10.0,  26:10.5,  27:11.0,  28:11.0,  29:10.0,  30:10.0,  31:10.75,  32:11.25,  33:10.5,  34:11.0,  35:11.5,  36:11.5,  37:10.5,  38:10.5,  39:11.25, 40:12.25,  41:11.5,  42:12.0,  43:12.5,  44:12.5,  45:11.5,  46:11.5,  47:12.25,  48:13.75,  49:13.0,  50:13.5,  51:14.0,  52:14.0,  53:13.5,  54:13.0,  55:13.75,  56:0.0,  57:0.0,  58:0.0,  59:0.0,  60:0.0,  61:0.0,  62:0.0,  63:0.0}, pawn:{0:-0.0,   1:-0.0,   2:-0.0,   3:-0.0,   4:-0.0,   5:-0.0,   6:-0.0,   7:-0.0,   8:-13.75,   9:-13.0,  10:-13.5,  11:-14.0,  12:-14.0,  13:-13.5,  14:-13.0,  15:-13.75,  16:-12.25,  17:-11.5,  18:-12.0,  19:-12.5,  20:-12.5,  21:-11.5,  22:-11.5,  23:-12.25,  24:-11.25,  25:-10.5,  26:-11.0,  27:-11.5,  28:-11.5,  29:-10.5,  30:-10.5,  31:-11.25,  32:-10.75,  33:-10.0,  34:-10.5,  35:-11.0,  36:-11.0,  37:-10.0,  38:-10.0,  39:-10.75, 40:-10.75,  41:-10.0,  42:-10.5,  43:-9.5,  44:-9.5,  45:-10.5,  46:-10.0,  47:-10.75,  48:-9.5,  49:-9.5,  50:-9.0,  51:-8.5,  52:-8.5,  53:-9.0,  54:-9.5,  55:-9.5,  56:-0.0,  57:-0.0,  58:-0.0,  59:-0.0,  60:-0.0,  61:-0.0,  62:-0.0,  63:-0.0}, KNIGHT: {0:28.5,  1:28.5,  2:28.5,  3:28,  4:28,  5:28.5,  6:28.5,  7:28.5,  8:28.5,  9:29.5, 10:29.5, 11:29, 12:29, 13:29.5, 14:29.5, 15:28.5, 16:28.5, 17:29.5, 18:30.5, 19:30, 20:30, 21:30.5, 22:29.5, 23:28.5, 24:28.5, 25:29.5, 26:30.5, 27:31.5, 28:31.5, 29:30.5, 30:29.5, 31:28.5, 32:28.5, 33:29.5, 34:30.75, 35:31.5, 36:31.5, 37:30.75, 38:29.5, 39:28.5, 40:28.5, 41:29.5, 42:30.5, 43:30.5, 44:30.5, 45:30.5, 46:29.5, 47:28.5, 48:28.5, 49:29.5, 50:29.5, 51:29.5, 52:29.5, 53:29.5, 54:29.5, 55:28.5, 56:28.5, 57:28.5, 58:28.5, 59:28.5, 60:28.5, 61:28.5, 62:28.5, 63:28.5}, knight: {0:-28.5,  1:-28.5,  2:-28.5,  3:-28.5,  4:-28.5,  5:-28.5,  6:-28.5,  7:-28.5,  8:-28.5,  9:-29.5, 10:-29.5, 11:-29.5, 12:-29.5, 13:-29.5, 14:-29.5, 15:-28.5, 16:-28.5, 17:-29.5, 18:-30.5, 19:-30.5, 20:-30.5, 21:-30.5, 22:-29.5, 23:-28.5, 24:-28.5, 25:-29.5, 26:-30.75, 27:-31.5, 28:-31.5, 29:-30.75, 30:-29.5, 31:-28.5, 32:-28.5, 33:-29.5, 34:-30.5, 35:-31.5, 36:-31.5, 37:-30.5, 38:-29.5, 39:-28.5, 40:-28.5, 41:-29.5, 42:-30.5, 43:-30, 44:-30, 45:-30.5, 46:-29.5, 47:-28.5, 48:-28.5, 49:-29.5, 50:-29.5, 51:-29, 52:-29, 53:-29.5, 54:-29.5, 55:-28.5, 56:-28.5, 57:-28.5, 58:-28.5, 59:-28, 60:-28, 61:-28.5, 62:-28.5, 63:-28.5},BISHOP:{0:27.0,   1:28.0,   2:28.0,   3:28.0,   4:28.0,   5:28.0,   6:28.0,   7:27.0,   8:28.0,   9:29.5,  10:29.5,  11:29.5,  12:29.5,  13:29.5,  14:29.5,  15:28.0,  16:29.5,  17:31.25,  18:30.75,  19:30.5,  20:30.5,  21:30.75,  22:31.25,  23:29.5,  24:30.5,  25:32.0,  26:31.5,  27:31.5,  28:31.5,  29:31.5,  30:32.0,  31:30.5,  32:30.0,  33:31.0,  34:32.0,  35:31.5,  36:31.5,  37:32.0,  38:31.0,  39:30.0, 40:30.0,  41:30.5,  42:31.0,  43:30.5,  44:30.5,  45:31.0,  46:30.5,  47:30.0,  48:28.75,  49:30.0,  50:30.25,  51:30.5,  52:30.5,  53:30.25,  54:30.0,  55:28.75,  56:27.0,  57:28.0,  58:28.0,  59:28.0,  60:28.0,  61:28.0,  62:28.0,  63:27.0}, bishop:{0:-27.0,   1:-28.0,   2:-28.0,   3:-28.0,   4:-28.0,   5:-28.0,   6:-28.0,   7:-27.0,   8:-28.75,   9:-30.0,  10:-30.25,  11:-30.5,  12:-30.5,  13:-30.25,  14:-30.0,  15:-28.75,  16:-30.0,  17:-30.5,  18:-31.0,  19:-30.5,  20:-30.5,  21:-31.0,  22:-30.5,  23:-30.0,  24:-30.0,  25:-31.0,  26:-32.0,  27:-31.5,  28:-31.5,  29:-32.0,  30:-31.0,  31:-30.0,  32:-30.5,  33:-32.0,  34:-31.5,  35:-31.5,  36:-31.5,  37:-31.5,  38:-32.0,  39:-30.5, 40:-29.5,  41:-31.25,  42:-30.75,  43:-30.5,  44:-30.5,  45:-30.75,  46:-31.25,  47:-29.5,  48:-28.0,  49:-29.5,  50:-29.5,  51:-29.5,  52:-29.5,  53:-29.5,  54:-29.5,  55:-28.0,  56:-27.0,  57:-28.0,  58:-28.0,  59:-28.0,  60:-28.0,  61:-28.0,  62:-28.0,  63:-27.0}, ROOK: {0:50,  1:50,  2:50.5,  3:51,  4:51,  5:50.5,  6:50,  7:50,  8:50,  9:50, 10:50, 11:50, 12:50, 13:50, 14:50, 15:49.5, 16:49.5, 17:50, 18:50, 19:50, 20:50, 21:50, 22:50, 23:49.5, 24:49.5, 25:50, 26:50, 27:50, 28:50, 29:50, 30:50, 31:49.5, 32:49.5, 33:50, 34:50, 35:50, 36:50, 37:50, 38:50, 39:49.5, 40:49.5, 41:50, 42:50, 43:50, 44:50, 45:50, 46:50, 47:49.5, 48:50.5, 49:51, 50:51, 51:51.5, 52:51.5, 53:51, 54:51, 55:50.5, 56:50, 57:50, 58:50, 59:50, 60:50, 61:50, 62:50, 63:50}, rook: {0:-50,  1:-50,  2:-50,  3:-50,  4:-50,  5:-50,  6:-50,  7:-50,  8:-50.5,  9:-51, 10:-51, 11:-51.5, 12:-51.5, 13:-51, 14:-51, 15:-50.5, 16:-49.5, 17:-50, 18:-50, 19:-50, 20:-50, 21:-50, 22:-50, 23:-49.5, 24:-49.5, 25:-50, 26:-50, 27:-50, 28:-50, 29:-50, 30:-50, 31:-49.5, 32:-49.5, 33:-50, 34:-50, 35:-50, 36:-50, 37:-50, 38:-50, 39:-49.5, 40:-49.5, 41:-50, 42:-50, 43:-50, 44:-50, 45:-50, 46:-50, 47:-49.5, 48:-50, 49:-50, 50:-50, 51:-50, 52:-50, 53:-50, 54:-50, 55:-49.5, 56:-50, 57:-50, 58:-50.5, 59:-51, 60:-51, 61:-50.5, 62:-50, 63:-50}, QUEEN: {0:89,   1:89,   2:89,   3:89,   4:89,   5:89,   6:89,   7:89,   8:89,   9:90,  10:90,  11:90,  12:90,  13:90,  14:90,  15:89,  16:89,  17:90,  18:91,  19:91,  20:91,  21:91,  22:90,  23:89,  24:89,  25:90,  26:91,  27:91,  28:91,  29:91,  30:90,  31:89,  32:89,  33:90,  34:91,  35:91,  36:91,  37:91,  38:90,  39:89, 40:89,  41:90,  42:91,  43:91,  44:91,  45:91,  46:90,  47:89,  48:89,  49:90,  50:90,  51:90,  52:90,  53:90,  54:90,  55:89,  56:89,  57:89,  58:89,  59:89,  60:89,  61:89,  62:89,  63:89}, queen: {0:-89,   1:-89,   2:-89,   3:-89,   4:-89,   5:-89,   6:-89,   7:-89,   8:-89,   9:-90,  10:-90,  11:-90,  12:-90,  13:-90,  14:-90,  15:-89,  16:-89,  17:-90,  18:-91,  19:-91,  20:-91,  21:-91,  22:-90,  23:-89,  24:-89,  25:-90,  26:-91,  27:-91,  28:-91,  29:-91,  30:-90,  31:-89,  32:-89,  33:-90,  34:-91,  35:-91,  36:-91,  37:-91,  38:-90,  39:-89, 40:-89,  41:-90,  42:-91,  43:-91,  44:-91,  45:-91,  46:-90,  47:-89,  48:-89,  49:-90,  50:-90,  51:-90,  52:-90,  53:-90,  54:-90,  55:-89,  56:-89,  57:-89,  58:-89,  59:-89,  60:-89,  61:-89,  62:-89,  63:-89}, KING: {0:0,   1:1.75,   2:1.5,   3:0,   4:0,   5:0,   6:1.5,   7:0,  8:-1.5,   9:-0.75,  10:-0.5,  11:0,  12:0,  13:-0.5,  14:-0.75,  15:-1.5,  16:2.5,  17:-1.75,  18:-1,  19:0,  20:0,  21:-1,  22:-1.75,  23:2.5,  24:-3,  25:-2.5,  26:-2,  27:-2,  28:-2,  29:-2,  30:-2.5,  31:-3,  32:-4,  33:-3,  34:-2.5,  35:-2.5,  36:-2.5,  37:-2.5,  38:-3,  39:-4, 40:-5,  41:-4,  42:-3,  43:-3,  44:-3,  45:-3,  46:-4,  47:-5,  48:-7,  49:-5.5,  50:-5,  51:-4,  52:-4,  53:-5,  54:-5.5,  55:-7,  56:-9,  57:-7,  58:-6,  59:-5.5,  60:-5.5,  61:-6,  62:-7,  63:-9}, king:{0:9,   1:7,   2:6,   3:5.5,   4:5.5,   5:6,   6:7,   7:9,  8:7,   9:5.5,  10:5,  11:4,  12:4,  13:5,  14:5.5,  15:7,  16:5,  17:4,  18:3,  19:3,  20:3,  21:3,  22:4,  23:5,  24:4,  25:3,  26:2.5,  27:2.5,  28:2.5,  29:2.5,  30:3,  31:4,  32:3,  33:2.5,  34:2,  35:2,  36:2,  37:2,  38:2.5,  39:3, 40:-2.5,  41:1.75,  42:1,  43:0,  44:0,  45:1,  46:1.75,  47:-2.5,  48:1.5,  49:0.75,  50:0.5,  51:0,  52:0,  53:0.5,  54:0.75,  55:1.5,  56:0,  57:-1.75,  58:-1.5,  59:0,  60:0,  61:0,  62:-1.5,  63:0}}

# Function to figure out the numeric value of a board
## Note it works recursively and due to return calls at the end of each if
## There is no need for an else anywhere
def evaluateBoard(board, depth):

  ## Since this is no longer always called as black, 
  ## the code first check the current turn
  if board.turn:

    ### if the player is white and it's checkmate,
    ### it's very good for black
    if board.is_checkmate():
      return -10000
    
    ### If depth is non-zero return the highest scoring follow up move's score
    if depth:  
      Legal = list(board.generate_legal_moves())
      alpha = -10000
      for m in Legal:
        board.push(m)        
        rating = evaluateBoard(board, depth-1)
        board.pop()
        if rating > alpha:
          alpha = rating        
      return alpha
    
    ### If depth is zero, evaluate as before
    score = 0
    for square,piece in board.piece_map().items():
      score += pieceValues[piece][square]
    return score
  
  ## if the player is black and it's checkmate,
  ## it's very good for white
  if board.is_checkmate():
    return 10000
  
  ## If depth is non-zero return the lowest scoring follow up move's score
  if depth:  
    Legal = list(board.generate_legal_moves())
    alpha = 10000
    for m in Legal:
      board.push(m)
      rating = evaluateBoard(board, depth-1)
      if rating < alpha:
        alpha = rating
      board.pop()
    return alpha
  
  ## If depth is zero, evaluate as before
  score = 0
  for square,piece in board.piece_map().items():
    score += pieceValues[piece][square]
  return score
  