#!/usr/bin/env python

import os
import subprocess

import numpy as np
import pygame as pg


def Fill(Surf, Point, Color, threshold=10):
    import cv2
    arr = pg.surfarray.array3d(Surf)    # copy array from surface
    swapPoint = (Point[1], Point[0])        # swap X and Y
    cv2.floodFill(arr, None, swapPoint, Color, (threshold, threshold, threshold), (threshold, threshold, threshold))
    pg.surfarray.blit_array(Surf, arr)


def draw_color_list(blocksize=10):
    _colour_names = pg.colordict.THECOLORS
    # _colour_sort = sorted(_colour_names, key=lambda name: name[0])
    _colour_sort = sorted(list(_colour_names.keys()))
    ysize = max_map_y - 3 * SIZE
    # print(len(_colour_names))
    idx = 0
    for cname in _colour_sort:
        if cname.startswith('grey'):
            continue
        if cname.startswith('gray'):
            continue
        ccolor = _colour_names[cname]
        posy = (idx * blocksize) % ysize
        posx = int(idx * blocksize / ysize)
        pg.draw.rect(screen, ccolor, pg.Rect(max_map_x + 2 * SIZE + posx * int(SIZE / 4), posy, int(SIZE / 4), blocksize), 0)
        idx += 1


def load_images(image_dir='images', size=50):
    images = []
    images.append(pg.Surface((size, size)))
    for cimagename in os.listdir(image_dir):
        if not cimagename.endswith('.jpg'):
            continue
        cimage = pg.image.load(os.path.join(image_dir, cimagename)).convert()
        cimage = pg.transform.scale(cimage, (size, size))
        images.append(cimage)
    return images


def draw_color_pallette(sat=255, size=50):
    for x, r in enumerate(np.arange(0, sat, sat / (size * 2))):
        for y, g in enumerate(np.arange(0, sat, sat / (size * 2))):
            r = int(round(r))
            g = int(round(g))
            b = sat - (r + g)
            if b > 255:
                b = int(255)
            if b < 0:
                b = 0
            ccolor = pg.Color(r, g, b, 255)
            screen.set_at((x + max_map_x + 2 * size, y), ccolor)


def color_dist(color1, color2):
    return (color1.r - color2.r)**2 + (color1.g - color2.g)**2 + (color1.b - color2.b)**2


def replace_color(img, orig_color, new_color, dist=4):
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            ccolor = img.get_at((x, y))
            # new_color.a = ccolor.a  # Preserve the alpha value.
            if color_dist(ccolor, orig_color) < dist:
                # print(ccolor)
                img.set_at((x, y), new_color)  # Set the color of the pixel.


pg.init()
pg.font.init()

# tile size for main design
SIZE = 30
# number of tiles on screen in each axis
num_tiles = 23
# threshold for adaptive fill
threshold = 10


# 1000 * 1000 is main screen, then 2 * SIZE blocks, then color pallette
# max_map_x = int(22.5 * SIZE)
max_map_x = int(num_tiles * SIZE)
max_map_y = int(num_tiles * SIZE)
tiles = np.zeros((num_tiles, num_tiles), dtype=int)
rotations = np.zeros((num_tiles, num_tiles))
screen = pg.display.set_mode((max_map_x + 4 * SIZE, max_map_y + SIZE))
clock = pg.time.Clock()
BG_COLOR = pg.Color('black')
selected_color = BG_COLOR
images = load_images('images', SIZE)
orig_images = [x.copy() for x in images]
print('loaded %d images' % len(images))
img = images[0]

# create the room scheme
room = pg.Surface((1000, 1000), pg.SRCALPHA)
pg.draw.polygon(room, (255, 255, 255), ((0, 0), (22.5 * SIZE, 0), (22.5 * SIZE, 14 * SIZE), (18 * SIZE, 14 * SIZE), (18 * SIZE, 22 * SIZE), (0, 22 * SIZE)), 2)
pg.draw.line(room, (255, 255, 255), (3 * SIZE, 0), (3 * SIZE, 22 * SIZE), 2)
pg.draw.line(room, (255, 255, 255), (18 * SIZE, 0), (18 * SIZE, 22 * SIZE), 2)

screen.fill(BG_COLOR)

# the font for showing the adaptive threshold for floodfill
myfont = pg.font.SysFont('Comic Sans MS', 20)
textsurface = myfont.render('%s' % threshold, False, (0, 0, 0))

# draw the tile list
for idx, cimage in enumerate(images):
    cy = idx % num_tiles
    cx = int(idx / num_tiles)
    screen.blit(cimage, (max_map_x + cx * SIZE, cy * SIZE))
    # screen.blit(cimage, (max_map_x, idx * SIZE))

draw_color_list()

# draw_color_pallette(size=SIZE)
pg.display.flip()

print('keyboard shortcuts:')
print('r to reset current tile to loaded image')
print('f to fill all blank tiles with current image')
print('left/right to rotate current tile')
print('up/down to select next/prev tile')
print('space to redraw with modified tiles')
print('d/e to increase/decrease fill threshold')
print('to fill a tile, select it, select a color and then click inside the tile. use r if did a mistake')

