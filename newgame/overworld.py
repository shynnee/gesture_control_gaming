import pygame.display
from newgame.setting import *
from newgame.sprites import Sprite,AnimatedSprite,Node,Icon
from newgame.groups import Worldsprites
from random import randint

class Overworld:
    def __init__(self,tmx_map,data,overworld_frames, switch_stage):
        self.screen = pygame.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage

        #groups
        self.all_sprites = Worldsprites(data)
        self.node_sprites = pygame.sprite.Group()

        self.setup(tmx_map,overworld_frames)

        self.current_node = [node for node in self.node_sprites if node.level == 0][0]

        self.create_path_sprites()

    def setup(self, tmx_map, overworld_frames):
        # tiles
        for layer in ['main', 'top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, Z_LAYERS['bg tiles'])

        # water
        for col in range(tmx_map.width):
            for row in range(tmx_map.height):
                AnimatedSprite((col * TILE_SIZE, row * TILE_SIZE), overworld_frames['water'], self.all_sprites, Z_LAYERS['bg'])

        #objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'palm':
                AnimatedSprite((obj.x,obj.y), overworld_frames['palms'], self.all_sprites, Z_LAYERS['main'], randint(4,6))
            else:
                z = Z_LAYERS[f"{'bg details' if obj.name == 'grass' else 'bg tiles'}"]

                Sprite((obj.x,obj.y),obj.image,self.all_sprites,z)
        #paths
        self.paths = {}
        for obj in tmx_map.get_layer_by_name('Paths'):
            pos = [((p.x + TILE_SIZE /2), (p.y + TILE_SIZE /2)) for p in obj.points]
            start = obj.properties['start']
            end = obj.properties['end']
            self.paths[end] = {'pos':pos,'start':start}

        #nodes & player
        for obj in tmx_map.get_layer_by_name('Nodes'):
            #player
            if obj.name == 'Node' and obj.properties['stage'] == self.data.current_level:
                self.icon = Icon((obj.x + TILE_SIZE/2,obj.y + TILE_SIZE/2),self.all_sprites,overworld_frames['icon'])
            #node
            if obj.name == 'Node':
                available_paths = {k:v for k,v in obj.properties.items() if k in ('left','right','up','down')}
                print(available_paths)
                Node(
                    pos = (obj.x,obj.y),
                    surf = overworld_frames['path']['node'],
                    groups = (self.all_sprites, self.node_sprites),
                    level = obj.properties['stage'],
                    data = self.data,
                    paths = available_paths)

    def create_path_sprites(self):
        # get tiles from path
        nodes = {node.level:vt(node.grid_pos) for node in self.node_sprites}
        path_tiles = {}
        for path_id, data in self.paths.items():
            path = data['pos']
            start_node,end_node = nodes[data['start']],nodes[path_id]
            path_tiles[path_id] = [start_node]

            for index, points in enumerate(path):
                if index < len(path) -1:
                    start,end = vt(points), vt(path[index + 1])
                    path_dir = (end - start) / TILE_SIZE
                    start_tile = vt(int(start[0]/TILE_SIZE),int(start[1]/TILE_SIZE))
                    if path_dir.y:
                        dir_y = 1 if path_dir.y > 0 else -1
                        for y in range (dir_y,int(path_dir.y)+dir_y,dir_y):
                            path_tiles[path_id].append(start_tile + vt(0,y))
                    if path_dir.x:
                        dir_x = 1 if path_dir.x > 0 else -1
                        for x in range (dir_x,int(path_dir.x)+dir_y,dir_x):
                            path_tiles[path_id].append(start_tile + vt(x,0))

            path_tiles[path_id].append(end_node)

    def input(self):
        keys = pygame.key.get_pressed()
        if self.current_node and not self.icon.path:
            if self.current_node:
                if keys[pygame.K_s] and self.current_node.can_move('down'):
                    self.move('down')
                if keys[pygame.K_d] and self.current_node.can_move('left'):
                    self.move('left')
                if keys[pygame.K_a] and self.current_node.can_move('right'):
                    self.move('right')
                if keys[pygame.K_w] and self.current_node.can_move('up'):
                    self.move('up')
                if keys[pygame.K_RETURN]:
                    self.data.current_level = self.current_node.level
                    self.switch_stage('level')

    def move(self,direction):
        path_key = int(self.current_node.paths[direction][0])
        path_reverse = True if self.current_node.paths[direction][-1] =='r' else False
        path = self.paths[path_key]['pos'][:] if not path_reverse else self.paths[path_key]['pos'][::-1]
        self.icon.start_move(path)

    def get_current_node(self):
        nodes = pygame.sprite.spritecollide(self.icon, self.node_sprites, False)
        if nodes:
            self.current_node = nodes[0]
    def run(self,dt):
        self.input()
        self.get_current_node()
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.icon.rect.center)