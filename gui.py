import tkinter as tk
from tkinter import ttk
import chess
from evaluation import alpha_beta
from typing import Optional, Tuple

# === Config / constants (remove magic numbers) ===
BOARD_DIM = 8
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 500
DEFAULT_SQUARE_SIZE = 60
MIN_SQUARE_SIZE = 30

# AI search settings
DEFAULT_SEARCH_DEPTH = 3
ALPHA_INIT = -100000
BETA_INIT = 100000

# Color scheme
LIGHT_SQUARE = '#F0D9B5'
DARK_SQUARE = '#B58863'
HIGHLIGHT_COLOR = '#FFFF99'
SELECTED_COLOR = '#90EE90'
LAST_MOVE_COLOR = '#FFE4B5'

# Piece Unicode symbols (clean and consistent)
PIECE_UNICODES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}

# UI font & piece color constants
PIECE_FONT_NAME = 'Arial'
# White pieces render as white and thicker (bold)
WHITE_PIECE_COLOR = '#FFFFFF'
# Black pieces render as black and thinner (normal)
BLACK_PIECE_COLOR = '#000000'

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Chess Bot - Player vs AI')
        self.root.geometry(f'{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}')
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Game state
        self.board = chess.Board()
        self.selected = None
        self.last_move = None
        self.square_size = DEFAULT_SQUARE_SIZE
        
        # Configure root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
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
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Configure>', self.on_resize)
        
        # Initial draw
        self.root.after(100, self.draw_board)

    # --- Helper utilities ---
    def _board_size_and_offsets(self) -> Tuple[int, int, int]:
        board_size = self.square_size * BOARD_DIM
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        offset_x = (canvas_w - board_size) // 2 if canvas_w > board_size else 0
        offset_y = (canvas_h - board_size) // 2 if canvas_h > board_size else 0
        return board_size, offset_x, offset_y

    def _square_from_click(self, x: int, y: int) -> Optional[Tuple[int, int]]:
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

    def on_resize(self, event):
        """Handle canvas resize events"""
        # Prefer the event size (fast) but fall back to canvas widget size
        try:
            canvas_width = event.width
            canvas_height = event.height
        except Exception:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

        # Calculate square size based on available space
        size = min(canvas_width, canvas_height) // BOARD_DIM
        self.square_size = max(MIN_SQUARE_SIZE, size)  # Minimum size

        self.draw_board()
    
    def draw_board(self):
        """Draw the chess board with pieces"""
        self.canvas.delete('all')

        # Calculate board dimensions and offsets
        board_size, offset_x, offset_y = self._board_size_and_offsets()

        # Dynamic font size based on square size
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

                # Determine square color
                is_light = (rank_idx + file_idx) % 2 == 0
                color = LIGHT_SQUARE if is_light else DARK_SQUARE

                # Highlight selected square
                if self.selected and self.selected == (file_idx, rank_idx):
                    color = SELECTED_COLOR

                # Highlight last move
                square = chess.square(file_idx, 7 - rank_idx)
                if (self.last_move and 
                    (square == self.last_move.from_square or square == self.last_move.to_square)):
                    color = LAST_MOVE_COLOR

                # Draw square
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='#8B4513', width=1)

                # Draw coordinates
                if file_idx == 0:  # Rank numbers on left
                    self.canvas.create_text(x0 + 5, y0 + 10, text=str(BOARD_DIM - rank_idx), 
                                          font=coord_font, fill='#654321', anchor='nw')
                if rank_idx == BOARD_DIM - 1:  # File letters at bottom
                    self.canvas.create_text(x1 - 10, y1 - 5, text=chr(ord('a') + file_idx), 
                                          font=coord_font, fill='#654321', anchor='se')

                # Draw piece: white pieces are bold+white, black pieces normal+black
                piece = self.board.piece_at(square)
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

        # Highlight possible moves for selected piece
        if self.selected:
            from_square = chess.square(self.selected[0], 7 - self.selected[1])
            for move in self.board.legal_moves:
                if move.from_square == from_square:
                    to_file = chess.square_file(move.to_square)
                    to_rank = 7 - chess.square_rank(move.to_square)
                    x = offset_x + to_file * self.square_size + self.square_size // 2
                    y = offset_y + to_rank * self.square_size + self.square_size // 2
                    radius = max(4, self.square_size // 8)
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                          fill=HIGHLIGHT_COLOR, outline='orange', width=2)

    def on_click(self, event):
        """Handle mouse clicks on the board"""
        res = self._square_from_click(event.x, event.y)
        if res is None:
            return
        file_idx, rank_idx = res
        square = chess.square(file_idx, 7 - rank_idx)
        
        if self.selected is None:
            # Select a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected = (file_idx, rank_idx)
                self.draw_board()
        else:
            # Try to make a move
            from_square = chess.square(self.selected[0], 7 - self.selected[1])
            
            # Check for promotion moves
            move = None
            for legal_move in self.board.legal_moves:
                if legal_move.from_square == from_square and legal_move.to_square == square:
                    move = legal_move
                    break
            
            if move:
                self.board.push(move)
                self.last_move = move
                self.selected = None
                self.draw_board()

                if self.board.is_game_over():
                    self.update_status()
                else:
                    self.status.config(text="AI thinking...")
                    self.root.after(100, self.ai_move)
            else:
                # Invalid move, try to select new piece
                piece = self.board.piece_at(square)
                if piece and piece.color == chess.WHITE:
                    self.selected = (file_idx, rank_idx)
                else:
                    self.selected = None
                self.draw_board()

    def ai_move(self):
        """Execute AI move"""
        if self.board.is_game_over():
            self.update_status()
            return
        best_move = None
        alpha, beta = ALPHA_INIT, BETA_INIT
        depth = DEFAULT_SEARCH_DEPTH

        for move in self.board.legal_moves:
            self.board.push(move)
            score = -alpha_beta(-beta, -alpha, self.board, depth)
            self.board.pop()
            if best_move is None or score > alpha:
                best_move = move
                alpha = score

        if best_move:
            self.board.push(best_move)
            self.last_move = best_move

        self.draw_board()
        self.update_status()
    
    def update_status(self):
        """Update the status label based on game state"""
        if self.board.is_game_over():
            outcome = self.board.outcome()
            if outcome.winner is None:
                self.status.config(text="Game Over - Draw!", foreground='blue')
            elif outcome.winner == chess.WHITE:
                self.status.config(text="Game Over - White Wins!", foreground='green')
            else:
                self.status.config(text="Game Over - Black Wins!", foreground='red')
        elif self.board.turn == chess.WHITE:
            self.status.config(text="White to move", foreground='black')
        else:
            self.status.config(text="Black to move", foreground='black')
    
    def new_game(self):
        """Start a new game"""
        self.board = chess.Board()
        self.selected = None
        self.last_move = None
        self.draw_board()
        self.update_status()
    
    def undo_move(self):
        """Undo the last two moves (player and AI)"""
        # Pop up to two moves safely
        pops = min(2, len(self.board.move_stack))
        for _ in range(pops):
            self.board.pop()

        # Maintain last_move safely
        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        
        self.selected = None
        self.draw_board()
        self.update_status()

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
