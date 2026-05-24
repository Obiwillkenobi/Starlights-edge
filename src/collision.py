import pygame
from room import Tile, TILE_SIZE

def get_wall_rects(room):
    walls = []
    for row in range(room.height):
        for col in range(room.width):
            if room.tiles[row][col] == Tile.WALL:
                walls.append(pygame.Rect(
                    room.x + col * TILE_SIZE,
                    room.y + row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                ))
    return walls

def resolve_collision(entity_rect, walls):
    for wall in walls:
        if entity_rect.colliderect(wall):
            # Figure out overlap on each side
            overlap_left = entity_rect.right - wall.left
            overlap_right = wall.right - entity_rect.left
            overlap_top = entity_rect.bottom - wall.top
            overlap_bottom = wall.bottom - entity_rect.top

            # Push out by the smallest overlap
            min_overlap = min(overlap_left, overlap_right,
                              overlap_top, overlap_bottom)

            if min_overlap == overlap_left:
                entity_rect.right = wall.left
            elif min_overlap == overlap_right:
                entity_rect.left = wall.right
            elif min_overlap == overlap_top:
                entity_rect.bottom = wall.top
            elif min_overlap == overlap_bottom:
                entity_rect.top = wall.bottom

    return entity_rect