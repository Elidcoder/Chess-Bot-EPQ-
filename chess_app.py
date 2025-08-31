"""
Main chess application that coordinates the engine, renderer, and UI flow.

This module provides the top-level application structure, handling the
start screen, game flow, and coordination between the engine and renderer.
"""

import tkinter as tk
from tkinter import ttk
import chess
import threading
from typing import Optional

from engine import get_default_engine, Engine
from board_renderer import BoardRenderer
from home_page import HomePage

# Application constants
APP_TITLE = "Chess Challenge"

# Window dimensions
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 500

# UI timing
INITIAL_DRAW_DELAY = 100
AI_START_DELAY = 200
AI_MOVE_DELAY = 100

# Search parameters
DEFAULT_SEARCH_DEPTH = 3

# Typography and layout
PIECE_FONT_NAME = 'Arial'
STATUS_FONT_SIZE = 12
CAPTURED_FONT_SIZE = 14
CAPTURED_LABEL_FONT_SIZE = 10
TITLE_FONT_SIZE = 20
SUBTITLE_FONT_SIZE = 14
MAIN_PADDING = 10
SIDE_PANEL_PADDING = 8
BUTTON_PADDING = 5
BORDER_WIDTH = 2

# Captured pieces display
CAPTURE_ORDER = ['k', 'q', 'r', 'b', 'n', 'p']
MAX_ERROR_DISPLAY_LENGTH = 30
PIECE_UNICODES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}


