from typing import Optional
import chess
from evaluation import alpha_beta, evaluate_move_on_board

ALPHA_INIT = -100000
BETA_INIT = 100000
DEFAULT_SEARCH_DEPTH = 3

class Engine:
    def __init__(self, depth: int = DEFAULT_SEARCH_DEPTH, board_fen: Optional[str] = None):
        self.board = chess.Board(board_fen) if board_fen else chess.Board()
        self.depth = depth
        self.captured_by_white = {}
        self.captured_by_black = {} 
        self._capture_stack = []
        
        # Board state stack for reliable game state tracking
        self._board_state_stack = []  
        # Initialize with starting position
        self._push_game_state()

    def set_depth(self, depth: int):
        self.depth = depth

    def resetboard(self):
        """Reset the board to the starting position and clear all tracking."""
        self.board = chess.Board()
        self.captured_by_white.clear()
        self.captured_by_black.clear()
        self._capture_stack.clear()
        self._board_state_stack.clear()
        # Initialize with starting position
        self._push_game_state()

    def get_current_board(self) -> chess.Board:
        """Return a copy of the current game state (not the engine's working board)."""
        if self._board_state_stack:
            return chess.Board(self._board_state_stack[-1].fen())
        return chess.Board()
        
    def _push_game_state(self):
        """Push current board state onto the game stack."""
        self._board_state_stack.append(chess.Board(self.board.fen()))
        
    def _pop_game_state(self) -> Optional[chess.Board]:
        """Pop the most recent game state from the stack."""
        if len(self._board_state_stack) > 1:  # Keep at least starting position
            self._board_state_stack.pop()
            # Reset working board to current game state
            if self._board_state_stack:
                self.board = chess.Board(self._board_state_stack[-1].fen())
                # Use capture stack for efficient undo instead of rebuilding
                self._undo_last_capture()
            return self.get_current_board()
        return None

    def _undo_last_capture(self):
        """Efficiently undo the last capture using the capture stack."""
        if self._capture_stack:
            capture_info = self._capture_stack.pop()
            if capture_info:
                captured_symbol_lower, capturer_is_white = capture_info
                if capturer_is_white:
                    # Restore the piece that was captured by white
                    cur = self.captured_by_white.get(captured_symbol_lower, 0)
                    if cur <= 1:
                        self.captured_by_white.pop(captured_symbol_lower, None)
                    else:
                        self.captured_by_white[captured_symbol_lower] = cur - 1
                else:
                    # Restore the piece that was captured by black
                    cur = self.captured_by_black.get(captured_symbol_lower, 0)
                    if cur <= 1:
                        self.captured_by_black.pop(captured_symbol_lower, None)
                    else:
                        self.captured_by_black[captured_symbol_lower] = cur - 1

    def _sync_capture_stack(self):
        """Ensure capture stack length matches the expected game state."""
        expected_length = len(self._board_state_stack) - 1  # -1 because starting position has no captures
        current_length = len(self._capture_stack)
        
        if current_length != expected_length:
            # Rebuild capture tracking to sync
            self._rebuild_capture_tracking()

    def can_undo(self) -> bool:
        """Check if there are moves available to undo."""
        return len(self._board_state_stack) > 1

    def make_move(self, move: chess.Move) -> bool:
        """Make a move and push new game state. Returns True if successful."""
        if move in self.board.legal_moves:
            self.push(move)
            self._push_game_state()  # Push new state to game stack
            # Ensure stacks stay synchronized
            self._sync_capture_stack()
            return True
        return False

    def undo_move(self) -> bool:
        """Undo the last move from both engine and game stack. Returns True if successful."""
        if self.can_undo():
            # Pop from game stack first (this syncs working board)
            self._pop_game_state()
            # Ensure stacks stay synchronized
            self._sync_capture_stack()
            return True
        return False

    def get_last_move(self) -> Optional[chess.Move]:
        """Get the last move made by comparing game states."""
        if len(self._board_state_stack) > 1:
            # Compare current state with previous state to find the last move
            previous_board = chess.Board(self._board_state_stack[-2].fen())
            current_board = chess.Board(self._board_state_stack[-1].fen())
            
            # Generate all possible moves from the previous position
            for move in previous_board.legal_moves:
                test_board = chess.Board(previous_board.fen())
                test_board.push(move)
                if test_board.fen() == current_board.fen():
                    return move
        return None

    def push(self, move: chess.Move):
        """Push a move onto the internal board. Caller should ensure move is legal."""
        # Determine if this move captures a piece and record it before mutating the board
        captured_symbol_lower = None
        capturer_is_white = self.board.turn == chess.WHITE

        if self.board.is_capture(move):
            # handle en-passant which captures a pawn on a different square
            if self.board.is_en_passant(move):
                # captured pawn sits on the file of to_square but on the from-rank
                if self.board.turn == chess.WHITE:
                    cap_sq = move.to_square - 8
                else:
                    cap_sq = move.to_square + 8
                cap_piece = self.board.piece_at(cap_sq)
            else:
                cap_piece = self.board.piece_at(move.to_square)

            if cap_piece:
                captured_symbol_lower = cap_piece.symbol().lower()
                # increment appropriate counter
                if capturer_is_white:
                    self.captured_by_white[captured_symbol_lower] = (
                        self.captured_by_white.get(captured_symbol_lower, 0) + 1
                    )
                else:
                    self.captured_by_black[captured_symbol_lower] = (
                        self.captured_by_black.get(captured_symbol_lower, 0) + 1
                    )

        # record into stack to allow undo
        self._capture_stack.append((captured_symbol_lower, capturer_is_white) if captured_symbol_lower else None)

        # Now actually push the move
        self.board.push(move)

    def pop(self) -> Optional[chess.Move]:
        if not self.board.move_stack:
            return None

        # Pop the board move first
        mv = self.board.pop()

        # Restore capture counts if the popped move had a capture
        # Use bounds checking to prevent "pop from empty list" errors
        if self._capture_stack:
            info = self._capture_stack.pop()
            if info:
                captured_symbol_lower, capturer_is_white = info
                if capturer_is_white:
                    # a piece previously recorded as captured by White is being restored
                    cur = self.captured_by_white.get(captured_symbol_lower, 0)
                    if cur <= 1:
                        self.captured_by_white.pop(captured_symbol_lower, None)
                    else:
                        self.captured_by_white[captured_symbol_lower] = cur - 1
                else:
                    cur = self.captured_by_black.get(captured_symbol_lower, 0)
                    if cur <= 1:
                        self.captured_by_black.pop(captured_symbol_lower, None)
                    else:
                        self.captured_by_black[captured_symbol_lower] = cur - 1

        return mv

    def get_captured_by_white(self) -> dict:
        """Return a shallow copy of pieces captured by White (black pieces taken).
        Keys are piece type letters in lowercase ('p','n','b','r','q','k')."""
        return dict(self.captured_by_white)

    def get_captured_by_black(self) -> dict:
        """Return a shallow copy of pieces captured by Black (white pieces taken).
        Keys are piece type letters in lowercase ('p','n','b','r','q','k')."""
        return dict(self.captured_by_black)

    def find_best_move(self, cancel_token=None) -> Optional[chess.Move]:
        """Blocking call that returns the best move for the current position."""
        try:
            best_move = None
            alpha = ALPHA_INIT

            # sort moves by shallow static eval to get reasonable ordering
            moves = sorted(self.board.generate_legal_moves(), key=lambda m: -evaluate_move_on_board(m, self.board))
            for move in moves:
                # Check for cancellation
                if cancel_token and cancel_token.is_set():
                    return None
                    
                self.board.push(move)
                try:
                    score = -alpha_beta(-BETA_INIT, -alpha, self.board, self.depth - 1, cancel_token)
                finally:
                    # Safely pop with error handling
                    try:
                        self.board.pop()
                    except IndexError:
                        # If board stack is empty, sync with game state
                        if self._board_state_stack:
                            self.board = chess.Board(self._board_state_stack[-1].fen())
                        break
                        
                if score > alpha:
                    alpha = score
                    best_move = move

            return best_move
        except Exception as e:
            # If there's a stack synchronization issue, try to recover
            if self._board_state_stack:
                self.board = chess.Board(self._board_state_stack[-1].fen())
                # Rebuild capture tracking if needed
                if "pop from empty list" in str(e):
                    self._rebuild_capture_tracking()
            raise e


if __name__ == '__main__':
    e = Engine()
    print('Engine ready, legal moves:', len(list(e.board.generate_legal_moves())))
