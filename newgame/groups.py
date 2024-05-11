import pygame.sprite
from setting import *

class Allsprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen =  pygame.display.get_surface()
        self.offset = vt() # biểu diễn câc vt của sprite

    def draw(self,target_pos):# vị trí nhân vật
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH/2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT/ 2)

        for sprite in sorted(self,key=lambda sprite: sprite.z):# duyệt và sắp xếp các sprite theo gtri z
            offset_pos = sprite.rect.topleft + self.offset
            self.screen.blit(sprite.image,offset_pos)