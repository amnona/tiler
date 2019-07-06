#!/usr/bin/env python

import os

import numpy as np
import pygame as pg


def load_images(image_dir='images', size=50):
    images = []
    for cimagename in os.listdir(image_dir):
        if not cimagename.endswith('.jpg'):
            continue
        cimage = pg.image.load(os.path.join(image_dir, cimagename))
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


def replace_color(img, orig_color, new_color, dist=50):
    print(new_color)
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            ccolor = img.get_at((x, y))
            new_color.a = ccolor.a  # Preserve the alpha value.
            if color_dist(ccolor, orig_color) < dist:
                # print(ccolor)
                img.set_at((x, y), new_color)  # Set the color of the pixel.


pg.init()
SIZE = 40
# 1000 * 1000 is main screen, then 2 * SIZE blocks, then color pallette
max_map_x = int(22.5 * SIZE)
max_map_y = int(22 * SIZE)
screen = pg.display.set_mode((max_map_x + 4 * SIZE, max_map_y + SIZE))
clock = pg.time.Clock()
BG_COLOR = pg.Color('black')
selected_color = BG_COLOR
images = load_images('images', SIZE)
print('loaded %d images' % len(images))
img = images[0]

# create the room scheme
room = pg.Surface((1000, 1000), pg.SRCALPHA)
pg.draw.polygon(room, (255, 255, 255), ((0, 0), (22.5 * SIZE, 0), (22.5 * SIZE, 14 * SIZE), (18 * SIZE, 14 * SIZE), (18 * SIZE, 22 * SIZE), (0, 22 * SIZE)), 2)
pg.draw.line(room, (255, 255, 255), (3 * SIZE, 0), (3 * SIZE, 22 * SIZE), 2)
pg.draw.line(room, (255, 255, 255), (18 * SIZE, 0), (18 * SIZE, 22 * SIZE), 2)

screen.fill(BG_COLOR)

# draw the tile list
for idx, cimage in enumerate(images):
    screen.blit(cimage, (max_map_x, idx * SIZE))
draw_color_pallette(size=SIZE)
pg.display.flip()

done = False
rotation = 0
cimagenum = 0
cimage = images[cimagenum]
draw_select = True
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN:
            draw_select = True
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
        elif pg.mouse.get_pressed()[0]:
            pos = pg.mouse.get_pos()
            if pos[0] < max_map_x:
                rxpos = round(pos[0] / SIZE - 0.5) * SIZE
                rypos = round(pos[1] / SIZE - 0.5) * SIZE
                screen.blit(cimage, (rxpos, rypos))
            elif pos[0] < max_map_x + SIZE * 2:
                    newnum = round(pos[1] / SIZE - 0.5)
                    if newnum <= len(images):
                        cimagenum = newnum
                        cimage = images[cimagenum]
                        rotation = 0
                    draw_select = True
            else:
                # selected a color
                if pos[1] <= 2 * SIZE:
                    selected_color = screen.get_at(pos)
                    pg.draw.rect(screen, selected_color, pg.Rect(max_map_x + 2 * SIZE, 4 * SIZE, 2 * SIZE, 2 * SIZE),0)
                # clicked on the selected zoomed tile - change color
                else:
                    cimage = images[cimagenum]
                    replace_color(cimage, screen.get_at(pos), selected_color)
                    draw_select = True
        if draw_select:
            # prepare the zoomed selected image (rotation etc.)
            timage = cimage
            timage = pg.transform.scale(timage, (SIZE * 2, SIZE * 2))
            # draw the zoomed selected image
            screen.blit(timage, (max_map_x + 2 * SIZE, max_map_y - SIZE * 2))
            draw_select = False
        # overlay the room scheme
        screen.blit(room, (0, 0))
        pg.display.flip()
    # screen.fill(BG_COLOR)
    # screen.blit(img, (200, 200))
    # pg.display.flip()
    clock.tick(60)
