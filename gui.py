import tkinter as tk
from tkinter import ttk
import chess
from engine import get_default_engine, Engine
from typing import Optional, Tuple
import threading

# Board constants
BOARD_DIM = 8
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 500
DEFAULT_SQUARE_SIZE = 60
MIN_SQUARE_SIZE = 30
APP_TITLE = "Chess Challenge"

# Search parameters
DEFAULT_SEARCH_DEPTH = 3
ALPHA_INIT = -100000
BETA_INIT = 100000

# Colors
LIGHT_SQUARE    = '#F0D9B5'
DARK_SQUARE     = '#B58863'
HIGHLIGHT_COLOR = '#FFFF99'
SELECTED_COLOR  = '#90EE90'
LAST_MOVE_COLOR = '#FFE4B5'
# White pieces bold
WHITE_PIECE_COLOR = '#FFFFFF'
# Black pieces thin 
BLACK_PIECE_COLOR = '#000000'

# Piece Constants
PIECE_FONT_NAME = 'Arial'
PIECE_UNICODES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f'{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}')
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Game state
        self.engine = get_default_engine(DEFAULT_SEARCH_DEPTH)
        self.display_board = chess.Board(self.engine.board.fen())
        self.selected = None
        self.last_move = None
        self.square_size = DEFAULT_SQUARE_SIZE
        self.ai_thinking = False
        
        # Configure root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status = ttk.Label(status_frame, text="White to move", font=('Arial', 12, 'bold'))
        self.status.grid(row=0, column=0)
        
        # Buttons frame
        buttons_frame = ttk.Frame(status_frame)
        buttons_frame.grid(row=1, column=0, pady=(5, 0))
        
        ttk.Button(buttons_frame, text="New Game", command=self.new_game).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Undo Move", command=self.undo_move).grid(row=0, column=1, padx=5)
        
        # Canvas frame for the board
        canvas_frame = ttk.Frame(main_frame, relief='solid', borderwidth=2)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Captured pieces panel (right side)
        side_frame = ttk.Frame(main_frame, padding=(8,0))
        side_frame.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E), padx=(10,0))

        ttk.Label(side_frame, text="Captured", font=(PIECE_FONT_NAME, 12, 'bold')).grid(row=0, column=0, pady=(0,6))
        ttk.Label(side_frame, text="White's captures:", font=(PIECE_FONT_NAME, 10)).grid(row=1, column=0, sticky='w')
        self.captured_white_label = ttk.Label(side_frame, text="", font=(PIECE_FONT_NAME, 14))
        self.captured_white_label.grid(row=2, column=0, sticky='w', pady=(2,8))

        ttk.Label(side_frame, text="Black's captures:", font=(PIECE_FONT_NAME, 10)).grid(row=3, column=0, sticky='w')
        self.captured_black_label = ttk.Label(side_frame, text="", font=(PIECE_FONT_NAME, 14))
        self.captured_black_label.grid(row=4, column=0, sticky='w', pady=(2,8))
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Initial draw
        self.root.after(100, self.draw_board)

    # Helper function 
    # Returns board size (Int) and the X & Y offsets (Int)
    def _board_size_and_offsets(self) -> Tuple[int, int, int]:
        board_size = self.square_size * BOARD_DIM
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        offset_x = (canvas_w - board_size) // 2 if canvas_w > board_size else 0
        offset_y = (canvas_h - board_size) // 2 if canvas_h > board_size else 0
        return board_size, offset_x, offset_y

    # Helper function
    # Returns the square clicked if possible 
    def square_clicked(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        board_size, offset_x, offset_y = self._board_size_and_offsets()
        click_x = x - offset_x
        click_y = y - offset_y
        if click_x < 0 or click_y < 0 or click_x >= board_size or click_y >= board_size:
            return None
        file_idx = click_x // self.square_size
        rank_idx = click_y // self.square_size
        if not (0 <= file_idx < BOARD_DIM and 0 <= rank_idx < BOARD_DIM):
            return None
        return int(file_idx), int(rank_idx)

    def update_captured_panel(self):
        """Update the captured pieces labels based on material missing from board."""
        # Count pieces on the board snapshot 
        piece_map = self.display_board.piece_map()
        counts = {}
        for sq, piece in piece_map.items():
            counts[piece.symbol()] = counts.get(piece.symbol(), 0) + 1

        # All starting counts
        start = {'P':8,'N':2,'B':2,'R':2,'Q':1,'K':1,'p':8,'n':2,'b':2,'r':2,'q':1,'k':1}

        white_captured = []
        black_captured = []
        # Find missing whites
        for sym, total in start.items():
            have = counts.get(sym, 0)
            missing = total - have
            if missing > 0:
                if sym.isupper():
                    # white piece missing -> black captured
                    black_captured += [PIECE_UNICODES[sym.lower()] for _ in range(missing)]
                else:
                    white_captured += [PIECE_UNICODES[sym] for _ in range(missing)]

        self.captured_white_label.config(text=' '.join(white_captured) or 'None')
        self.captured_black_label.config(text=' '.join(black_captured) or 'None')

    # Prefer the event size (fast) but fall back to canvas widget size
    def on_resize(self, event):
        """Handle canvas resize events"""
        try:
            canvas_width = event.width
            canvas_height = event.height
        except Exception:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

        # Calculate square size based on available space
        size = min(canvas_width, canvas_height) // BOARD_DIM
        self.square_size = max(MIN_SQUARE_SIZE, size)

        self.draw_board()
    
    def draw_board(self):
        """Draw the chess board with pieces"""
        self.canvas.delete('all')

        # Get font size based on square size
        board_size, offset_x, offset_y = self._board_size_and_offsets()
        piece_font_size = max(16, int(self.square_size * 0.6))
        coord_font_size = max(8, int(self.square_size * 0.2))
        piece_font = (PIECE_FONT_NAME, piece_font_size)
        coord_font = (PIECE_FONT_NAME, coord_font_size)

        # Draw squares and coordinates
        for rank_idx in range(BOARD_DIM):
            for file_idx in range(BOARD_DIM):
                x0 = offset_x + file_idx * self.square_size
                y0 = offset_y + rank_idx * self.square_size
                x1 = x0 + self.square_size
                y1 = y0 + self.square_size                

                # Color squares
                square = chess.square(file_idx, 7 - rank_idx)
                if (self.last_move and 
                    (square == self.last_move.from_square or square == self.last_move.to_square)):
                    color = LAST_MOVE_COLOR
                elif self.selected and self.selected == (file_idx, rank_idx):
                    color = SELECTED_COLOR
                else: 
                    color = DARK_SQUARE if ((rank_idx + file_idx) % 2) else LIGHT_SQUARE

                # Draw square
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='#8B4513', width=1)

                # Draw rank numbers
                if file_idx == 0:
                    self.canvas.create_text(x0 + 5, y0 + 10, text=str(BOARD_DIM - rank_idx), 
                                          font=coord_font, fill='#654321', anchor='nw')

                # Draw file letters
                if rank_idx == BOARD_DIM - 1:
                    self.canvas.create_text(x1 - 10, y1 - 5, text=chr(ord('a') + file_idx), 
                                          font=coord_font, fill='#654321', anchor='se')

                # Draw pieces
                piece = self.display_board.piece_at(square)
                if piece:
                    piece_x = x0 + self.square_size // 2
                    piece_y = y0 + self.square_size // 2
                    if piece.color == chess.WHITE:
                        pf = (PIECE_FONT_NAME, piece_font_size, 'bold')
                        fill_color = WHITE_PIECE_COLOR
                    else:
                        pf = (PIECE_FONT_NAME, piece_font_size, 'normal')
                        fill_color = BLACK_PIECE_COLOR
                    self.canvas.create_text(piece_x, piece_y, text=PIECE_UNICODES[piece.symbol()], 
                                          font=pf, fill=fill_color)

        # Highlight possible moves for piece
        if self.selected:
            from_square = chess.square(self.selected[0], 7 - self.selected[1])
            for move in self.display_board.legal_moves:
                if move.from_square == from_square:
                    to_file = chess.square_file(move.to_square)
                    to_rank = 7 - chess.square_rank(move.to_square)
                    x = offset_x + to_file * self.square_size + self.square_size // 2
                    y = offset_y + to_rank * self.square_size + self.square_size // 2
                    radius = max(4, self.square_size // 8)
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                          fill=HIGHLIGHT_COLOR, outline='orange', width=2)

        # Update captured pieces panel
        self.update_captured_panel()

    def on_click(self, event):
        # Ignore input while AI is thinking
        if self.ai_thinking:
            return
        res = self.square_clicked(event.x, event.y)
        if res is None:
            return

        file_idx, rank_idx = res
        square = chess.square(file_idx, BOARD_DIM - 1 - rank_idx)
        
        if self.selected is None:
            # Select a piece
            piece = self.display_board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected = (file_idx, rank_idx)
                self.draw_board()
        else:
            # Try to make a move
            from_square = chess.square(self.selected[0], BOARD_DIM - 1 - self.selected[1])
            
            # Check for promotion moves
            move = None
            for legal_move in self.display_board.legal_moves:
                if legal_move.from_square == from_square and legal_move.to_square == square:
                    move = legal_move
                    break
            
            if move:
                # push to engine so internal state is authoritative
                self.engine.push(move)
                # refresh display board from engine after the move
                self.display_board = chess.Board(self.engine.board.fen())
                self.last_move = move
                self.selected = None
                self.draw_board()

                if self.display_board.is_game_over():
                    self.update_status()
                else:
                    self.status.config(text="AI thinking...")
                    self.root.after(100, self.ai_move)
            else:
                # Invalid move, try to select new piece
                piece = self.display_board.piece_at(square)
                if piece and piece.color == chess.WHITE:
                    self.selected = (file_idx, rank_idx)
                else:
                    self.selected = None
                self.draw_board()

    def ai_move(self):
        """Start non-blocking AI move calculation in a background thread."""
        if self.display_board.is_game_over() or self.ai_thinking:
            return

        self.ai_thinking = True
        self.status.config(text="AI thinking...", foreground='black')

        def compute_best_move():
            """Compute best move in background thread using the GUI's engine directly."""
            try:
                # Use the GUI's engine directly - it stores the current position
                uci = self.engine.find_best_move()
                best_move = chess.Move.from_uci(uci) if uci else None
                # Schedule move application on main thread
                self.root.after(0, lambda: self._apply_ai_move(best_move))
            except Exception as e:
                self.root.after(0, lambda: self._handle_ai_error(e))

        # Start background computation
        threading.Thread(target=compute_best_move, daemon=True).start()

    def _apply_ai_move(self, move):
        """Apply AI move safely on the main thread."""
        try:
            if move and move in self.engine.legal_moves():
                # apply using the engine so it remains authoritative
                self.engine.push(move)
                # refresh display board from engine after move
                self.display_board = chess.Board(self.engine.board.fen())
                self.last_move = move

            self.ai_thinking = False
            self.draw_board()
            self.update_status()
        except Exception as e:
            self._handle_ai_error(e)
            self.update_status()
        except Exception as e:
            self._handle_ai_error(e)

    def _handle_ai_error(self, error):
        """Handle AI computation errors."""
        self.ai_thinking = False
        self.status.config(text=f"AI Error: {str(error)[:30]}...", foreground='red')
        print(f"AI Error: {error}")  # Log for debugging
    
    def update_status(self):
        """Update the status label based on game state"""
        if self.display_board.is_game_over():
            outcome = self.display_board.outcome()
            if outcome.winner is None:
                self.status.config(text="Game Over - Draw!", foreground='blue')
            elif outcome.winner == chess.WHITE:
                self.status.config(text="Game Over - White Wins!", foreground='green')
            else:
                self.status.config(text="Game Over - Black Wins!", foreground='red')
        elif self.display_board.turn == chess.WHITE:
            self.status.config(text="White to move", foreground='black')
        else:
            self.status.config(text="Black to move", foreground='black')
    
    def new_game(self):
        """Start a new game"""
        # Reset AI thinking state first
        self.ai_thinking = False
        self.engine.reset()
        self.display_board = chess.Board(self.engine.board.fen())
        self.selected = None
        self.last_move = None
        self.draw_board()
        self.update_status()
    
    def undo_move(self):
        """Undo the last two moves (player and AI)"""
        # Don't allow undo while AI is thinking
        if self.ai_thinking:
            return
            
        # Pop up to two moves safely using the engine
        pops = min(2, len(self.engine.board.move_stack))
        for _ in range(pops):
            self.engine.pop()

        # refresh display board and last_move
        self.display_board = chess.Board(self.engine.board.fen())
        self.last_move = self.engine.board.move_stack[-1] if self.engine.board.move_stack else None
                               
        self.selected = None
        self.draw_board()
        self.update_status()

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
