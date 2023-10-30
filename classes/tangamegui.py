#!/usr/bin/env python3

import time
try:
    import numpy as np
except:
    print("Numpy should be installed. pip install numpy")
    raise ImportError
try:
    import pygame
except:
    print("Pygame should be installed. pip install pygame")
    raise ImportError


class Bar:
    inner_color = (250,250,250)
    border_color = (200,200,200)
    border_width = 2
    border_radius = 5
    visibility = True

    def function(self): pass

    def __init__(self,x=0,y=0,width=20,height=90,ylim=360):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ylim = ylim

    def checkHover(self,ball):
        return (self.x-self.width//2 < ball.x-ball.radius < self.x+self.width//2 and(self.y-self.height//2 < ball.y-ball.radius < self.y+self.height//2 or self.y-self.height//2 < ball.y+ball.radius < self.y+self.height//2))or(self.x-self.width//2 < ball.x+ball.radius < self.x+self.width//2 and(self.y-self.height//2 < ball.y-ball.radius < self.y+self.height//2 or self.y-self.height//2 < ball.y+ball.radius < self.y+self.height//2))

    def toggle(self):
        self.visibility = not self.visibility

    def posScale(self,scalex,scaley):
        self.x = scalex*self.x
        self.y = scaley*self.y

    def sety(self,y):
        self.y = max(min(y,self.ylim-self.height//2),self.height//2)

    def setColor(self,color):
        self.inner_color = color

    def draw(self,surface):
        if self.visibility:
            pygame.draw.rect(surface,self.inner_color,(self.x-self.width//2,self.y-self.height//2,self.width,self.height),border_radius=self.border_radius)
            pygame.draw.rect(surface,self.border_color,(self.x-self.width//2,self.y-self.height//2,self.width,self.height),width=self.border_width,border_radius=self.border_radius)

class Ball:
    inner_color = (200,200,200)
    border_radius = 2
    visibility = True

    def function(self): pass

    def __init__(self,x=0,y=0,radius=10,vel=np.array([3,3]),xlim=640,ylim=360):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel = vel
        self.speed = np.sqrt(vel.dot(vel))
        self.xlim = xlim
        self.ylim = ylim

    def getPos4CheckHover(self,pos):
        _pos = np.array(pos)
        _pos = _pos/np.sqrt(_pos.dot(_pos))
        return _pos*self.radius
    
    def checkOutOfBounds(self):
        return self.x < self.radius or self.x > self.xlim-self.radius

    def toggle(self):
        self.visibility = not self.visibility

    def posScale(self,scalex,scaley):
        self.x = scalex*self.x
        self.y = scaley*self.y

    def setPos(self,pos):
        self.x,self.y = pos[0],pos[1]

    def setVel(self,vel):
        self.vel = vel
        self.speed = np.sqrt(vel.dot(vel))

    def update(self):
        self.x += self.vel[0]
        if self.y > self.ylim-self.radius or self.y < self.radius:
            self.vel[1] = -self.vel[1]
        self.y += self.vel[1]

    def setColor(self,color):
        self.inner_color = color

    def draw(self,surface):
        if self.visibility:
            pygame.draw.rect(surface,self.inner_color,(self.x-self.radius,self.y-self.radius,self.radius*2,self.radius*2),border_radius=self.border_radius)