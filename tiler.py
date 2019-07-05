#!/usr/bin/env python

import pygame as pg
import os


def load_images(image_dir='images', size=50):
    images = []
    for cimagename in os.listdir(image_dir):
        if not cimagename.endswith('.jpg'):
            continue
        cimage = pg.image.load(os.path.join(image_dir, cimagename))
        cimage = pg.transform.scale(cimage, (size, size))
        images.append(cimage)
    return images


pg.init()
screen = pg.display.set_mode((1200, 1000))
clock = pg.time.Clock()
BG_COLOR = pg.Color('gray12')
SIZE = 50
images = load_images('images', SIZE)
print('loaded %d images' % len(images))
img = images[0]
# img = pg.Surface((150, 150), pg.SRCALPHA)
# pg.draw.polygon(img, (0, 100, 200), ((75, 0), (150, 75), (75, 150), (0, 75)))
screen.fill(BG_COLOR)
for idx, cimage in enumerate(images):
    screen.blit(cimage, (1000, idx * SIZE))
pg.display.flip()


def set_color(img, color):
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            color.a = img.get_at((x, y)).a  # Preserve the alpha value.
            img.set_at((x, y), color)  # Set the color of the pixel.


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
            if event.key == pg.K_j:
                set_color(img, pg.Color(255, 0, 0))
            elif event.key == pg.K_h:
                set_color(img, pg.Color(0, 100, 200))
        elif event.type == pg.MOUSEBUTTONUP:
            pos = pg.mouse.get_pos()
            if pos[0] < 1000:
                rxpos = round(pos[0] / SIZE - 0.5) * SIZE
                rypos = round(pos[1] / SIZE - 0.5) * SIZE
                screen.blit(cimage, (rxpos, rypos))
            else:
                cimagenum = round(pos[1] / SIZE - 0.5)
                cimage = images[cimagenum]
                draw_select = True
        if draw_select:
            timage = cimage
            timage = pg.transform.scale(timage, (SIZE * 2, SIZE * 2))
            screen.blit(timage, (1200 - SIZE * 2, 1000 - SIZE * 2))
            draw_select = False
        pg.display.flip()
    # screen.fill(BG_COLOR)
    # screen.blit(img, (200, 200))
    # pg.display.flip()
    clock.tick(60)
