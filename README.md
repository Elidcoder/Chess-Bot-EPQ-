# Chess Bot with Alpha-Beta Pruning

## Table of Contents
1. [Overview](#overview)  
2. [File Structure](#file-structure)  
3. [Key Features](#key-features)  
4. [Requirements](#requirements)  
5. [How to Run](#how-to-run)  
6. [Acknowledgments](#acknowledgments)

---

## Overview
This project showcases a console-based chess engine that implements classical search algorithms: **Minimax**, **Alpha-Beta Pruning**, and **Quiescence Search**. It evaluates boardstates using piece-specific “heatmaps,” providing a positional scoring mechanism. Originally developed for my **EPQ (Extended Project Qualification)**, the primary goal was to create a functional chess AI **without** using neural networks.

---

## File Structure

1. **Main.py**  
   - **Key Contents:**  
     - Sets up the main gameplay loop.  
     - Uses Alpha-Beta search to choose the engine’s move.  
     - Continuously prompts the user for moves (in **UCI format**, e.g., `e2e4`) and updates the board state.  
     - Prints the outcome at game’s end (win/loss/draw).

2. **Evaluation.py**  
   - **Key Contents:**  
     - Defines piece heatmaps in a dictionary structure for position-based scoring.  
     - Contains methods for evaluating board positions and individual moves:  
       - `evaluate_board(board)`  
       - `evaluate_move_on_board(move, board)`  
     - Implements **Alpha-Beta Pruning** with a depth parameter and a **Quiescence Search** to handle critical captures/checks at leaf nodes.  
     - Demonstrates classic tree-search optimizations.

3. **Display_board.py**  
   - **Key Contents:**  
     - Custom color-coded, Unicode-based functions to print the chess board:  
       - `display_board_as_white(board)`  
       - `display_board_as_black(board)`  
     - Highlights squares with alternating colors and shows pieces using Unicode symbols for a user-friendly console output.

---

## Key Features
- **Human vs AI** gameplay in the console.  
- **Move Input** in standard UCI notation (e.g., `e2e4`).  
- **Alpha-Beta Pruning** to optimize Minimax decisions and reduce search tree size.  
- **Quiescence Search** to further refine evaluation at the end of the search.  
- **Heuristic Evaluation** using custom piece heatmaps for positional strength.

---

## Requirements
- **Python 3.7+** (or later)  
- **[python-chess](https://pypi.org/project/chess/)** library  

Install dependencies with:  
`pip install chess`

---

## How to Run

1. **Clone or download** this repository to your local machine.  
2. **Install** the required packages:  
   `pip install chess`  
3. **Navigate** to the project folder in your terminal.  
4. **Run the main file** (File1) with:  
   `python File1.py`  
5. **Follow the prompts**:
   - Type **white** or **black** to choose your color.  
   - Input moves in [UCI format](https://en.wikipedia.org/wiki/Universal_Chess_Interface), e.g., `e2e4`.  
   - The engine will respond with its best move based on Alpha-Beta search.

---

## Acknowledgments
- **python-chess** library for providing robust move generation and board handling.
- Created as part of an **EPQ**, focusing on fundamental AI search techniques without neural networks.

**Enjoy playing against the custom chess engine!**
