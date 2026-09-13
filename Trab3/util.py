import pygame

def singleton(class_):
    instances = {} 
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class EventHandler:
    def __init__(self):
        self.observers = {}

    def subscribe(self, type, callback):
        if type not in self.observers:
            self.observers[type] = []
        self.observers[type].append(callback)

    def notify(self, type, data=None):
        if type in self.observers:
            for o in self.observers[type]:
                o(data)

def colored_sprite(color, size=(32, 32), circle=True):
    sprite = pygame.Surface(size, pygame.SRCALPHA)
    if circle:
        pygame.draw.circle(sprite, color, (size[0]//2, size[1]//2), size[0]//2)
    else:
        sprite.fill(color)
    return sprite

def circle_collistiion(p1, r1, p2, r2):
    euc_distance = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(1/2)
    return euc_distance <= r1 + r2