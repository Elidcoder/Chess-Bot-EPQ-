from typing import Optional
import chess
from evaluation import alpha_beta, evaluate_move_on_board

ALPHA_INIT = -100000
BETA_INIT = 100000
DEFAULT_SEARCH_DEPTH = 3


class Engine:
    def __init__(self, board_fen: Optional[str] = None, depth: int = DEFAULT_SEARCH_DEPTH):
        self.board = chess.Board(board_fen) if board_fen else chess.Board()
        self.depth = depth
        self.captured_by_white = {}
        self.captured_by_black = {} 
        self._capture_stack = []

    def set_depth(self, depth: int):
        self.depth = depth

    def reset(self):
        self.board = chess.Board()
        self.captured_by_white.clear()
        self.captured_by_black.clear()
        self._capture_stack.clear()

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

    def legal_moves(self):
        return list(self.board.generate_legal_moves())

    def find_best_move(self) -> Optional[str]:
        """Blocking call that returns a UCI string for the best move."""
        best_move = None
        alpha = ALPHA_INIT

        # sort moves by shallow static eval to get reasonable ordering
        moves = sorted(self.board.generate_legal_moves(), key=lambda m: -evaluate_move_on_board(m, self.board))
        for move in moves:
            self.board.push(move)
            try:
                score = -alpha_beta(-BETA_INIT, -alpha, self.board, self.depth - 1)
            finally:
                self.board.pop()
            if score > alpha:
                alpha = score
                best_move = move

        return best_move.uci() if best_move else None


# Provide a small module-level convenience instance for simple use
_default_engine: Optional[Engine] = None


def get_default_engine(depth: int = DEFAULT_SEARCH_DEPTH) -> Engine:
    global _default_engine
    if _default_engine is None:
        _default_engine = Engine(depth=depth)
    else:
        _default_engine.set_depth(depth)
    return _default_engine


if __name__ == '__main__':
    e = get_default_engine()
    print('Engine ready, legal moves:', len(e.legal_moves()))
