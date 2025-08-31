import tkinter as tk
from tkinter import ttk
import chess
from engine import get_default_engine, Engine
from typing import Optional, Tuple
import threading

# Application constants
APP_TITLE = "Chess Challenge"

# Window dimensions
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 500

# Board layout
BOARD_DIM = 8
DEFAULT_SQUARE_SIZE = 60
MIN_SQUARE_SIZE = 30
PIECE_FONT_SCALE = 0.6
COORD_FONT_SCALE = 0.2
MIN_PIECE_FONT_SIZE = 16
MIN_COORD_FONT_SIZE = 8

# UI timing
INITIAL_DRAW_DELAY = 100
AI_START_DELAY = 200
AI_MOVE_DELAY = 100

# Search parameters
DEFAULT_SEARCH_DEPTH = 3
ALPHA_INIT = -100000
BETA_INIT = 100000

# Color scheme
LIGHT_SQUARE = '#F0D9B5'
DARK_SQUARE = '#B58863'
HIGHLIGHT_COLOR = '#FFFF99'
SELECTED_COLOR = '#90EE90'
LAST_MOVE_COLOR = '#FFE4B5'
WHITE_PIECE_COLOR = '#FFFFFF'
BLACK_PIECE_COLOR = '#000000'
BOARD_OUTLINE_COLOR = '#8B4513'
COORD_TEXT_COLOR = '#654321'

# Typography
PIECE_FONT_NAME = 'Arial'
STATUS_FONT_SIZE = 12
CAPTURED_FONT_SIZE = 14
CAPTURED_LABEL_FONT_SIZE = 10
TITLE_FONT_SIZE = 20
SUBTITLE_FONT_SIZE = 14

# Layout spacing
MAIN_PADDING = 10
SIDE_PANEL_PADDING = 8
BUTTON_PADDING = 5
COORD_OFFSET = 5
COORD_CORNER_OFFSET = 10
HIGHLIGHT_RADIUS_SCALE = 8
BORDER_WIDTH = 2

# Captured pieces display
CAPTURE_ORDER = ['k', 'q', 'r', 'b', 'n', 'p']
MAX_ERROR_DISPLAY_LENGTH = 30
PIECE_UNICODES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}

