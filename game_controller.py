from enum import Enum
from typing import Optional, Callable, Dict, Any
import chess
import threading
from engine import Engine
from ui_config import UIConfig

class GameState(Enum):
    NOT_STARTED = "not_started"
    PLAYER_TURN = "player_turn"
    AI_THINKING = "ai_thinking"
    GAME_OVER   = "game_over"

class GameResult(Enum):
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    ONGOING    = "ongoing"
    DRAW       = "draw"

class GameController:
    def __init__(self, search_depth: int = UIConfig.game.DEFAULT_SEARCH_DEPTH):
        self.engine: Optional[Engine] = None
        self.player_color: chess.Color = chess.WHITE
        self.current_state: GameState = GameState.NOT_STARTED
        self._ai_cancel_token = threading.Event()
        
        self._observers: Dict[str, Callable] = {}
        
    def add_observer(self, event_name: str, callback: Callable):
        self._observers[event_name] = callback
        
    def _notify_observers(self, event_name: str, *args, **kwargs):
        if event_name in self._observers:
            try:
                self._observers[event_name](*args, **kwargs)
            except Exception as e:
                print(f"Observer error for {event_name}: {e}")
    
    def start_new_game(self, player_color: chess.Color) -> bool:
        try:
            self.player_color = player_color
            self.engine = Engine(UIConfig.game.DEFAULT_SEARCH_DEPTH)

            self.current_state = GameState.PLAYER_TURN
            self._notify_observers('game_started', player_color)
            if player_color == chess.BLACK:
                self._start_ai_move()
                
            return True
            
        except Exception as e:
            self._notify_observers('error', f"Failed to start game: {e}")
            return False
    
    def make_player_move(self, move: chess.Move) -> bool:
        if self.current_state != GameState.PLAYER_TURN:
            return False
            
        try:
            if self.engine and self.engine.make_move(move):
                self._notify_observers('move_made', move)
                
                if self._is_game_over():
                    self._handle_game_over()
                else:
                    self._start_ai_move()
                    
                return True
                
        except Exception as e:
            self._notify_observers('error', f"Invalid move: {e}")
            
        return False
    
    def undo_move(self) -> bool:
        try:
            # If AI is thinking, cancel and undo player move
            if self.current_state == GameState.AI_THINKING:
                self._cancel_ai_move()
            else:
                # Undo AI move if appropriate
                if (self.engine.get_current_board().turn == self.player_color):
                    self.engine.undo_move()
                
            # Undo player move
            self.engine.undo_move()
            self.current_state = GameState.PLAYER_TURN
            self._notify_observers('move_undone')
            
            return True
            
        except Exception as e:
            self._notify_observers('error', f"Undo failed: {e}")
            return False
    
    def end_game(self):
        self._cancel_ai_move()
        self.current_state = GameState.NOT_STARTED
        self.engine = None
        self._notify_observers('game_ended')
    
    def get_current_board(self) -> Optional[chess.Board]:
        return self.engine.get_current_board() if self.engine else None
    
    def get_last_move(self) -> Optional[chess.Move]:
        return self.engine.get_last_move() if self.engine else None
    
    def get_captured_pieces(self) -> tuple:
        return self.engine.get_captured_by_white(), self.engine.get_captured_by_black()
    
    def get_game_result(self) -> GameResult:            
        board = self.engine.get_current_board()
        if not board.is_game_over():
            return GameResult.ONGOING
            
        outcome = board.outcome()
        if outcome.winner is None:
            return GameResult.DRAW
        elif outcome.winner == chess.WHITE:
            return GameResult.WHITE_WINS
        else:
            return GameResult.BLACK_WINS
    
    def is_legal_move(self, from_square: int, to_square: int) -> Optional[chess.Move]:
        board = self.engine.get_current_board()
        for legal_move in board.legal_moves:
            if (legal_move.from_square == from_square and 
                legal_move.to_square == to_square):
                return legal_move
        return None
    
    # Private methods
    def _is_game_over(self) -> bool:
        return self.engine.get_current_board().is_game_over()
    
    def _handle_game_over(self):
        self.current_state = GameState.GAME_OVER
        self._notify_observers('game_over', self.get_game_result())
    
    def _start_ai_move(self):
        if self.current_state != GameState.PLAYER_TURN:
            return
            
        self.current_state = GameState.AI_THINKING
        self._notify_observers('ai_thinking_started')
        
        def compute_ai_move():
            try:
                move = self.engine.find_best_move(cancel_token=self._ai_cancel_token)
                if not self._ai_cancel_token.is_set():
                    self._notify_observers('ai_move_ready', move)

            except Exception as e:
                if not self._ai_cancel_token.is_set():
                    self._notify_observers('error', f"AI Error: {e}")
        
        threading.Thread(target=compute_ai_move, daemon=True).start()
    
    def apply_ai_move(self, move: Optional[chess.Move]):
        if self._ai_cancel_token.is_set() or not move:
            return
            
        try:
            board = self.engine.get_current_board()
            if move in board.legal_moves:
                self.engine.make_move(move)
                self._notify_observers('move_made', move)
                
                if self._is_game_over():
                    self._handle_game_over()
                else:
                    self.current_state = GameState.PLAYER_TURN
                        
        except Exception as e:
            self._notify_observers('error', f"AI move failed: {e}")
        finally:
            if self.current_state == GameState.AI_THINKING:
                self.current_state = GameState.PLAYER_TURN
    
    def _cancel_ai_move(self):
        self._ai_cancel_token.set()
        self._ai_cancel_token = threading.Event()
