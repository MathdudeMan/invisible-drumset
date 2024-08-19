import pygame
import math
#import pyglet

def hit(tail, head, range):
    # Check head / tail of extremity for drum hit

    isHit = hitCheck(tail, head)

    if isHit:
        mapNum = map(head.x, head.y, range)
        playSound(mapNum)

def hitCheck(tail, head):
    return

def angle(tail, head):
    
    deltaX = tail.x - head.x
    deltaY = tail.y - tail.y
    angle = math.atan2(deltaX, deltaY)
    return angle


def map(x, y, range):
    # Determine region of appendage, indexed 1 - 16
    
    mapNum = 0
    
    # x Check
    if x < range[1]:
        mapNum += 1
    elif x < range[2]:
        mapNum += 2
    elif x < range[3]:
        mapNum += 3
    else:
        mapNum += 4

    # y Check
    if y < range[1]:
        pass
    elif y < range[2]:
        mapNum += 4
    elif y < range[3]:
        mapNum += 8
    else:
        mapNum += 12

    return mapNum


def playSound(mapNum):

    sounds = {
        1: "Cymbal 1",
        2: "Cymbal 2",
        3: "Cymbal 3",
        4: "Cymbal 4",
        5: "Ride",
        6: "Tom 2",
        7: "Tom 1",
        8: "Hi Hat",
        9: "Floor Tom",
        10: "Snare",
        11: "Snare",
        12: "Cowbell",
        13: "Cat",
        14: "BD",
        15: "Floor Hi Hat",
        16: "Whoopie Cushion"
    }

    pygame.mixer.init() #Add to regular file

    pygame.mixer.music.load(sounds[mapNum])
    pygame.mixer.music.play()




