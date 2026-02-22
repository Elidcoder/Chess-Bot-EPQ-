"""
Home page component for the chess application.

This module provides the initial screen for selecting game options.
"""

import tkinter as tk
from tkinter import ttk
import chess
from typing import Callable, Optional
from ui_config import UIConfig

class HomePage:
    """Initial screen for selecting game options."""
    
    def __init__(self, parent: tk.Widget, app_title: str = UIConfig.game.APP_TITLE):
        """
        Initialize the home page.
        
        Args:
            parent: The parent widget to contain the home page
            app_title: Title to display on the home page
        """
        self.parent = parent
        self.app_title = app_title
        self.frame: Optional[ttk.Frame] = None
        
        # Callbacks
        self._on_play_white: Optional[Callable[[], None]] = None
        self._on_play_black: Optional[Callable[[], None]] = None
        
    def set_callbacks(self, 
                     on_play_white: Callable[[], None],
                     on_play_black: Callable[[], None]):
        """Set callback functions for button actions."""
        self._on_play_white = on_play_white
        self._on_play_black = on_play_black
        
    def show(self):
        """Display the home page."""
        self._create_interface()
        
    def hide(self):
        """Hide the home page."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
            
    def _create_interface(self):
        """Create the home page interface using centralized UI configuration."""
        # Main container frame - centered
        self.frame = ttk.Frame(self.parent)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Configure parent for centering
        self._setup_parent_grid()
        
        # Create UI elements
        self._create_title()
        self._create_subtitle()
        self._create_buttons()
    
    def _setup_parent_grid(self):
        """Configure parent widget grid for proper centering."""
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
    
    def _create_title(self):
        """Create the main title label."""
        title_label = ttk.Label(
            self.frame, 
            text=self.app_title,
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.HOME_TITLE_SIZE, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, UIConfig.layout.TITLE_SPACING))
    
    def _create_subtitle(self):
        """Create the subtitle label."""
        subtitle_label = ttk.Label(
            self.frame,
            text='Choose your side',
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.HOME_SUBTITLE_SIZE)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, UIConfig.layout.TITLE_SPACING))
    
    def _create_buttons(self):
        """Create the game selection buttons."""
        # Buttons container
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=0, pady=(UIConfig.layout.TITLE_SPACING, 0))
        
        # Button configurations with chess piece symbols
        button_configs = [
            ('♔ Play as White', self._handle_play_white, 0),
            ('♛ Play as Black', self._handle_play_black, 1)
        ]
        
        for text, command, row in button_configs:
            self._create_game_button(buttons_frame, text, command, row)
    
    def _create_game_button(self, parent: tk.Widget, text: str, command: Callable, row: int):
        """Create a single game selection button with consistent styling."""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=24,
            font=(UIConfig.fonts.FAMILY, UIConfig.fonts.HOME_BUTTON_SIZE),
            bg=UIConfig.colors.BUTTON_BG,
            fg=UIConfig.colors.BUTTON_FG,
            activebackground=UIConfig.colors.BUTTON_ACTIVE_BG,
            relief='raised',
            bd=2
        )
        
        # Grid with padding for visual appeal
        button.grid(
            row=row, 
            column=0, 
            pady=(UIConfig.layout.BUTTON_SPACING, UIConfig.layout.BUTTON_SPACING // 2),
            padx=UIConfig.layout.HOME_PADDING, 
            ipadx=24, 
            ipady=10
        )
            
    def _handle_play_white(self):
        """Handle Play as White button click."""
        if self._on_play_white:
            self._on_play_white()
            
    def _handle_play_black(self):
        """Handle Play as Black button click."""
        if self._on_play_black:
            self._on_play_black()
            