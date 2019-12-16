#!/usr/bin/env python


import argparse
import random
import os

import pyglet
import pygame, time
from pydub.utils import mediainfo
from madmom.features.beats import RNNBeatProcessor, MultiModelSelectionProcessor
from madmom.models import 	BEATS_LSTM

pyglet.options['audio'] = 'pulse'

window = pyglet.window.Window(fullscreen=True)
(maxX, maxY) = window.get_size()
proc2 = RNNBeatProcessor(online=True, nn_files=[BEATS_LSTM[0]])
#proc = RNNBeatProcessor(post_processor=None)
#mm_proc = MultiModelSelectionProcessor(num_ref_predictions=1)
audio = 'audio.wav'
rng = random.SystemRandom()
#predictions = proc(audio)
#final = mm_proc(predictions)

def update_pan_zoom_speeds():
    global _pan_speed_x
    global _pan_speed_y
    global _zoom_speed
    _pan_speed_x = random.randint(-8, 8)
    _pan_speed_y = random.randint(-8, 8)
    _zoom_speed = random.uniform(-0.02, 0.02)
    return _pan_speed_x, _pan_speed_y, _zoom_speed


def update_pan(dt):
    sprite.x += dt * _pan_speed_x
    sprite.y += dt * _pan_speed_y


def update_zoom(dt):
    sprite.scale += dt * _zoom_speed


def update_image(dt):
    img = pyglet.image.load(random.choice(image_paths))
    sprite.image = img
    sprite.scale = get_scale(window, img)
    imgW = img.width * sprite.scale
    if imgW < maxX:
        sprite.position = (maxX/2 - imgW/2, 0)
    else:
        sprite.position = (0, 0)
    update_pan_zoom_speeds()

def update_image2(dt):
    if update_image2.beatsProb[update_image2.i] > update_image2.umbral and time.time()-update_image2.start >=3.0:
        update_image2.start = time.time()
        update_image(dt)
    update_image2.i += 1

update_image2.start = 0
update_image2.i = 0
update_image2.umbral = 0.6
#update_image2.beatsProb = final
update_image2.beatsProb = proc2(audio)

def get_image_paths(input_dir='.'):
    paths = []
    for root, dirs, files in os.walk(input_dir, topdown=True):
        for file in sorted(files):
            if file.endswith(('jpg', 'png', 'gif')):
                path = os.path.abspath(os.path.join(root, file))
                paths.append(path)
    return paths


def get_scale(window, image):
    if image.width > image.height:
        scale = float(window.width) / image.width
    else:
        scale = float(window.height) / image.height
    return scale


@window.event
def on_draw():
    window.clear()
    sprite.draw()

def playMusic():
    audioFile = audio

    info = mediainfo(audioFile)
    frame_rate = info['sample_rate']
    pygame.mixer.init(int(frame_rate))
    pygame.mixer.music.load(audioFile)
    pygame.mixer.music.play()

if __name__ == '__main__':
    _pan_speed_x, _pan_speed_y, _zoom_speed = update_pan_zoom_speeds()

    parser = argparse.ArgumentParser()
    parser.add_argument('imagesDir', help='directory of images')
    parser.add_argument('audioFile', help='audio file')
    args = parser.parse_args()

    image_paths = get_image_paths(args.imagesDir)
    audio = args.audioFile
    #img = pyglet.image.load(random.choice(image_paths))
    img = pyglet.image.load(rng.choice(image_paths))
    sprite = pyglet.sprite.Sprite(img)
    sprite.scale = get_scale(window, img)

    #pyglet.clock.schedule_interval(update_image, 0.5)
    pyglet.clock.schedule_interval(update_image2, 1/100.0)
    pyglet.clock.schedule_interval(update_pan, 1/60.0)
    pyglet.clock.schedule_interval(update_zoom, 1/60.0)

    playMusic()
    pyglet.app.run()