class ChessApp:
    """Main chess application coordinating engine, renderer, and UI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.engine: Optional[Engine] = None
        self.board_renderer: Optional[BoardRenderer] = None
        self.home_page: Optional[HomePage] = None
        
        # Thread cancellation
        self.ai_cancel_token = threading.Event()
        
        # Game state
        self.player_color = chess.WHITE
        self.current_board: Optional[chess.Board] = None
        self.selected_display_coords: Optional[tuple] = None
        self.ai_thinking = False
        
        # UI components (set when in game)
        self.main_frame: Optional[ttk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.status_label: Optional[ttk.Label] = None
        self.captured_white_label: Optional[ttk.Label] = None
        self.captured_black_label: Optional[ttk.Label] = None
        
        self._setup_main_window()
        self._show_start_screen()

    def run(self):
        """Start the application main loop."""
        # Set up cleanup handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.root.mainloop()
        
    def _on_window_close(self):
        """Handle window close event with proper cleanup."""
        # Cancel any running AI computation
        self._cancel_ai_computation()
        
        # Destroy the window
        self.root.destroy()

    def _setup_main_window(self):
        """Configure the main application window."""
        self.root.title(APP_TITLE)
        self.root.geometry(f'{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}')
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _show_start_screen(self):
        """Display the start screen for color selection."""
        # Clear any existing content
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create and show home page
        self.home_page = HomePage(self.root, APP_TITLE)
        self.home_page.set_callbacks(
            on_play_white=lambda: self._start_game(chess.WHITE),
            on_play_black=lambda: self._start_game(chess.BLACK),
            on_quit=self._quit_application
        )
        self.home_page.show()
        
    def _quit_application(self):
        """Quit the application with proper cleanup."""
        self._cancel_ai_computation()
        self.root.quit()
        
    def _cancel_ai_computation(self):
        """Cancel any running AI computation."""
        self.ai_cancel_token.set()
        # Reset for next game
        self.ai_cancel_token = threading.Event()

    def _start_game(self, player_color: chess.Color):
        """Start a new chess game with the specified player color."""
        self.player_color = player_color
        
        # Initialize engine and get starting board
        self.engine = get_default_engine(DEFAULT_SEARCH_DEPTH)
        self.engine.resetboard()
        self.current_board = self.engine.get_board_copy()
        
        # Clear start screen and create game UI
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self._create_game_interface()
        
        # Initialize board renderer
        is_white_player = (player_color == chess.WHITE)
        self.board_renderer = BoardRenderer(self.canvas, is_white_player)
        self.board_renderer.set_square_click_handler(self._on_square_clicked)
        self.board_renderer.set_resize_handler(self._on_resize)
        
        # Start the game
        self.selected_display_coords = None
        self.ai_thinking = False
        
        self.root.after(INITIAL_DRAW_DELAY, self._refresh_display)
        
        # Start AI if it should move first
        if self.current_board.turn != self.player_color:
            self.root.after(AI_START_DELAY, self._start_ai_move)

    def _create_game_interface(self):
        """Create the game UI components."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=MAIN_PADDING)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        # Status section
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, MAIN_PADDING))
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ttk.Label(status_frame, text="White to move", 
                                    font=(PIECE_FONT_NAME, STATUS_FONT_SIZE, 'bold'))
        self.status_label.grid(row=0, column=0)

        # Control buttons
        buttons_frame = ttk.Frame(status_frame)
        buttons_frame.grid(row=1, column=0, pady=(BUTTON_PADDING, 0))

        button_configs = [
            ("New Game", self._new_game),
            ("Undo Move", self._undo_move),
            ("End Game", self._end_game),
            ("Quit", self.root.destroy)
        ]
        
        for col, (text, command) in enumerate(button_configs):
            ttk.Button(buttons_frame, text=text, command=command).grid(
                row=0, column=col, padx=BUTTON_PADDING)

        # Game board canvas
        canvas_frame = ttk.Frame(self.main_frame, relief='solid', borderwidth=BORDER_WIDTH)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Captured pieces panel
        side_frame = ttk.Frame(self.main_frame, padding=(SIDE_PANEL_PADDING, 0))
        side_frame.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E), padx=(MAIN_PADDING, 0))

        ttk.Label(side_frame, text="Captured", 
                 font=(PIECE_FONT_NAME, STATUS_FONT_SIZE, 'bold')).grid(row=0, column=0, pady=(0, 6))
        
        ttk.Label(side_frame, text="White's captures:", 
                 font=(PIECE_FONT_NAME, CAPTURED_LABEL_FONT_SIZE)).grid(row=1, column=0, sticky='w')
        self.captured_white_label = ttk.Label(side_frame, text="", 
                                            font=(PIECE_FONT_NAME, CAPTURED_FONT_SIZE))
        self.captured_white_label.grid(row=2, column=0, sticky='w', pady=(2, 8))

        ttk.Label(side_frame, text="Black's captures:", 
                 font=(PIECE_FONT_NAME, CAPTURED_LABEL_FONT_SIZE)).grid(row=3, column=0, sticky='w')
        self.captured_black_label = ttk.Label(side_frame, text="", 
                                            font=(PIECE_FONT_NAME, CAPTURED_FONT_SIZE))
        self.captured_black_label.grid(row=4, column=0, sticky='w', pady=(2, 8))

    def _refresh_display(self):
        """Refresh the board display and status."""
        if not self.board_renderer or not self.current_board:
            return
            
        # Get last move from engine
        last_move = None
        if self.engine and self.engine.board.move_stack:
            last_move = self.engine.board.move_stack[-1]
            
        self.board_renderer.render_board(
            self.current_board, 
            self.selected_display_coords, 
            last_move
        )
        
        self._update_status()
        self._update_captured_panel()

    def _on_square_clicked(self, display_file: int, display_rank: int):
        """Handle square clicks from the board renderer."""
        if self.ai_thinking:
            return
            
        # Convert display coordinates to chess coordinates
        chess_file, chess_rank = self.board_renderer.get_chess_coordinates_from_display(
            display_file, display_rank)
        chess_square = chess.square(chess_file, chess_rank)
        
        if self.selected_display_coords is None:
            # Try to select a piece
            piece = self.current_board.piece_at(chess_square)
            if piece and piece.color == self.player_color:
                self.selected_display_coords = (display_file, display_rank)
                self._refresh_display()
        else:
            # Try to make a move
            selected_chess_file, selected_chess_rank = self.board_renderer.get_chess_coordinates_from_display(
                self.selected_display_coords[0], self.selected_display_coords[1])
            from_square = chess.square(selected_chess_file, selected_chess_rank)
            
            # Find matching legal move
            move = self._find_legal_move(from_square, chess_square)
            
            if move:
                self._execute_player_move(move)
            else:
                # Invalid move - try selecting new piece or deselect
                piece = self.current_board.piece_at(chess_square)
                if piece and piece.color == self.player_color:
                    self.selected_display_coords = (display_file, display_rank)
                else:
                    self.selected_display_coords = None
                self._refresh_display()

    def _on_resize(self):
        """Handle board resize events from the renderer."""
        # Update status and captured panel to ensure they stay consistent
        if self.current_board:
            self._update_status()
            self._update_captured_panel()

    def _find_legal_move(self, from_square: int, to_square: int) -> Optional[chess.Move]:
        """Find a legal move matching the from and to squares."""
        for legal_move in self.current_board.legal_moves:
            if (legal_move.from_square == from_square and 
                legal_move.to_square == to_square):
                return legal_move
        return None

    def _execute_player_move(self, move: chess.Move):
        """Execute a player move and trigger AI response."""
        try:
            self.current_board = self.engine.makemove(move)
            self.selected_display_coords = None
            
            self._refresh_display()
            
            # Handle game continuation
            if self.current_board.is_game_over():
                self._update_status()
            else:
                self.status_label.config(text="AI thinking...")
                self.root.after(AI_MOVE_DELAY, self._start_ai_move)
                
        except ValueError as e:
            # Invalid move
            print(f"Invalid move: {e}")
            self.selected_display_coords = None
            self._refresh_display()

    def _start_ai_move(self):
        """Start AI move calculation in a background thread."""
        if self.current_board.is_game_over() or self.ai_thinking:
            return

        self.ai_thinking = True
        self.status_label.config(text="AI thinking...", foreground='black')

        def compute_move():
            """Background thread function to compute AI move."""
            try:
                best_move = self.engine.get_best_move(cancel_token=self.ai_cancel_token)
                if not self.ai_cancel_token.is_set():
                    self.root.after(0, lambda move=best_move: self._apply_ai_move(move))
            except Exception as error:
                if not self.ai_cancel_token.is_set():
                    self.root.after(0, lambda err=error: self._handle_ai_error(err))

        threading.Thread(target=compute_move, daemon=True).start()

    def _apply_ai_move(self, move: Optional[chess.Move]):
        """Apply AI move on the main thread."""
        try:
            if move and move in self.current_board.legal_moves:
                self.current_board = self.engine.makemove(move)

            self.ai_thinking = False
            self._refresh_display()
        except Exception as error:
            self._handle_ai_error(error)

    def _handle_ai_error(self, error: Exception):
        """Handle AI computation errors."""
        self.ai_thinking = False
        error_text = str(error)[:MAX_ERROR_DISPLAY_LENGTH]
        self.status_label.config(text=f"AI Error: {error_text}...", foreground='red')
        print(f"AI Error: {error}")

    def _update_status(self):
        """Update status display based on current game state."""
        if self.current_board.is_game_over():
            outcome = self.current_board.outcome()
            
            if outcome.winner is None:
                self.status_label.config(text="Game Over - Draw!", foreground='blue')
            elif outcome.winner == chess.WHITE:
                self.status_label.config(text="Game Over - White Wins!", foreground='green')
            else:
                self.status_label.config(text="Game Over - Black Wins!", foreground='red')
        else:
            if self.current_board.turn == chess.WHITE:
                self.status_label.config(text="White to move", foreground='black')
            else:
                self.status_label.config(text="Black to move", foreground='black')

    def _update_captured_panel(self):
        """Update captured pieces display using engine's capture tracking."""
        if not self.engine:
            return
            
        try:
            white_captures = self.engine.get_captured_by_white()
            black_captures = self.engine.get_captured_by_black()
        except Exception:
            white_captures = {}
            black_captures = {}

        def format_captures(capture_dict: dict) -> str:
            """Create a human-readable summary of captured pieces."""
            parts = []
            for piece_type in CAPTURE_ORDER:
                count = capture_dict.get(piece_type, 0)
                if count > 0:
                    parts.append(f"{PIECE_UNICODES[piece_type]} * {count}")
            return ', '.join(parts) if parts else 'No captures'

        self.captured_white_label.config(text=format_captures(white_captures))
        self.captured_black_label.config(text=format_captures(black_captures))

    def _new_game(self):
        """Reset to a new game and start AI if needed."""
        if self.ai_thinking:
            return
            
        self.ai_thinking = False
        self.engine.resetboard()
        self.current_board = self.engine.get_board_copy()
        self.selected_display_coords = None
        
        self._refresh_display()
        
        # Start AI if it should move first
        if self.current_board.turn != self.player_color:
            self.root.after(AI_MOVE_DELAY, self._start_ai_move)

    def _undo_move(self):
        """Undo the last two moves (player and AI)."""
        if self.ai_thinking or not self.engine:
            return

        # Undo up to two moves to return to player's turn
        moves_to_undo = min(2, len(self.engine.board.move_stack))
        for _ in range(moves_to_undo):
            result = self.engine.undo()
            if result:
                self.current_board = result

        self.selected_display_coords = None
        self._refresh_display()

    def _end_game(self):
        """End current game and return to start screen."""
        if self.ai_thinking:
            return
            
        self._show_start_screen()


def main():
    """Main application entry point."""
    app = ChessApp()
    app.run()


if __name__ == '__main__':
    main()
