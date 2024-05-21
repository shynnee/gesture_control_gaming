from newgame.setting import *
from os import walk #duyệt qua tất cả các tệp và thư mục trong một cây thư mục
from os.path import join

# Tạo ra một bề mặt từ hình ảnh đc tải lên
def import_image(*path, alpha = True, format = 'png'):#nhận vào một chuỗi đường dẫn và tùy chọn alpha
	full_path = join(*path) + f'.{format}'
	return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path):# tải tất cả hình ảnh từ một thư mục
	frames = []# duyệt hình ảnh và tạo ra danh sách
	for folder_path, subfolders, image_names in walk(join(*path)):
		for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, image_name)
			frames.append(pygame.image.load(full_path).convert_alpha())
	return frames

def import_folder_dict(*path):#trả về một từ điển vs tên tệp là khóa
	frame_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image_name in image_names:
			full_path = join(folder_path, image_name)
			surface = pygame.image.load(full_path).convert_alpha()
			frame_dict[image_name.split('.')[0]] = surface
	return frame_dict

def import_sub_folders(*path):#Hàm này tải tất cả các thư mục con trong thư mục được chỉ định
	frame_dict = {}
	for _, sub_folders, __ in walk(join(*path)):
		if sub_folders:
			for sub_folder in sub_folders:
				frame_dict[sub_folder] = import_folder(*path, sub_folder)
	return frame_dict