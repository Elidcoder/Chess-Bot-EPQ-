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

    def get_current_board(self) -> chess.Board:
        return chess.Board(self._board_state_stack[-1].fen())
        
    def _push_game_state(self):
        self._board_state_stack.append(chess.Board(self.board.fen()))
        
    #TODO(BUG WITH STARTING AS BLACK -> STARTING MOVE CAN GET UNDONE)
    def undo_move(self) -> bool:
        if len(self._board_state_stack) <= 1:
            return False

        self._board_state_stack.pop()
        # Update to match old state
        self.board = chess.Board(self._board_state_stack[-1].fen())
        self._undo_last_capture()
        self._sync_capture_stack()
        return True

    def _undo_last_capture(self):
        capture_info = self._capture_stack.pop()
        if not capture_info:
            return

        captured_symbol_lower, capturer_is_white = capture_info

        # Restore the piece that was captured by white
        if capturer_is_white:
            cur = self.captured_by_white.get(captured_symbol_lower, 0)
            if cur <= 1:
                self.captured_by_white.pop(captured_symbol_lower, None)
            else:
                self.captured_by_white[captured_symbol_lower] = cur - 1
            return

        # Restore the piece that was captured by black
        cur = self.captured_by_black.get(captured_symbol_lower, 0)
        if cur <= 1:
            self.captured_by_black.pop(captured_symbol_lower, None)
        else:
            self.captured_by_black[captured_symbol_lower] = cur - 1

    def _sync_capture_stack(self):
        expected_length = len(self._board_state_stack) - 1
        current_length = len(self._capture_stack)
        
        if current_length != expected_length:
            self._rebuild_capture_tracking()

    def make_move(self, move: chess.Move) -> bool:
        if move not in self.board.legal_moves:
            return False

        was_capture = self.board.is_capture(move)
        capturer_is_white = self.board.turn == chess.WHITE
        if self.board.is_en_passant(move):
            if capturer_is_white:
                cap_sq = move.to_square - 8
            else:
                cap_sq = move.to_square + 8
            cap_piece = self.board.piece_at(cap_sq)
        else:
            cap_piece = self.board.piece_at(move.to_square)

        self.board.push(move)
        self._push_game_state()

        if not was_capture:
            self._capture_stack.append(None)
            return True

        captured_symbol_lower = cap_piece.symbol().lower()
        if capturer_is_white:
            self.captured_by_white[captured_symbol_lower] = self.captured_by_white.get(captured_symbol_lower, 0) + 1
        else:
            self.captured_by_black[captured_symbol_lower] = self.captured_by_black.get(captured_symbol_lower, 0) + 1

        self._capture_stack.append((captured_symbol_lower, capturer_is_white))
        return True

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

    def pop(self) -> Optional[chess.Move]:
        mv = self.board.pop()
        info = self._capture_stack.pop()
        if not info:
            return mv

        # Restore captured piece
        captured_symbol_lower, capturer_is_white = info
        if capturer_is_white:
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
        return dict(self.captured_by_white)

    def get_captured_by_black(self) -> dict:
        return dict(self.captured_by_black)

    def find_best_move(self, cancel_token=None) -> Optional[chess.Move]:
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
