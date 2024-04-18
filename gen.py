import os
import hashlib
import numpy as np
from PIL import Image, ImageDraw

class Generator:
    class Constants:
        BLOCK_ROW = 5
        BLOCK_ROW_HALF = BLOCK_ROW // 2 + 1
        BLOCK_WIDTH = 70
        REMAINS_WIDTH = 35
        IMAGE_WIDTH = REMAINS_WIDTH * 2 + BLOCK_WIDTH * BLOCK_ROW
        IMAGE_HEIGHT = REMAINS_WIDTH * 2 + BLOCK_WIDTH * BLOCK_ROW
        BACKGROUND_COLOR = (230, 230, 230)

    class AvatarInfo:
        def __init__(self, color):
            self.color = color
            self.blocks = [False] * (Generator.Constants.BLOCK_ROW * Generator.Constants.BLOCK_ROW)

        def set_block_value(self, index, value):
            self.blocks[index] = value

        def get_block_value(self, index):
            return self.blocks[index]

        def get_color(self):
            return self.color

    def __init__(self):
        self.count = 0

    def next_avatar(self, seed):
        avatar_info = self.next_avatar_info(seed)
        buffered_image = Image.new('RGB', (Generator.Constants.IMAGE_WIDTH, Generator.Constants.IMAGE_HEIGHT), Generator.Constants.BACKGROUND_COLOR)

        for i in range(buffered_image.height):
            for j in range(buffered_image.width):
                buffered_image.putpixel((i, j), Generator.Constants.BACKGROUND_COLOR)

        count = 0
        for i in range(Generator.Constants.BLOCK_ROW_HALF):
            for j in range(Generator.Constants.BLOCK_ROW):
                if not avatar_info.get_block_value(count):
                    count += 1
                    continue
                self.fill_image_block(buffered_image, i, j, avatar_info.get_color())
                self.fill_image_block(buffered_image, Generator.Constants.BLOCK_ROW - 1 - i, j, avatar_info.get_color())
                count += 1

        return buffered_image

    def fill_image_block(self, buffered_image, row, col, color):
        pixel_row_start = Generator.Constants.REMAINS_WIDTH + row * Generator.Constants.BLOCK_WIDTH
        pixel_col_start = Generator.Constants.REMAINS_WIDTH + col * Generator.Constants.BLOCK_WIDTH
        for i in range(pixel_row_start, pixel_row_start + Generator.Constants.BLOCK_WIDTH):
            for j in range(pixel_col_start, pixel_col_start + Generator.Constants.BLOCK_WIDTH):
                buffered_image.putpixel((i, j), color)

    def next_avatar_info(self, seed):
        hash_bytes = self.next_hash(seed)

        # 3 byte for color, 15 byte for block
        info = np.zeros(18, dtype=int)
        for i in range(len(hash_bytes)):
            index = i % 18
            info[index] = (info[index] + (hash_bytes[i] + 128)) % 256

        avatar_info = self.AvatarInfo((info[0], info[1], info[2]))
        for i in range(3, 18):
            avatar_info.set_block_value(i, info[i] > 127)
        return avatar_info

    def next_hash(self, seed):
        message_digest = hashlib.sha256()
        message_digest.update((seed + str(self.count)).encode('utf-8'))
        self.count += 1
        return message_digest.digest()

if not os.path.exists('./avatars'):
    os.makedirs('./avatars')

generator = Generator()
num_iterations = 30 
for i in range(num_iterations):
    seed = ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz0123456789'), size=10))
    avatar = generator.next_avatar(seed)
    avatar_path = os.path.join('avatars', f'avatar_{i}.png')
    avatar.save(avatar_path)
    print(f"Avatar {i+1}/{num_iterations} saved at: {avatar_path}")
