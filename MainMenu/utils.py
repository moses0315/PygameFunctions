def manhattan_distance(start, goal):
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

def can_move_diagonal(tile_map, current, row_offset, col_offset):
    row_check = current[1] + row_offset
    col_check = current[0] + col_offset

    if (
        row_check < 0 or row_check >= len(tile_map.tile_map) - 1 or
        col_check < 0 or col_check >= len(tile_map.tile_map[0]) - 1
    ):
        return False

    if tile_map.is_obstacle(col_check, row_check) or tile_map.is_obstacle(col_check, row_check + 1):
        return False
    if tile_map.is_obstacle(current[0], row_check) or tile_map.is_obstacle(current[0], row_check + 1):
        return False
    if tile_map.is_obstacle(col_check, current[1]) or tile_map.is_obstacle(col_check, current[1] + 1):
        return False

    return True
