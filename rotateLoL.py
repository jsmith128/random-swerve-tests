from pygame import Vector2
import pygame

import math

WIDTH = 888*2
HEIGHT = 360*2


class Field:
    def __init__(self):
        self.width = 888
        self.height = 360
        self.image = pygame.image.load(r"C:\Users\Jon\Desktop\chimeras\asteria swerve test\frc2024-sliced.png")
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))

    def draw(self, screen):
        screen.blit(self.image, (0,0))

class Robot:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.yaw = 0
        self.width = 21
        self.alliance = 0 # 0= blue; 1= red

        self.image = pygame.image.load(r"C:\Users\Jon\Desktop\chimeras\asteria swerve test\robot.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width*2, self.width*2))
        self.rotated_image = self.image

        self.rect = self.image.get_rect()
        
        

    def draw(self, screen):
        self.rect.center = (self.x, self.y)
        self.rect = self.rotated_image.get_rect(center=self.rect.center)
        self.rotated_image = pygame.transform.rotate(self.image, self.yaw)
    
        screen.blit(self.rotated_image, self.rect)

        pygame.draw.circle(screen, "red", (self.x, self.y), 10)

    def move(self, x, y):
        self.x += x
        self.y += y

        x = self.x/2 - (888/2)
        y = -(self.y/2 - (360/2))
        print(x, y)
        if (self.alliance == 1):
            self.yaw = -math.atan((y - 56.75) / (327.125 - x))
            self.yaw *= 180/math.pi
        else:
            self.yaw = math.atan((y - 56.75) / (327.125 + x))
            self.yaw = (self.yaw * 180/math.pi) - 180


        



def extendPoint(x0,y0,x1,y1,length):
    dt = length
    d = -math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
    if (d!=0):
        t = dt/d
    else:
        t = 0
    return Vector2(((1 - t) * x0 + t * x1), ((1 - t) * y0 + t * y1))




# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

# CLASSES
robot = Robot()
field = Field()

# INPUT
js = pygame.joystick.Joystick(0)
js.init()

# CONSTANTS
CENTER = Vector2(screen.get_width() /2, screen.get_height() /2)




circleWidth = 200
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30)
while running:
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if (js.get_button(2)):
        robot.alliance = 0
    elif (js.get_button(1)):
        robot.alliance = 1

    movx = js.get_axis(0)
    movy = js.get_axis(1)

    if (abs(movx)>0.05 or abs(movy)>0.05):
        robot.move(movx*5**2, movy*5**2)

    screen.fill("grey")

    # RENDER YOUR GAME HERE
    field.draw(screen)
    robot.draw(screen)

    

    pygame.display.flip()

    clock.tick(60)

pygame.joystick.quit()
pygame.quit()