# Generation ID: Hutch_1763364437558_xuehjrafl (前半)

import sys
from typing import List, Tuple

# 評価表（隅は高評価、Xスクエアは低評価、辺は中評価）
POSITION_VALUES = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

def count_pieces(board: List[List[int]]) -> Tuple[int, int]:
    """黒と白の駒数をカウント"""
    black_count = sum(row.count(1) for row in board)
    white_count = sum(row.count(-1) for row in board)
    return black_count, white_count

def get_valid_moves(board: List[List[int]], player: int) -> List[Tuple[int, int]]:
    """有効な手を全て取得"""
    valid_moves = []
    opponent = -player

    for r in range(8):
        for c in range(8):
            if board[r][c] != 0:
                continue

            for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == opponent:
                    while 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == opponent:
                        nr += dr
                        nc += dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == player:
                        valid_moves.append((r, c))
                        break

    return valid_moves

def apply_move(board: List[List[int]], move: Tuple[int, int], player: int) -> List[List[int]]:
    """手を適用して新しいボードを返す"""
    new_board = [row[:] for row in board]
    r, c = move
    opponent = -player
    new_board[r][c] = player

    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        nr, nc = r + dr, c + dc
        flips = []
        while 0 <= nr < 8 and 0 <= nc < 8 and new_board[nr][nc] == opponent:
            flips.append((nr, nc))
            nr += dr
            nc += dc

        if flips and 0 <= nr < 8 and 0 <= nc < 8 and new_board[nr][nc] == player:
            for fr, fc in flips:
                new_board[fr][fc] = player

    return new_board

def count_stable_stones(board: List[List[int]], player: int) -> int:
    """簡易的な安定石をカウント"""
    stable = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                if (r in [0, 7] and c in [0, 7]) or \
                   (r in [0, 7] and all(board[r][i] == player for i in range(8))) or \
                   (c in [0, 7] and all(board[i][c] == player for i in range(8))):
                    stable += 1
    return stable

def evaluate_board(board: List[List[int]], current_player: int) -> float:
    """ボード評価関数"""
    # current_player: 1=黒(プレイヤー), 2=白(コンピュータ)
    black_idx = 1 if current_player == 1 else -1
    white_idx = -1 if current_player == 1 else 1

    black_count, white_count = count_pieces(board)
    total_pieces = black_count + white_count

    # ゲームフェーズ判定
    if total_pieces < 20:
        phase = "early"
    elif total_pieces < 50:
        phase = "mid"
    else:
        phase = "late"

    # 位置評価
    position_score = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == 1:
                position_score += POSITION_VALUES[r][c]
            elif board[r][c] == -1:
                position_score -= POSITION_VALUES[r][c]

    # 可動性評価
    black_moves = len(get_valid_moves(board, 1))
    white_moves = len(get_valid_moves(board, -1))
    mobility_score = black_moves - white_moves

    # 安定性評価
    black_stable = count_stable_stones(board, 1)
    white_stable = count_stable_stones(board, -1)
    stability_score = black_stable - white_stable

    # 石数差
    piece_diff = black_count - white_count

    # フェーズ別重み付け
    if phase == "early":
        score = 1.0 * position_score + 2.5 * mobility_score
    elif phase == "mid":
        score = 1.0 * position_score + 1.5 * mobility_score + 1.0 * stability_score
    else:  # late
        score = 2.0 * piece_diff + 0.5 * position_score + 1.0 * stability_score

    # コンピュータ視点に変換
    if current_player == 2:
        score = -score

    return score

def minimax(board: List[List[int]], depth: int, current_player: int,
            is_maximizing: bool, alpha: float, beta: float) -> float:
    """ミニマックス法＋αβ枝狩り"""
    if depth == 0:
        return evaluate_board(board, current_player)

    valid_moves = get_valid_moves(board, 1 if is_maximizing else -1)

    if not valid_moves:
        opponent_moves = get_valid_moves(board, -1 if is_maximizing else 1)
        if not opponent_moves:
            return evaluate_board(board, current_player)
        return minimax(board, depth - 1, current_player, not is_maximizing, alpha, beta)

    if is_maximizing:
        max_eval = -sys.maxsize
        for move in valid_moves:
            new_board = apply_move(board, move, 1)
            eval_score = minimax(new_board, depth - 1, current_player, False, alpha, beta)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = sys.maxsize
        for move in valid_moves:
            new_board = apply_move(board, move, -1)
            eval_score = minimax(new_board, depth - 1, current_player, True, alpha, beta)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def choose_best_move(board: List[List[int]], current_player: int, depth: int = 4) -> Tuple[int, int]:
    """最善手を選択（コンピュータ用）"""
    valid_moves = get_valid_moves(board, -1)

    if not valid_moves:
        return None

    best_move = valid_moves[0]
    best_score = -sys.maxsize

    for move in valid_moves:
        new_board = apply_move(board, move, -1)
        score = minimax(new_board, depth - 1, current_player, True, -sys.maxsize, sys.maxsize)

        if score > best_score:
            best_score = score
            best_move = move

    return best_move

# Generation ID: Hutch_1763364437558_xuehjrafl (後半)