class ChessGUI:
    """Main chess GUI application with player vs AI gameplay."""
    
    def __init__(self, root, on_end=None, player_color=chess.WHITE):
        self.root = root
        self.player_color = player_color
        self.on_end = on_end
        
        # Game state
        self._initialize_game_state()
        
        # UI setup
        self._setup_window()
        self._create_ui_components()
        self._bind_events()
        
        # Start game
        self._start_initial_game()

    def _initialize_game_state(self):
        """Initialize core game state variables."""
        self.engine = get_default_engine(DEFAULT_SEARCH_DEPTH)
        self.display_board = chess.Board(self.engine.board.fen())
        self.selected = None
        self.last_move = None
        self.square_size = DEFAULT_SQUARE_SIZE
        self.ai_thinking = False

    def _setup_window(self):
        """Configure the main application window."""
        self.root.title(APP_TITLE)
        self.root.geometry(f'{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}')
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _create_ui_components(self):
        """Create and layout all UI components."""
        self._create_main_frame()
        self._create_status_section()
        self._create_game_board()
        self._create_captured_pieces_panel()

    def _create_main_frame(self):
        """Create the main container frame."""
        self.main_frame = ttk.Frame(self.root, padding=MAIN_PADDING)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

    def _create_status_section(self):
        """Create status display and control buttons."""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, MAIN_PADDING))
        status_frame.grid_columnconfigure(0, weight=1)

        self.status = ttk.Label(status_frame, text="White to move", 
                               font=(PIECE_FONT_NAME, STATUS_FONT_SIZE, 'bold'))
        self.status.grid(row=0, column=0)

        self._create_control_buttons(status_frame)

    def _create_control_buttons(self, parent):
        """Create game control buttons."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=1, column=0, pady=(BUTTON_PADDING, 0))

        button_configs = [
            ("New Game", self.new_game),
            ("Undo Move", self.undo_move),
            ("Quit", self.root.destroy)
        ]
        
        for col, (text, command) in enumerate(button_configs):
            ttk.Button(buttons_frame, text=text, command=command).grid(
                row=0, column=col, padx=BUTTON_PADDING)

    def _create_game_board(self):
        """Create the chess board canvas."""
        canvas_frame = ttk.Frame(self.main_frame, relief='solid', borderwidth=BORDER_WIDTH)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _create_captured_pieces_panel(self):
        """Create the captured pieces display panel."""
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

    def _bind_events(self):
        """Bind event handlers."""
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Configure>', self.on_resize)

    def _start_initial_game(self):
        """Initialize the game display and AI if needed."""
        self.root.after(INITIAL_DRAW_DELAY, self.draw_board)
        self.update_status()
        if self.engine.board.turn != self.player_color:
            self.root.after(AI_START_DELAY, self.ai_move)

    def _calculate_board_metrics(self) -> Tuple[int, int, int]:
        """Calculate board dimensions and positioning."""
        board_size = self.square_size * BOARD_DIM
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        offset_x = max(0, (canvas_w - board_size) // 2)
        offset_y = max(0, (canvas_h - board_size) // 2)
        
        return board_size, offset_x, offset_y

    def _get_clicked_square(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Convert canvas coordinates to display square indices."""
        board_size, offset_x, offset_y = self._calculate_board_metrics()
        
        # Adjust for board offset
        click_x = x - offset_x
        click_y = y - offset_y
        
        # Check if click is within board bounds
        if not (0 <= click_x < board_size and 0 <= click_y < board_size):
            return None
            
        # Convert to display square indices
        display_file = click_x // self.square_size
        display_rank = click_y // self.square_size
        
        if not (0 <= display_file < BOARD_DIM and 0 <= display_rank < BOARD_DIM):
            return None
            
        return int(display_file), int(display_rank)

    def _calculate_font_sizes(self) -> Tuple[int, int]:
        """Calculate appropriate font sizes based on square size."""
        piece_font_size = max(MIN_PIECE_FONT_SIZE, int(self.square_size * PIECE_FONT_SCALE))
        coord_font_size = max(MIN_COORD_FONT_SIZE, int(self.square_size * COORD_FONT_SCALE))
        return piece_font_size, coord_font_size

    def _get_square_color(self, display_file: int, display_rank: int, square: int) -> str:
        """Determine the display color for a board square."""
        # Check for last move highlight
        if (self.last_move and 
            square in (self.last_move.from_square, self.last_move.to_square)):
            return LAST_MOVE_COLOR
            
        # Check for selection highlight (selected coordinates are in display space)
        if self.selected and self.selected == (display_file, display_rank):
            return SELECTED_COLOR
            
        # Standard checkerboard pattern based on chess coordinates
        chess_file = chess.square_file(square)
        chess_rank = chess.square_rank(square)
        return DARK_SQUARE if (chess_rank + chess_file) % 2 else LIGHT_SQUARE

    def _get_display_coordinates(self, file_idx: int, rank_idx: int) -> Tuple[int, int]:
        """Convert chess board coordinates to display coordinates based on player color.
        
        For White player: a1 at bottom-left (standard orientation)
        For Black player: a8 at bottom-left (flipped orientation)
        """
        if self.player_color == chess.WHITE:
            # White oreantation
            return file_idx, BOARD_DIM - 1 - rank_idx
        else:
            # Black orientation
            return BOARD_DIM - 1 - file_idx, rank_idx

    def _get_chess_coordinates_from_display(self, display_file: int, display_rank: int) -> Tuple[int, int]:
        """Convert display coordinates back to chess board coordinates."""
        if self.player_color == chess.WHITE:
            return display_file, BOARD_DIM - 1 - display_rank
        else:
            return BOARD_DIM - 1 - display_file, display_rank

    def _draw_square_and_coordinates(self, file_idx: int, rank_idx: int, 
                                   offset_x: int, offset_y: int, coord_font):
        """Draw a single board square with coordinates."""
        # Calculate display positions
        display_file, display_rank = self._get_display_coordinates(file_idx, rank_idx)
        
        x0 = offset_x + display_file * self.square_size
        y0 = offset_y + display_rank * self.square_size
        x1 = x0 + self.square_size
        y1 = y0 + self.square_size
        
        square = chess.square(file_idx, rank_idx)
        color = self._get_square_color(display_file, display_rank, square)
        
        # Draw square
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, 
                                   outline=BOARD_OUTLINE_COLOR, width=1)
        
        # Draw rank numbers (left edge) - show chess rank (1-8)
        if display_file == 0:
            chess_rank = rank_idx + 1 if self.player_color == chess.WHITE else (8 - rank_idx)
            self.canvas.create_text(x0 + COORD_OFFSET, y0 + COORD_OFFSET, 
                                  text=str(chess_rank),
                                  font=coord_font, fill=COORD_TEXT_COLOR, anchor='nw')
        
        # Draw file letters (bottom edge) - show chess file (a-h)
        if display_rank == BOARD_DIM - 1:
            chess_file = file_idx if self.player_color == chess.WHITE else (7 - file_idx)
            self.canvas.create_text(x1 - COORD_CORNER_OFFSET, y1 - COORD_OFFSET,
                                  text=chr(ord('a') + chess_file),
                                  font=coord_font, fill=COORD_TEXT_COLOR, anchor='se')

    def _draw_piece(self, square: int, file_idx: int, rank_idx: int,
                   offset_x: int, offset_y: int, piece_font_size: int):
        """Draw a chess piece on the board."""
        piece = self.display_board.piece_at(square)
        if not piece:
            return
        
        # Convert to display coordinates
        display_file, display_rank = self._get_display_coordinates(file_idx, rank_idx)
        
        piece_x = offset_x + display_file * self.square_size + self.square_size // 2
        piece_y = offset_y + display_rank * self.square_size + self.square_size // 2
        
        # Choose font weight and color based on piece color
        if piece.color == chess.WHITE:
            font = (PIECE_FONT_NAME, piece_font_size, 'bold')
            fill_color = WHITE_PIECE_COLOR
        else:
            font = (PIECE_FONT_NAME, piece_font_size, 'normal')
            fill_color = BLACK_PIECE_COLOR
            
        self.canvas.create_text(piece_x, piece_y, text=PIECE_UNICODES[piece.symbol()],
                              font=font, fill=fill_color)

    def _draw_move_highlights(self, offset_x: int, offset_y: int):
        """Draw highlights for possible moves of the selected piece."""
        if not self.selected:
            return
            
        # Convert selected display coordinates back to chess coordinates
        selected_file, selected_rank = self._get_chess_coordinates_from_display(
            self.selected[0], self.selected[1])
        from_square = chess.square(selected_file, selected_rank)
        
        for move in self.display_board.legal_moves:
            if move.from_square != from_square:
                continue
                
            # Get chess coordinates of the target square
            to_file = chess.square_file(move.to_square)
            to_rank = chess.square_rank(move.to_square)
            
            # Convert to display coordinates
            display_file, display_rank = self._get_display_coordinates(to_file, to_rank)
            
            center_x = offset_x + display_file * self.square_size + self.square_size // 2
            center_y = offset_y + display_rank * self.square_size + self.square_size // 2
            radius = max(4, self.square_size // HIGHLIGHT_RADIUS_SCALE)
            
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  fill=HIGHLIGHT_COLOR, outline='orange', width=2)

    def update_captured_panel(self):
        """Update captured pieces display using engine's capture tracking."""
        try:
            white_captures = self.engine.get_captured_by_white()
            black_captures = self.engine.get_captured_by_black()
        except Exception:
            # Fallback if engine doesn't support capture tracking
            white_captures = {}
            black_captures = {}

        def format_captures(capture_dict):
            """Format capture dictionary into display string."""
            parts = []
            for piece_type in CAPTURE_ORDER:
                count = capture_dict.get(piece_type, 0)
                if count > 0:
                    unicode_symbol = PIECE_UNICODES[piece_type]
                    parts.append(f"{unicode_symbol} * {count}")
            return ', '.join(parts) if parts else 'None'

        self.captured_white_label.config(text=format_captures(white_captures))
        self.captured_black_label.config(text=format_captures(black_captures))

    def on_resize(self, event):
        """Handle canvas resize by recalculating square size and redrawing."""
        try:
            canvas_width = event.width
            canvas_height = event.height
        except AttributeError:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

        # Calculate new square size to fit canvas
        available_size = min(canvas_width, canvas_height)
        new_square_size = max(MIN_SQUARE_SIZE, available_size // BOARD_DIM)
        
        if new_square_size != self.square_size:
            self.square_size = new_square_size
            self.draw_board()

    def draw_board(self):
        """Render the complete chess board with pieces and highlights."""
        self.canvas.delete('all')
        
        # Calculate layout metrics
        board_size, offset_x, offset_y = self._calculate_board_metrics()
        piece_font_size, coord_font_size = self._calculate_font_sizes()
        coord_font = (PIECE_FONT_NAME, coord_font_size)

        # Draw all squares with coordinates and pieces
        for rank_idx in range(BOARD_DIM):
            for file_idx in range(BOARD_DIM):
                # Draw square and coordinates
                self._draw_square_and_coordinates(file_idx, rank_idx, offset_x, offset_y, coord_font)
                
                # Draw piece if present
                square = chess.square(file_idx, rank_idx)
                self._draw_piece(square, file_idx, rank_idx, offset_x, offset_y, piece_font_size)

        # Draw move highlights
        self._draw_move_highlights(offset_x, offset_y)
        
        # Update captured pieces display
        self.update_captured_panel()

    def on_click(self, event):
        """Handle mouse clicks on the chess board."""
        if self.ai_thinking:
            return
            
        clicked_square = self._get_clicked_square(event.x, event.y)
        if clicked_square is None:
            return

        # clicked_square contains display coordinates
        display_file, display_rank = clicked_square
        
        # Convert to chess coordinates
        chess_file, chess_rank = self._get_chess_coordinates_from_display(display_file, display_rank)
        square = chess.square(chess_file, chess_rank)
        
        if self.selected is None:
            self._handle_piece_selection(square, display_file, display_rank)
        else:
            self._handle_move_attempt(square, display_file, display_rank)

    def _handle_piece_selection(self, square: int, display_file: int, display_rank: int):
        """Handle selection of a piece."""
        piece = self.display_board.piece_at(square)
        if piece and piece.color == self.player_color:
            self.selected = (display_file, display_rank)  # Store display coordinates
            self.draw_board()

    def _handle_move_attempt(self, target_square: int, display_file: int, display_rank: int):
        """Handle attempt to move the selected piece."""
        # Convert selected display coordinates to chess coordinates
        selected_chess_file, selected_chess_rank = self._get_chess_coordinates_from_display(
            self.selected[0], self.selected[1])
        from_square = chess.square(selected_chess_file, selected_chess_rank)
        
        # Find matching legal move
        move = self._find_legal_move(from_square, target_square)
        
        if move:
            self._execute_player_move(move)
        else:
            self._handle_invalid_move(target_square, display_file, display_rank)

    def _find_legal_move(self, from_square: int, to_square: int) -> Optional[chess.Move]:
        """Find a legal move matching the from and to squares."""
        for legal_move in self.display_board.legal_moves:
            if (legal_move.from_square == from_square and 
                legal_move.to_square == to_square):
                return legal_move
        return None

    def _execute_player_move(self, move: chess.Move):
        """Execute a player move and trigger AI response."""
        # Update game state
        self.engine.push(move)
        self.display_board = chess.Board(self.engine.board.fen())
        self.last_move = move
        self.selected = None
        
        # Refresh display
        self.draw_board()
        
        # Handle game continuation
        if self.display_board.is_game_over():
            self.update_status()
        else:
            self.status.config(text="AI thinking...")
            self.root.after(AI_MOVE_DELAY, self.ai_move)

    def _handle_invalid_move(self, target_square: int, display_file: int, display_rank: int):
        """Handle invalid move attempt by reselecting or deselecting."""
        piece = self.display_board.piece_at(target_square)
        if piece and piece.color == self.player_color:
            self.selected = (display_file, display_rank)
        else:
            self.selected = None
        self.draw_board()

    def ai_move(self):
        """Start AI move calculation in a background thread."""
        if self.display_board.is_game_over() or self.ai_thinking:
            return

        self.ai_thinking = True
        self.status.config(text="AI thinking...", foreground='black')

        def compute_move():
            """Background thread function to compute AI move."""
            try:
                uci_move = self.engine.find_best_move()
                best_move = chess.Move.from_uci(uci_move) if uci_move else None
                self.root.after(0, lambda move=best_move: self._apply_ai_move(move))
            except Exception as error:
                self.root.after(0, lambda err=error: self._handle_ai_error(err))

        threading.Thread(target=compute_move, daemon=True).start()

    def _apply_ai_move(self, move: Optional[chess.Move]):
        """Apply AI move on the main thread."""
        try:
            if move and move in self.engine.legal_moves():
                self.engine.push(move)
                self.display_board = chess.Board(self.engine.board.fen())
                self.last_move = move

            self.ai_thinking = False
            self.draw_board()
            self.update_status()
        except Exception as error:
            self._handle_ai_error(error)

    def _handle_ai_error(self, error: Exception):
        """Handle AI computation errors."""
        self.ai_thinking = False
        error_text = str(error)[:MAX_ERROR_DISPLAY_LENGTH]
        self.status.config(text=f"AI Error: {error_text}...", foreground='red')
        print(f"AI Error: {error}")  # For debugging
    
    def update_status(self):
        """Update status display based on current game state."""
        if self.display_board.is_game_over():
            self._display_game_over_status()
        else:
            self._display_turn_status()

    def _display_game_over_status(self):
        """Display appropriate game over message."""
        outcome = self.display_board.outcome()
        
        if outcome.winner is None:
            self.status.config(text="Game Over - Draw!", foreground='blue')
        elif outcome.winner == chess.WHITE:
            self.status.config(text="Game Over - White Wins!", foreground='green')
        else:
            self.status.config(text="Game Over - Black Wins!", foreground='red')

    def _display_turn_status(self):
        """Display whose turn it is to move."""
        if self.display_board.turn == chess.WHITE:
            self.status.config(text="White to move", foreground='black')
        else:
            self.status.config(text="Black to move", foreground='black')

    def new_game(self):
        """Reset to a new game and start AI if needed."""
        self.ai_thinking = False
        self.engine.reset()
        self.display_board = chess.Board(self.engine.board.fen())
        self.selected = None
        self.last_move = None
        
        self.draw_board()
        self.update_status()
        
        # Start AI if it should move first
        if self.engine.board.turn != self.player_color:
            self.root.after(AI_MOVE_DELAY, self.ai_move)

    def undo_move(self):
        """Undo the last two moves (player and AI)."""
        if self.ai_thinking:
            return

        # Undo up to two moves to return to player's turn
        moves_to_undo = min(2, len(self.engine.board.move_stack))
        for _ in range(moves_to_undo):
            self.engine.pop()

        # Update display state
        self.display_board = chess.Board(self.engine.board.fen())
        self.last_move = (self.engine.board.move_stack[-1] 
                         if self.engine.board.move_stack else None)
        self.selected = None
        
        self.draw_board()
        self.update_status()

    def end_game(self):
        """End current game and return to start screen."""
        if self.ai_thinking:
            return

        try:
            self.main_frame.destroy()
        except Exception:
            pass

        if callable(self.on_end):
            try:
                self.on_end()
            except Exception as error:
                print(f"Error returning to start screen: {error}")

class StartScreen:
    """Initial screen for selecting game options."""
    
    def __init__(self, master):
        self.master = master
        self._create_start_interface()

    def _create_start_interface(self):
        """Create the start screen interface."""
        self.frame = ttk.Frame(self.master, padding=MAIN_PADDING * 2)
        self.frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self._add_title_and_subtitle()
        self._add_game_options()

    def _add_title_and_subtitle(self):
        """Add title and subtitle labels."""
        title = ttk.Label(self.frame, text=APP_TITLE, 
                         font=(PIECE_FONT_NAME, TITLE_FONT_SIZE, 'bold'))
        title.grid(row=0, column=0, pady=(MAIN_PADDING, MAIN_PADDING * 2))

        subtitle = ttk.Label(self.frame, text='Choose color to play', 
                           font=(PIECE_FONT_NAME, SUBTITLE_FONT_SIZE))
        subtitle.grid(row=1, column=0, pady=(0, MAIN_PADDING))

    def _add_game_options(self):
        """Add game option buttons."""
        button_configs = [
            ('Play as White', self._start_as_white, 2),
            ('Play as Black', self._start_as_black, 3),
            ('Quit', self.master.destroy, 4)
        ]
        
        for text, command, row in button_configs:
            pady = (SIDE_PANEL_PADDING, 4) if row < 4 else (4, SIDE_PANEL_PADDING)
            ttk.Button(self.frame, text=text, command=command).grid(
                row=row, column=0, pady=pady)

    def _start_as_white(self):
        """Start game with player as White."""
        self._start_game(chess.WHITE)

    def _start_as_black(self):
        """Start game with player as Black."""
        self._start_game(chess.BLACK)

    def _start_game(self, player_color: chess.Color):
        """Start a new chess game with the specified player color."""
        self._cleanup_start_screen()
        
        def return_to_start():
            """Callback to recreate start screen."""
            StartScreen(self.master)
            
        ChessGUI(self.master, on_end=return_to_start, player_color=player_color)

    def _cleanup_start_screen(self):
        """Clean up the start screen interface."""
        try:
            self.frame.destroy()
        except Exception:
            pass


def main():
    """Main application entry point."""
    root = tk.Tk()
    StartScreen(root)
    root.mainloop()

if __name__ == '__main__':
    main()
