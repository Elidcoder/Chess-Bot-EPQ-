"""
Home page component for the chess application.

This module provides the initial screen for selecting game options.
"""

import tkinter as tk
from tkinter import ttk
import chess
from typing import Callable, Optional

# Constants for home page layout
TITLE_FONT_SIZE = 50
SUBTITLE_FONT_SIZE = 30
BUTTON_FONT_SIZE = 18
PIECE_FONT_NAME = 'Arial'
HOME_PADDING = 30
BUTTON_SPACING = 15
TITLE_SPACING = 20
# Button color scheme to make controls stand out from the background
BUTTON_BG = '#ADD8E6'  # warm yellow
BUTTON_FG = '#000000'  # black text
BUTTON_ACTIVE_BG = '#FFB84D'


class HomePage:
    """Initial screen for selecting game options."""
    
    def __init__(self, parent: tk.Widget, app_title: str = "Chess Challenge"):
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
        self.on_play_white: Optional[Callable[[], None]] = None
        self.on_play_black: Optional[Callable[[], None]] = None
        
    def set_callbacks(self, 
                     on_play_white: Callable[[], None],
                     on_play_black: Callable[[], None]):
        """Set callback functions for button actions."""
        self.on_play_white = on_play_white
        self.on_play_black = on_play_black
        
    def show(self):
        """Display the home page."""
        self._create_interface()
        
    def hide(self):
        """Hide the home page."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
            
    def _create_interface(self):
        """Create the home page interface."""
        # Main container frame - centered
        self.frame = ttk.Frame(self.parent)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Configure parent for centering
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            self.frame, 
            text=self.app_title,
            font=(PIECE_FONT_NAME, TITLE_FONT_SIZE, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, TITLE_SPACING))
        
        # Subtitle  
        subtitle_label = ttk.Label(
            self.frame,
            text='Choose your side',
            font=(PIECE_FONT_NAME, SUBTITLE_FONT_SIZE)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, TITLE_SPACING))
        
        # Buttons container
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.grid(row=2, column=0, pady=(TITLE_SPACING, 0))
        
        # Game option buttons
        button_configs = [
            ('♔ Play as White', self._handle_play_white, 0),
            ('♛ Play as Black', self._handle_play_black, 1)
        ]
        
        for text, command, row in button_configs:
            # Make the start buttons larger and easier to click; use tk.Button so font/ipad options work
            button = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                width=24,
                font=(PIECE_FONT_NAME, BUTTON_FONT_SIZE),
                bg=BUTTON_BG,
                fg=BUTTON_FG,
                activebackground=BUTTON_ACTIVE_BG,
                relief='raised',
                bd=2
            )
            # Add internal padding (ipadx/ipady) so the button visually appears bigger
            button.grid(row=row, column=0, pady=(BUTTON_SPACING, BUTTON_SPACING//2),
                        padx=HOME_PADDING, ipadx=24, ipady=10)
            
    def _handle_play_white(self):
        """Handle Play as White button click."""
        if self.on_play_white:
            self.on_play_white()
            
    def _handle_play_black(self):
        """Handle Play as Black button click.""" 
        if self.on_play_black:
            self.on_play_black()
