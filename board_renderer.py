"""
Board rendering component for the chess GUI.

This module handles all the visual display logic for the chess board,
including piece positioning, coordinate labels, move highlights, and
player color orientation.
"""

import tkinter as tk
from tkinter import ttk
import chess
from typing import Optional, Tuple, Callable

# Board layout constants
BOARD_DIM = 8
DEFAULT_SQUARE_SIZE = 60
MIN_SQUARE_SIZE = 30
PIECE_FONT_SCALE = 0.6
COORD_FONT_SCALE = 0.2
MIN_PIECE_FONT_SIZE = 16
MIN_COORD_FONT_SIZE = 8

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

# Layout spacing
COORD_OFFSET = 5
COORD_CORNER_OFFSET = 10
HIGHLIGHT_RADIUS_SCALE = 8

# Piece unicode symbols
PIECE_UNICODES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}


class BoardRenderer:
    """Handles all chess board rendering and display logic."""
    
    def __init__(self, canvas: tk.Canvas, is_white_player: bool = True):
        """
        Initialize the board renderer.
        
        Args:
            canvas: The Tkinter canvas to draw on
            is_white_player: True if player is white (standard orientation)
        """
        self.canvas = canvas
        self.is_white_player = is_white_player
        self.square_size = DEFAULT_SQUARE_SIZE
        
        # Display state
        self.selected_square = None  # (display_file, display_rank)
        self.last_move = None
        self._last_board: Optional[chess.Board] = None  # Keep last rendered board for resize
        
        # Event handlers
        self.on_square_clicked: Optional[Callable[[int, int], None]] = None
        self.on_resize: Optional[Callable[[], None]] = None
        
        # Bind canvas events
        self.canvas.bind('<Button-1>', self._handle_click)
        self.canvas.bind('<Configure>', self._handle_resize)

    def set_square_click_handler(self, handler: Callable[[int, int], None]):
        """Set the callback for when a square is clicked."""
        self.on_square_clicked = handler

    def set_resize_handler(self, handler: Callable[[], None]):
        """Set the callback for when the canvas is resized."""
        self.on_resize = handler

    def render_board(self, board: chess.Board, selected_square: Optional[Tuple[int, int]] = None,
                    last_move: Optional[chess.Move] = None):
        """
        Render the complete chess board.
        
        Args:
            board: The chess board to render
            selected_square: Currently selected square in display coordinates
            last_move: Last move made (for highlighting)
        """
        self.selected_square = selected_square
        self.last_move = last_move
        self._last_board = board  # Store for resize redraws
        
        self.canvas.delete('all')
        
        # Calculate layout
        board_size, offset_x, offset_y = self._calculate_board_metrics()
        piece_font_size, coord_font_size = self._calculate_font_sizes()
        coord_font = (PIECE_FONT_NAME, coord_font_size)

        # Draw all squares, coordinates, and pieces
        for chess_rank in range(BOARD_DIM):  # 0-7 (chess ranks 1-8)
            for chess_file in range(BOARD_DIM):  # 0-7 (chess files a-h)
                square = chess.square(chess_file, chess_rank)
                
                # Draw square and coordinates
                self._draw_square_and_coordinates(
                    chess_file, chess_rank, square, offset_x, offset_y, coord_font)
                
                # Draw piece if present
                self._draw_piece(
                    board, square, chess_file, chess_rank, offset_x, offset_y, piece_font_size)

        # Draw move highlights for selected piece
        if selected_square:
            self._draw_move_highlights(board, selected_square, offset_x, offset_y)

    def _calculate_board_metrics(self) -> Tuple[int, int, int]:
        """Calculate board dimensions and positioning."""
        board_size = self.square_size * BOARD_DIM
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        offset_x = max(0, (canvas_w - board_size) // 2)
        offset_y = max(0, (canvas_h - board_size) // 2)
        
        return board_size, offset_x, offset_y

    def _calculate_font_sizes(self) -> Tuple[int, int]:
        """Calculate appropriate font sizes based on square size."""
        piece_font_size = max(MIN_PIECE_FONT_SIZE, int(self.square_size * PIECE_FONT_SCALE))
        coord_font_size = max(MIN_COORD_FONT_SIZE, int(self.square_size * COORD_FONT_SCALE))
        return piece_font_size, coord_font_size

    def _get_display_coordinates(self, chess_file: int, chess_rank: int) -> Tuple[int, int]:
        """Convert chess coordinates to display coordinates based on player color."""
        if self.is_white_player:
            # Standard orientation: a1 at bottom-left
            return chess_file, 7 - chess_rank
        else:
            # Flipped orientation: a8 at bottom-left (black player perspective)
            return 7 - chess_file, chess_rank

    def _get_chess_coordinates_from_display(self, display_file: int, display_rank: int) -> Tuple[int, int]:
        """Convert display coordinates back to chess coordinates."""
        if self.is_white_player:
            return display_file, 7 - display_rank
        else:
            return 7 - display_file, display_rank

    def _get_square_color(self, display_file: int, display_rank: int, chess_square: int) -> str:
        """Determine the display color for a board square."""
        # Check for last move highlight
        if (self.last_move and 
            chess_square in (self.last_move.from_square, self.last_move.to_square)):
            return LAST_MOVE_COLOR
            
        # Check for selection highlight
        if self.selected_square and self.selected_square == (display_file, display_rank):
            return SELECTED_COLOR
            
        # Standard checkerboard pattern based on chess coordinates
        chess_file = chess.square_file(chess_square)
        chess_rank = chess.square_rank(chess_square)
        return DARK_SQUARE if (chess_rank + chess_file) % 2 else LIGHT_SQUARE

    def _draw_square_and_coordinates(self, chess_file: int, chess_rank: int, chess_square: int,
                                   offset_x: int, offset_y: int, coord_font):
        """Draw a single board square with coordinates."""
        display_file, display_rank = self._get_display_coordinates(chess_file, chess_rank)
        
        x0 = offset_x + display_file * self.square_size
        y0 = offset_y + display_rank * self.square_size
        x1 = x0 + self.square_size
        y1 = y0 + self.square_size
        
        color = self._get_square_color(display_file, display_rank, chess_square)
        
        # Draw square
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, 
                                   outline=BOARD_OUTLINE_COLOR, width=1)
        
        # Draw rank numbers (left edge) - show chess rank (1-8)
        if display_file == 0:
            chess_rank_display = chess_rank + 1 if self.is_white_player else (8 - chess_rank)
            self.canvas.create_text(x0 + COORD_OFFSET, y0 + COORD_OFFSET, 
                                  text=str(chess_rank_display),
                                  font=coord_font, fill=COORD_TEXT_COLOR, anchor='nw')
        
        # Draw file letters (bottom edge) - show chess file (a-h)
        if display_rank == BOARD_DIM - 1:
            chess_file_display = chess_file if self.is_white_player else (7 - chess_file)
            self.canvas.create_text(x1 - COORD_CORNER_OFFSET, y1 - COORD_OFFSET,
                                  text=chr(ord('a') + chess_file_display),
                                  font=coord_font, fill=COORD_TEXT_COLOR, anchor='se')

    def _draw_piece(self, board: chess.Board, chess_square: int, chess_file: int, chess_rank: int,
                   offset_x: int, offset_y: int, piece_font_size: int):
        """Draw a chess piece on the board."""
        piece = board.piece_at(chess_square)
        if not piece:
            return
        
        # Convert to display coordinates
        display_file, display_rank = self._get_display_coordinates(chess_file, chess_rank)
        
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

    def _draw_move_highlights(self, board: chess.Board, selected_display_coords: Tuple[int, int],
                            offset_x: int, offset_y: int):
        """Draw highlights for possible moves of the selected piece."""
        # Convert selected display coordinates to chess coordinates
        selected_chess_file, selected_chess_rank = self._get_chess_coordinates_from_display(
            selected_display_coords[0], selected_display_coords[1])
        from_square = chess.square(selected_chess_file, selected_chess_rank)
        
        for move in board.legal_moves:
            if move.from_square != from_square:
                continue
                
            # Get chess coordinates of the target square
            to_chess_file = chess.square_file(move.to_square)
            to_chess_rank = chess.square_rank(move.to_square)
            
            # Convert to display coordinates
            display_file, display_rank = self._get_display_coordinates(to_chess_file, to_chess_rank)
            
            center_x = offset_x + display_file * self.square_size + self.square_size // 2
            center_y = offset_y + display_rank * self.square_size + self.square_size // 2
            radius = max(4, self.square_size // HIGHLIGHT_RADIUS_SCALE)
            
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  fill=HIGHLIGHT_COLOR, outline='orange', width=2)

    def _handle_click(self, event):
        """Handle mouse clicks on the canvas."""
        clicked_coords = self._get_clicked_display_coordinates(event.x, event.y)
        if clicked_coords and self.on_square_clicked:
            self.on_square_clicked(clicked_coords[0], clicked_coords[1])

    def _get_clicked_display_coordinates(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Convert canvas coordinates to display square coordinates."""
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

    def _handle_resize(self, event):
        """Handle canvas resize by recalculating square size."""
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
            # Automatically redraw the board with current state
            if self._last_board is not None:
                try:
                    self.render_board(self._last_board, self.selected_square, self.last_move)
                except Exception:
                    pass  # Don't let render errors crash resize handling
            
            # Notify parent that resize occurred
            if self.on_resize:
                try:
                    self.on_resize()
                except Exception:
                    pass  # Don't let callback errors crash resize handling

    def get_chess_coordinates_from_display(self, display_file: int, display_rank: int) -> Tuple[int, int]:
        """Public method to convert display coordinates to chess coordinates."""
        return self._get_chess_coordinates_from_display(display_file, display_rank)
