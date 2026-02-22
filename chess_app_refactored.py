"""
Refactored chess application using GameController and centralized UI configuration.

This module provides a cleaner separation of concerns with the game logic
handled by GameController and UI concerns handled by the application class.
"""

import tkinter as tk
from tkinter import ttk
import chess
from typing import Optional

from game_controller import GameController, GameState, GameResult
from board_renderer import BoardRenderer
from constants import PIECE_UNICODES, CAPTURE_ORDER
from home_page import HomePage
from ui_config import UIConfig

class ChessApp:
    """Refactored chess application with improved architecture."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.game_controller = GameController()
        self.board_renderer: Optional[BoardRenderer] = None
        self.home_page: Optional[HomePage] = None
        
        # Game state
        self.selected_display_coords: Optional[tuple] = None
        
        # UI components (set when in game)
        self.main_frame: Optional[ttk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.status_label: Optional[ttk.Label] = None
        self.captured_white_label: Optional[ttk.Label] = None
        self.captured_black_label: Optional[ttk.Label] = None
        
        self._setup_main_window()
        self._setup_game_controller_observers()
        self._show_start_screen()

    def run(self):
        """Start the application main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.root.mainloop()
        
    def _on_window_close(self):
        """Handle window close event with proper cleanup."""
        self.game_controller.end_game()
        self.root.destroy()

    def _setup_main_window(self):
        """Configure the main application window."""
        self.root.title(UIConfig.game.APP_TITLE)
        self.root.geometry(f'{UIConfig.window.DEFAULT_WIDTH}x{UIConfig.window.DEFAULT_HEIGHT}')
        self.root.minsize(UIConfig.window.MIN_WIDTH, UIConfig.window.MIN_HEIGHT)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _setup_game_controller_observers(self):
        """Set up observer callbacks for game events."""
        self.game_controller.add_observer('game_started', self._on_game_started)
        self.game_controller.add_observer('move_made', self._on_move_made)
        self.game_controller.add_observer('move_undone', self._on_move_undone)
        self.game_controller.add_observer('ai_thinking_started', self._on_ai_thinking_started)
        self.game_controller.add_observer('ai_move_ready', self._on_ai_move_ready)
        self.game_controller.add_observer('game_over', self._on_game_over)
        self.game_controller.add_observer('game_ended', self._on_game_ended)
        self.game_controller.add_observer('error', self._on_error)

    def _show_start_screen(self):
        """Display the start screen for color selection."""
        self._clear_window()
        
        self.home_page = HomePage(self.root, UIConfig.game.APP_TITLE)
        self.home_page.set_callbacks(
            on_play_white=lambda: self._start_game(chess.WHITE),
            on_play_black=lambda: self._start_game(chess.BLACK)
        )
        self.home_page.show()

    def _clear_window(self):
        """Clear all widgets from the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
    def _start_game(self, player_color: chess.Color):
        """Start a new chess game with the specified player color."""
        if self.game_controller.start_new_game(player_color):
            self._clear_window()
            self._create_game_interface(player_color)
    
    def _create_game_interface(self, player_color: chess.Color):
        """Create the game UI components."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=UIConfig.layout.MAIN_PADDING)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        # Create UI sections
        self._create_status_section()
        self._create_board_section(player_color)
        self._create_captured_pieces_panel()
        
        # Initialize display
        self.root.after(UIConfig.timing.INITIAL_DRAW_DELAY, self._refresh_display)

    def _create_status_section(self):
        """Create the status and control buttons section."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, UIConfig.layout.MAIN_PADDING))
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            status_frame, 
            text="White to move", 
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.STATUS_SIZE, 'bold')
        )
        self.status_label.grid(row=0, column=0)

        # Control buttons
        buttons_frame = ttk.Frame(status_frame)
        buttons_frame.grid(row=1, column=0, pady=(UIConfig.layout.BUTTON_PADDING, 0))

        button_configs = [
            ("Undo Move", self._undo_move),
            ("End Game", self._end_game)
        ]
        
        for col, (text, command) in enumerate(button_configs):
            ttk.Button(buttons_frame, text=text, command=command).grid(
                row=0, column=col, padx=UIConfig.layout.BUTTON_PADDING)

    def _create_board_section(self, player_color: chess.Color):
        """Create the chess board canvas."""
        canvas_frame = ttk.Frame(
            self.main_frame, 
            relief='solid', 
            borderwidth=UIConfig.layout.BORDER_WIDTH
        )
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initialize board renderer
        is_white_player = (player_color == chess.WHITE)
        self.board_renderer = BoardRenderer(self.canvas, is_white_player)
        self.board_renderer.set_square_click_handler(self._on_square_clicked)
        self.board_renderer.set_resize_handler(self._on_resize)

    def _create_captured_pieces_panel(self):
        """Create the captured pieces display panel."""
        side_frame = ttk.Frame(
            self.main_frame, 
            padding=(UIConfig.layout.SIDE_PANEL_PADDING, 0)
        )
        side_frame.grid(
            row=1, 
            column=1, 
            sticky=(tk.N, tk.S, tk.E), 
            padx=(UIConfig.layout.MAIN_PADDING, 0)
        )

        ttk.Label(
            side_frame, 
            text="Captured", 
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.STATUS_SIZE, 'bold')
        ).grid(row=0, column=0, pady=(0, 6))
        
        ttk.Label(
            side_frame, 
            text="White's captures:", 
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.CAPTURED_LABEL_SIZE)
        ).grid(row=1, column=0, sticky='w')
        
        self.captured_white_label = ttk.Label(
            side_frame, 
            text="", 
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.CAPTURED_SIZE)
        )
        self.captured_white_label.grid(row=2, column=0, sticky='w', pady=(2, 8))

        ttk.Label(
            side_frame, 
            text="Black's captures:", 
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.CAPTURED_LABEL_SIZE)
        ).grid(row=3, column=0, sticky='w')
        
        self.captured_black_label = ttk.Label(
            side_frame, 
            text="", 
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.CAPTURED_SIZE)
        )
        self.captured_black_label.grid(row=4, column=0, sticky='w', pady=(2, 8))

    # Game Controller Event Handlers
    
    def _on_game_started(self, player_color: chess.Color):
        """Handle game start event."""
        self._refresh_display()
    
    def _on_move_made(self, move: chess.Move):
        """Handle move made event."""
        self.selected_display_coords = None
        self._refresh_display()
    
    def _on_move_undone(self):
        """Handle move undo event."""
        self.selected_display_coords = None
        self._refresh_display()
    
    def _on_ai_thinking_started(self):
        """Handle AI thinking start event."""
        if self.status_label:
            self.status_label.config(text="AI thinking...", foreground='black')
    
    def _on_ai_move_ready(self, move: Optional[chess.Move]):
        """Handle AI move ready event."""
        # Apply move on main thread
        self.root.after(0, lambda: self.game_controller.apply_ai_move(move))
    
    def _on_game_over(self, result: GameResult):
        """Handle game over event."""
        self._update_game_over_status(result)
    
    def _on_game_ended(self):
        """Handle game end event."""
        self._show_start_screen()
    
    def _on_error(self, error_message: str):
        """Handle error event."""
        if self.status_label:
            display_text = error_message[:UIConfig.game.MAX_ERROR_DISPLAY_LENGTH]
            if len(error_message) > UIConfig.game.MAX_ERROR_DISPLAY_LENGTH:
                display_text += "..."
            self.status_label.config(text=f"Error: {display_text}", foreground='red')
        print(f"Game Error: {error_message}")

    # UI Event Handlers
    
    def _on_square_clicked(self, display_file: int, display_rank: int):
        """Handle square clicks from the board renderer."""
        if self.game_controller.current_state != GameState.PLAYER_TURN:
            return
            
        current_board = self.game_controller.get_current_board()
        if not current_board:
            return
        
        # Convert display coordinates to chess coordinates
        chess_file, chess_rank = self.board_renderer.get_chess_coordinates_from_display(
            display_file, display_rank)
        chess_square = chess.square(chess_file, chess_rank)
        
        if self.selected_display_coords is None:
            # Try to select a piece
            self._try_select_piece(current_board, chess_square, display_file, display_rank)
        else:
            # Try to make a move
            self._try_make_move(current_board, chess_square, display_file, display_rank)
    
    def _try_select_piece(self, board: chess.Board, chess_square: int, display_file: int, display_rank: int):
        """Try to select a piece at the given square."""
        piece = board.piece_at(chess_square)
        if piece and piece.color == self.game_controller.player_color:
            self.selected_display_coords = (display_file, display_rank)
            self._refresh_display()
    
    def _try_make_move(self, board: chess.Board, chess_square: int, display_file: int, display_rank: int):
        """Try to make a move to the given square."""
        # Get the selected square in chess coordinates
        selected_chess_file, selected_chess_rank = self.board_renderer.get_chess_coordinates_from_display(
            self.selected_display_coords[0], self.selected_display_coords[1])
        from_square = chess.square(selected_chess_file, selected_chess_rank)
        
        # Check if this is a legal move
        move = self.game_controller.is_legal_move(from_square, chess_square)
        
        if move:
            # Make the move
            self.game_controller.make_player_move(move)
        else:
            # Invalid move - try selecting new piece or deselect
            piece = board.piece_at(chess_square)
            if piece and piece.color == self.game_controller.player_color:
                self.selected_display_coords = (display_file, display_rank)
            else:
                self.selected_display_coords = None
            self._refresh_display()

    def _on_resize(self):
        """Handle board resize events from the renderer."""
        self._update_status()
        self._update_captured_panel()

    # UI Update Methods
    
    def _refresh_display(self):
        """Refresh the board display and status."""
        if not self.board_renderer:
            return
            
        current_board = self.game_controller.get_current_board()
        last_move = self.game_controller.get_last_move()
        
        if current_board:
            self.board_renderer.render_board(
                current_board, 
                self.selected_display_coords, 
                last_move
            )
        
        self._update_status()
        self._update_captured_panel()

    def _update_status(self):
        """Update status display based on current game state."""
        if not self.status_label:
            return
            
        current_board = self.game_controller.get_current_board()
        if not current_board:
            return
            
        game_result = self.game_controller.get_game_result()
        
        if game_result != GameResult.ONGOING:
            self._update_game_over_status(game_result)
        else:
            # Game is ongoing
            if self.game_controller.current_state == GameState.AI_THINKING:
                self.status_label.config(text="AI thinking...", foreground='black')
            else:
                turn_text = "White to move" if current_board.turn == chess.WHITE else "Black to move"
                self.status_label.config(text=turn_text, foreground='black')

    def _update_game_over_status(self, result: GameResult):
        """Update status for game over conditions."""
        if not self.status_label:
            return
            
        status_texts = {
            GameResult.DRAW: ("Game Over - Draw!", 'blue'),
            GameResult.WHITE_WINS: ("Game Over - White Wins!", 'green'),
            GameResult.BLACK_WINS: ("Game Over - Black Wins!", 'red'),
        }
        
        text, color = status_texts.get(result, ("Game Over!", 'black'))
        self.status_label.config(text=text, foreground=color)

    def _update_captured_panel(self):
        """Update captured pieces display."""
        if not (self.captured_white_label and self.captured_black_label):
            return
            
        white_captures, black_captures = self.game_controller.get_captured_pieces()
        
        self.captured_white_label.config(text=self._format_captures(white_captures))
        self.captured_black_label.config(text=self._format_captures(black_captures))

    def _format_captures(self, capture_dict: dict) -> str:
        """Create a human-readable summary of captured pieces."""
        if not capture_dict:
            return 'No captures'
            
        parts = []
        for piece_type in CAPTURE_ORDER:
            count = capture_dict.get(piece_type, 0)
            if count > 0:
                parts.append(f"{PIECE_UNICODES[piece_type]} × {count}")
        
        return ', '.join(parts) if parts else 'No captures'

    # Action Methods
    
    def _undo_move(self):
        """Request undo from game controller."""
        self.game_controller.undo_move()

    def _end_game(self):
        """Request game end from game controller."""
        self.game_controller.end_game()


def main():
    """Main application entry point."""
    app = ChessApp()
    app.run()


if __name__ == '__main__':
    main()
