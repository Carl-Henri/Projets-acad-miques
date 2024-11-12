############################
#       Slider Module      #
############################

import pygame
from pygame.locals import *

sliders = []

# Class Slider
cur_slider_y = 0
class Slider :
    x = 0

    def __init__(self, interv : tuple, setter, name: str, value):
        global cur_slider_y

        self.interv = interv
        self.value = value
        self.setter = setter
        self.y = cur_slider_y
        cur_slider_y += 23
        self.name = name

    def draw(self, screen, font):
        x,y = self.x, self.y
        pygame.draw.rect(screen,(255,255,255), Rect(x, y, 200, 20), 2)
        pygame.draw.line(screen, (255, 255, 255), (int((self.value)/(self.interv[1]-self.interv[0])*200) + x, y), (int((self.value)/(self.interv[1]-self.interv[0])*200) + x, y + 19))
        self.text = font.render(self.name + " = " + str(self.value), False, (255, 255, 255))
        screen.blit(self.text,(x + 210, self.y+3))

def updateSliders(pos):
    (x,y) = pos
    found = False
    for c in sliders:
        if x > c.x and x <= c.x + 200 and y >= c.y and y <= c.y + 20:
            c.value = x*(c.interv[1]-c.interv[0])/200
            c.setter(x*(c.interv[1]-c.interv[0])/200)
            found = True
            break