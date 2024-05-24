import pygame.font
from newgame.setting import *
from newgame.level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from newgame.support import *
from newgame.data import Data
from newgame.debug import debug
from newgame.ui import UI
from newgame.overworld import Overworld
import sqlite3

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Game0')
		self.clock = pygame.time.Clock()
		self.import_assets()

		self.ui = UI(self.font, self.ui_frames)
		self.data = Data(self.ui)
		self.tmx_maps = {
			0: load_pygame(join( 'newgame','data', 'levels', 'omni.tmx')),
			1: load_pygame(join('newgame','data', 'levels', '1.tmx')),
			2: load_pygame(join('newgame','data', 'levels', '2.tmx')),
			3: load_pygame(join('newgame','data', 'levels', '3.tmx')),
			4: load_pygame(join('newgame','data', 'levels', '4.tmx')),
			5: load_pygame(join('newgame','data', 'levels', '5.tmx')),
		}
		self.tmx_overworld = load_pygame(join( 'newgame','data', 'overworld', 'overworld.tmx'))
		self.current_stage = Level(self.tmx_maps[0],self.level_frames,self.data,self.switch_stage)

	def switch_stage(self, target, unlock=0):
		if target == 'level':
			self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.data, self.switch_stage)

		else:  # overworld
			if unlock > 0:
				self.data.unlocked_level += 1
			else:
				self.data.health -= 1
			self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)

	def import_assets(self):
		self.level_frames ={
			'flag': import_folder('newgame','graphics', 'level', 'flag'),
			'saw':import_folder('newgame','graphics', 'enemies', 'saw', 'animation'),
			'floor_spike':import_folder('newgame','graphics','enemies','floor_spikes'),
			'palms':import_sub_folders('newgame','graphics','level','palms'),
			'candle':import_folder('newgame','graphics','level','candle'),
			'candle light':import_folder('newgame','graphics','level','candle light'),
			'window':import_folder('newgame','graphics','level','window'),
			'player':import_sub_folders('newgame','graphics','player' ),
			'saw': import_folder('newgame','graphics', 'enemies', 'saw', 'animation'),
			'saw_chain': import_image('newgame','graphics', 'enemies', 'saw','saw_chain'),
			'helicopter':import_folder('newgame','graphics','level','helicopter'),
			'boat': import_folder('newgame','graphics','objects','boat'),
			'spike': import_image('newgame','graphics', 'enemies','spike_ball','Spiked Ball'),
			'spike_chain': import_image('newgame','graphics', 'enemies', 'spike_ball', 'spiked_chain'),
			'tooth':import_folder('newgame','graphics','enemies', 'tooth'),
			'shell': import_sub_folders('newgame','graphics', 'enemies','shell'),
			'pearl':import_image('newgame','graphics','enemies','bullets','pearl'),
			'items': import_sub_folders('newgame','graphics', 'items'),
			'particle': import_folder('newgame','graphics', 'effects', 'particle'),
			'water_top':import_folder('newgame','graphics','level','water','top'),
			'water_body':import_image('newgame','graphics','level','water','body'),
			'bg_tiles': import_folder_dict('newgame','graphics', 'level', 'bg', 'tiles'),
			'cloud_small': import_folder('newgame','graphics', 'level', 'clouds', 'small'),
			'cloud_large': import_image('newgame','graphics', 'level', 'clouds', 'large_cloud'),
		}

		self.font = pygame.font.Font(join('newgame','graphics', 'ui', 'runescape_uf.ttf'),40)
		self.ui_frames = {
			'heart': import_folder('newgame','graphics', 'ui', 'heart'),
			'coin': import_image('newgame','graphics', 'ui', 'coin')
		}
		self.overworld_frames = {
			'palms': import_folder('newgame','graphics', 'overworld', 'palm'),
			'water' : import_folder('newgame','graphics', 'overworld','water'),
			'path': import_folder_dict('newgame','graphics', 'overworld', 'path'),
			'icon': import_sub_folders('newgame','graphics', 'overworld', 'icon'),
		}

	def run(self):
		while True:

			dt = self.clock.tick(60) / 1000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			self.current_stage.run(dt)
			self.ui.update(dt)
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
