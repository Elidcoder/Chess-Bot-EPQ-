"""
UI configuration constants for the chess application.

This module centralizes all UI-related constants to eliminate magic numbers
and provide a single source of truth for visual styling.
"""

from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class WindowConfig:
    """Window dimensions and constraints."""
    DEFAULT_WIDTH: int = 600
    DEFAULT_HEIGHT: int = 700
    MIN_WIDTH: int = 400
    MIN_HEIGHT: int = 500

@dataclass(frozen=True)
class FontConfig:
    """Font family and size configurations."""
    FAMILY: str = 'Arial'
    
    # Home page fonts
    HOME_TITLE_SIZE: int = 50
    HOME_SUBTITLE_SIZE: int = 30
    HOME_BUTTON_SIZE: int = 18
    
    # Game interface fonts
    STATUS_SIZE: int = 14
    CAPTURED_SIZE: int = 16
    CAPTURED_LABEL_SIZE: int = 12
    TITLE_SIZE: int = 22
    SUBTITLE_SIZE: int = 16

@dataclass(frozen=True)
class ColorConfig:
    """Color scheme for UI elements."""
    # Board colors
    LIGHT_SQUARE: str = '#F0D9B5'
    DARK_SQUARE: str = '#B58863'
    HIGHLIGHT_COLOR: str = '#FFFF99'
    SELECTED_COLOR: str = '#90EE90'
    LAST_MOVE_COLOR: str = '#FFE4B5'
    BOARD_OUTLINE: str = '#8B4513'
    COORD_TEXT: str = '#654321'
    
    # Piece colors
    WHITE_PIECE: str = '#FFFFFF'
    BLACK_PIECE: str = '#000000'
    
    # Button colors
    BUTTON_BG: str = '#ADD8E6'
    BUTTON_FG: str = '#000000'
    BUTTON_ACTIVE_BG: str = '#FFB84D'

@dataclass(frozen=True)
class LayoutConfig:
    """Layout spacing and dimensions."""
    MAIN_PADDING: int = 10
    SIDE_PANEL_PADDING: int = 8
    BUTTON_PADDING: int = 5
    BORDER_WIDTH: int = 2
    
    # Home page layout
    HOME_PADDING: int = 30
    BUTTON_SPACING: int = 15
    TITLE_SPACING: int = 20
    
    # Board layout
    COORD_OFFSET: int = 5
    COORD_CORNER_OFFSET: int = 10

@dataclass(frozen=True)
class BoardConfig:
    """Board rendering configuration."""
    DIMENSION: int = 8
    DEFAULT_SQUARE_SIZE: int = 72
    MIN_SQUARE_SIZE: int = 36
    PIECE_FONT_SCALE: float = 0.65
    COORD_FONT_SCALE: float = 0.25
    MIN_PIECE_FONT_SIZE: int = 20
    MIN_COORD_FONT_SIZE: int = 10
    HIGHLIGHT_RADIUS_SCALE: int = 8

@dataclass(frozen=True)
class TimingConfig:
    """Timing delays for UI operations."""
    INITIAL_DRAW_DELAY: int = 100
    AI_START_DELAY: int = 200
    AI_MOVE_DELAY: int = 100

@dataclass(frozen=True)
class GameConfig:
    """Game-related configuration."""
    DEFAULT_SEARCH_DEPTH: int = 3
    MAX_ERROR_DISPLAY_LENGTH: int = 30
    APP_TITLE: str = "Chess Challenge"

class UIConfig:
    """Centralized UI configuration container."""
    
    window = WindowConfig()
    fonts = FontConfig()
    colors = ColorConfig()
    layout = LayoutConfig()
    board = BoardConfig()
    timing = TimingConfig()
    game = GameConfig()
