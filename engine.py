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

    def set_depth(self, depth: int):
        self.depth = depth

    def reset(self):
        self.board = chess.Board()

    def push(self, move: chess.Move):
        """Push a move onto the internal board. Caller should ensure move is legal."""
        self.board.push(move)

    def pop(self) -> Optional[chess.Move]:
        if self.board.move_stack:
            return self.board.pop()
        return None

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
