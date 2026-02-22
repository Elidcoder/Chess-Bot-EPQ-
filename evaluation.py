"""
Chess position evaluation using piece-square tables and alpha-beta search.

This module provides position evaluation, move scoring, and the main
alpha-beta search algorithm with quiescence search for tactical moves.
"""

import chess
from typing import Optional
from evaluation_constants import (
    PIECE_SQUARE_VALUES, 
    CHECKMATE_BASE_SCORE, 
    CHECK_BONUS,
    ALPHA_BETA_MIN,
    ALPHA_BETA_MAX
)

def is_tactical_move(board: chess.Board, move: chess.Move) -> bool:
    """Check if a move is tactical (capture or check)."""
    return board.gives_check(move) or board.is_capture(move)

# Evaluation on a single board with no depth
def evaluate_board(board: chess.Board) -> float:
    """
    Evaluate a board position using piece-square tables.
    
    Returns positive values for positions favoring the side to move.
    """
    if not board:
        return 0.0
        
    score = 0.0
    for square, piece in board.piece_map().items():
        if piece in PIECE_SQUARE_VALUES:
            score += PIECE_SQUARE_VALUES[piece].get(square, 0.0)

    # Return score relative to the player whose turn it is
    return score if board.turn else -score

def evaluate_move_on_board(move: chess.Move, board: chess.Board) -> float:
    """
    Evaluate a move's immediate positional impact without deep search.
    
    This is used for move ordering to improve alpha-beta efficiency.
    """
    if not board or move not in board.legal_moves:
        return 0.0
        
    # Apply the move temporarily
    board.push(move)
    
    # Calculate position value (no need for turn adjustment since this is for sorting)
    score = sum(
        PIECE_SQUARE_VALUES.get(piece, {}).get(square, 0.0)
        for square, piece in board.piece_map().items()
    )
    
    # Restore the board
    board.pop()
    return score

def estimate_tactical_move_value(board: chess.Board, move: chess.Move) -> float:
    """
    Get a quick estimate of the value of a tactical move (capture/check).
    
    Used for ordering tactical moves in quiescence search.
    """
    if not board or move not in board.legal_moves:
        return 0.0
        
    score = 0.0

    # Checks are valuable for forcing sequences
    if board.gives_check(move):
        score -= CHECK_BONUS

    # Add capture value (difference between capturing and captured piece values)
    try:
        if board.is_capture(move):
            # Get piece types involved
            capturing_piece_type = board.piece_type_at(move.from_square)
            captured_piece_type = board.piece_type_at(move.to_square)
            
            if capturing_piece_type and captured_piece_type:
                # Simple material difference (capturing lower value with higher is good)
                score += capturing_piece_type - captured_piece_type
                
    except (AttributeError, TypeError):
        # Handle en passant or other special captures
        pass
        
    return score

def alpha_beta(alpha: float, beta: float, board: chess.Board, 
               depth: int, cancel_token: Optional = None) -> float:
    """
    Alpha-beta pruning search algorithm.
    
    Args:
        alpha: Lower bound for search window
        beta: Upper bound for search window  
        board: Current board position
        depth: Remaining search depth
        cancel_token: Threading event for cancellation
        
    Returns:
        Position evaluation score
    """
    # Early return for cancellation
    if cancel_token and cancel_token.is_set():
        return alpha
        
    # Handle terminal positions
    if board.is_game_over():
        outcome = board.outcome()
        if outcome.winner is None:
            return 0.0  # Draw
        # Checkmate - prefer shorter mates
        return (-CHECKMATE_BASE_SCORE + depth) if outcome.winner else (CHECKMATE_BASE_SCORE - depth)
        
    # If we've reached depth limit, start quiescence search
    if depth <= 0:
        return quiescence_search(alpha, beta, board, cancel_token)
    
    # Main alpha-beta search
    for move in board.legal_moves:
        # Check for cancellation during search
        if cancel_token and cancel_token.is_set():
            return alpha
            
        board.push(move)
        score = -alpha_beta(-beta, -alpha, board, depth - 1, cancel_token)
        board.pop()
        
        # Beta cutoff (fail-high)
        if score >= beta:
            return beta
            
        # Update alpha (new best move)
        if score > alpha:
            alpha = score
            
    return alpha

def quiescence_search(alpha: float, beta: float, board: chess.Board, 
                     cancel_token: Optional = None) -> float:
    """
    Quiescence search to avoid horizon effects by examining tactical moves.
    
    Only searches captures and checks to ensure we don't miss immediate tactics.
    """
    # Check for cancellation
    if cancel_token and cancel_token.is_set():
        return alpha
    
    # Get standing pat (current position evaluation)
    standing_pat = evaluate_board(board)
    
    # Beta cutoff - position is already too good
    if standing_pat >= beta:
        return beta
        
    # Update alpha with standing pat
    if alpha < standing_pat:
        alpha = standing_pat

    # Generate and evaluate only tactical moves
    tactical_moves = [
        move for move in board.legal_moves 
        if is_tactical_move(board, move)
    ]
    
    # Sort tactical moves by estimated value for better pruning
    tactical_moves.sort(key=lambda move: estimate_tactical_move_value(board, move))

    # Search tactical moves
    for move in tactical_moves:
        # Check for cancellation
        if cancel_token and cancel_token.is_set():
            return alpha
            
        board.push(move)
        score = -quiescence_search(-beta, -alpha, board, cancel_token)
        board.pop()
        
        # Beta cutoff
        if score >= beta:
            return beta
            
        # Update alpha
        if score > alpha:
            alpha = score
            
    return alpha
