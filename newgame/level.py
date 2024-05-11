import pygame.sprite
from setting import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Spike, Item, ParticleEffectSprite
from player import Player
from groups import Allsprites
from enemies import Tooth,Shell,Pearl

class Level:
	def __init__(self, tmx_map,level_frames,data):
		self.screen = pygame.display.get_surface()
		self.data = data

		# groups 
		self.all_sprites = Allsprites()
		self.collision_sprites = pygame.sprite.Group()
		self.semi_collision_sprites = pygame.sprite.Group()
		self.damage_sprites = pygame.sprite.Group()
		self.tooth_sprites = pygame.sprite.Group()
		self.pearl_sprites = pygame.sprite.Group()
		self.item_sprites = pygame.sprite.Group()

		self.setup(tmx_map,level_frames)

		# frames
		self.pearl_surf = level_frames['pearl']
		self.particle_frames = level_frames['particle']

	def setup(self, tmx_map,level_frames):
		# tiles
		for layer in ['BG', 'Terrain', 'FG', 'Platforms']:
			for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
				groups = [self.all_sprites]
				if layer == 'Terrain': groups.append(self.collision_sprites)
				if layer == 'Platforms': groups.append(self.semi_collision_sprites)
				match layer:
					case 'BG':
						z = Z_LAYERS['bg tiles']
					case 'FG':
						z = Z_LAYERS['bg tiles']
					case _:
						z = Z_LAYERS['main']

				Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)
		# objects
		for obj in tmx_map.get_layer_by_name('Objects'):
			if obj.name == 'player':
				self.player = Player(
					pos = (obj.x, obj.y),
					groups = self.all_sprites,
					collision_sprites =self.collision_sprites,
					semi_collision_sprites = self.semi_collision_sprites,
				     frames = level_frames['player'],
				     data = self.data)
			else:
				if obj.name in ('barrel','crate'):
					Sprite((obj.x,obj.y), obj.image, (self.all_sprites,self.collision_sprites))
				else:
					# frames
					frames = level_frames[obj.name] if not 'palm' in obj.name else level_frames['palms'][obj.name]
					if obj.name == 'floor_spike' and obj.properties['inverted']:
						frames = [pygame.transform.flip(frame, False, True) for frame in frames]


					AnimatedSprite((obj.x, obj.y), frames, self.all_sprites)

		# moving objects
		for obj in tmx_map.get_layer_by_name('Moving Objects'):
			if obj.name == 'spike':
				Spike(
					pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
					surf=level_frames['spike'],
					radius=obj.properties['radius'],
					speed=obj.properties['speed'],
					start_angle=obj.properties['start_angle'],
					end_angle=obj.properties['end_angle'],
					groups=(self.all_sprites, self.damage_sprites))
				for radius in range(0, obj.properties['radius'], 20):
					Spike(
						pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
						surf=level_frames['spike_chain'],
						radius=radius,
						speed=obj.properties['speed'],
						start_angle=obj.properties['start_angle'],
						end_angle=obj.properties['end_angle'],
						groups=self.all_sprites,
						z=Z_LAYERS['bg details'])

			else:
				frames = level_frames[obj.name]
				groups = (self.all_sprites,self.semi_collision_sprites) if obj.properties['platform'] else (self.all_sprites,self.damage_sprites)
				if obj.width > obj.height:# ngang
					move_dir ='x'
					start_pos =(obj.x,obj.y + obj.height / 2)
					end_pos = (obj.x + obj.width,obj.y + obj.height/2)
				else:
					move_dir = 'y'
					start_pos = (obj.x + obj.width /2, obj.y)
					end_pos = (obj.x + obj.width/2, obj.y + obj.height)
				speed = obj.properties['speed']
				animation_speed = ANIMATION_SPEED if not 'palm' in obj.name else ANIMATION_SPEED + uniform(-1, 1)
				MovingSprite(frames,groups, start_pos, end_pos, move_dir, speed, obj.properties['flip'])

				if obj.name == 'saw':
					if move_dir == 'x':
						y = start_pos[1] - level_frames['saw_chain'].get_height() / 2
						left,right = int(start_pos[0]),int(end_pos[0])
						for x in range (left,right,20):
							Sprite((x,y), level_frames['saw_chain'], self.all_sprites,Z_LAYERS['bg details'])
					else:
						x = start_pos[0] - level_frames['saw_chain'].get_width() / 2
						top,bottom = int(start_pos[1]), int(end_pos[1])
						for y in range(top,bottom, 20):
							Sprite((x, y), level_frames['saw_chain'], self.all_sprites, Z_LAYERS['bg details'])
			#enemies
			for obj in tmx_map.get_layer_by_name('Enemies'):
				if obj.name == 'tooth':
					Tooth((obj.x,obj.y),level_frames['tooth'],(self.all_sprites,self.damage_sprites,self.tooth_sprites),self.collision_sprites)
				if obj.name == 'shell':
					Shell(
						pos=(obj.x,obj.y),
						frames=level_frames['shell'],
						groups=(self.all_sprites,self.collision_sprites),
						reverse=obj.properties['reverse'],
						player=self.player,
						create_pearl=self.create_pearl)
			#items
			for obj in tmx_map.get_layer_by_name('Items'):
				Item(obj.name, (obj.x + TILE_SIZE/2,obj.y), level_frames['items'][obj.name], (self.all_sprites,self.item_sprites),self.data)
	def create_pearl(self,pos,direction):
		Pearl(pos, (self.all_sprites,self.damage_sprites,self.pearl_sprites), self.pearl_surf, direction, 150)

	def pearl_collision(self):
		for sprite in self.collision_sprites:
			sprite = pygame.sprite.spritecollide(sprite,self.pearl_sprites, True)
			if sprite:
				ParticleEffectSprite((sprite[0].rect.center), self.particle_frames, self.all_sprites)

	def hit_collision(self):
		for sprite in self.damage_sprites:
			if sprite.rect.colliderect(self.player.hitbox_rect):
				self.player.get_damage()
				if hasattr(sprite,'pearl'):
					sprite.kill()
					ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)

	def item_collision(self):
		if self.item_sprites:
			item_sprites = pygame.sprite.spritecollide(self.player,self.item_sprites,True)
			if item_sprites:
				item_sprites[0].activate()
				ParticleEffectSprite((item_sprites[0].rect.center),self.particle_frames,self.all_sprites)

	def attack_collision(self):
		for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites():
			facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
							self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
			if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
				target.reversed()

	def run(self, dt):
		self.screen.fill('black')

		self.all_sprites.update(dt)
		self.pearl_collision()
		self.hit_collision()
		self.item_collision()
		self.attack_collision()

		self.all_sprites.draw(self.player.hitbox_rect.center)