done = False
rotation = 0
cimagenum = 0
cimage = images[cimagenum]
draw_select = True
while not done:
    redraw = False
    draw_color = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN:
            draw_select = True
            if event.key == pg.K_r:
                print('reset tile')
                images[cimagenum] = orig_images[cimagenum].copy()
                cimage = images[cimagenum]
                draw_select = True
            if event.key == pg.K_f:
                for cx in range(tiles.shape[0]):
                    for cy in range(tiles.shape[1]):
                        if tiles[cx, cy] == 0:
                            tiles[cx, cy] = cimagenum
                            rotations[cx, cy] = rotation
                redraw = True
            if event.key == pg.K_SPACE:
                redraw = True
            if event.key == pg.K_s:
                a = subprocess.run(['python', 'file_dlg.py', '--save'], capture_output=True)
                if a.returncode == 0:
                    filepath = a.stdout.decode().strip()
                    np.savez(filepath, tiles=tiles, rotations=rotations)
                    print('saved')
            if event.key == pg.K_l:
                a = subprocess.run(['python', 'file_dlg.py'], capture_output=True)
                if a.returncode == 0:
                    filepath = a.stdout.decode().strip()
                    fl = np.load(filepath)
                    print(fl)
                    print(fl.files)
                    tiles = fl['tiles']
                    rotations = fl['rotations']
                    print('loaded')
                    redraw = True
            if event.key == pg.K_UP:
                cimagenum += 1
                cimagenum = cimagenum % len(images)
                cimage = images[cimagenum]
            if event.key == pg.K_DOWN:
                cimagenum -= 1
                cimagenum = cimagenum % len(images)
                cimage = images[cimagenum]
            if event.key == pg.K_RIGHT:
                rotation = (rotation - 90) % 360
                cimage = pg.transform.rotate(images[cimagenum], rotation)
            if event.key == pg.K_LEFT:
                rotation = (rotation + 90) % 360
                cimage = pg.transform.rotate(images[cimagenum], rotation)
            if event.key == pg.K_d:
                threshold = threshold - 1
                draw_color = True
            if event.key == pg.K_e:
                threshold = threshold + 1
                draw_color = True
        elif pg.mouse.get_pressed()[0]:
            pos = pg.mouse.get_pos()
            if pos[0] < max_map_x:
                tile_x = round(pos[0] / SIZE - 0.5)
                tile_y = round(pos[1] / SIZE - 0.5)
                tiles[tile_x, tile_y] = cimagenum
                rotations[tile_x, tile_y] = rotation
                rxpos = tile_x * SIZE
                rypos = tile_y * SIZE
                screen.blit(cimage, (rxpos, rypos))
            elif pos[0] < max_map_x + SIZE * 2:
                    cx = round((pos[0] - max_map_x) / SIZE - 0.5)
                    cy = round(pos[1] / SIZE - 0.5)
                    newnum = cy + cx * num_tiles
                    # newnum = round(pos[1] / SIZE - 0.5)
                    if newnum <= len(images):
                        cimagenum = newnum
                        cimage = images[cimagenum]
                        rotation = 0
                    draw_select = True
            else:
                # selected a color
                if pos[1] <= max_map_y - 3 * SIZE:
                    selected_color = screen.get_at(pos)
                    draw_color = True
                # clicked on the selected zoomed tile - change color
                else:
                    cimage = images[cimagenum]
                    ipos = [pos[0], pos[1]]
                    ipos[0] = ipos[0] - max_map_x - 2 * SIZE
                    ipos[0] = int(ipos[0] / 2)
                    ipos[1] = ipos[1] - (max_map_y - 2 * SIZE)
                    ipos[1] = int(ipos[1] / 2)
                    # Fill(cimage, ipos, selected_color, threshold=threshold)
                    replace_color(cimage, screen.get_at(pos), selected_color)
                    draw_select = True
        if draw_color:
            pg.draw.rect(screen, selected_color, pg.Rect(max_map_x + 2 * SIZE, max_map_y - 3 * SIZE, 2 * SIZE, SIZE), 0)
            textsurface = myfont.render('%s' % threshold, False, (0, 0, 0))
            screen.blit(textsurface, (max_map_x + 2.5 * SIZE, max_map_y - 3 * SIZE))
        if draw_select:
            # prepare the zoomed selected image (rotation etc.)
            timage = cimage
            timage = pg.transform.scale(timage, (SIZE * 2, SIZE * 2))
            # draw the zoomed selected image
            screen.blit(timage, (max_map_x + 2 * SIZE, max_map_y - SIZE * 2))
            draw_select = False
        if redraw:
            print('redraw')
            # screen.fill(BG_COLOR)
            for cx in range(tiles.shape[0]):
                for cy in range(tiles.shape[1]):
                    ttimage = images[tiles[cx, cy]]
                    ttimage = pg.transform.rotate(ttimage, rotations[cx, cy])
                    screen.blit(ttimage, (cx * SIZE, cy * SIZE))
            redraw = False
        # overlay the room scheme
        screen.blit(room, (0, 0))
        pg.display.flip()
    # screen.fill(BG_COLOR)
    # screen.blit(img, (200, 200))
    # pg.display.flip()
    clock.tick(60)
