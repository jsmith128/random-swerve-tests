import math

class Pod:
    speed = 0
    angle = 0

    currentAngle = 0

    def set(self, speed, angle):
        angle *= 360
        self.currentAngle = math.remainder(angle, 360)

class Chassis:
    def __init__(self, pod1:Pod, pod2:Pod, pod3:Pod, pod4:Pod):
        self.pod1 = pod1
        self.pod2 = pod2
        self.pod3 = pod3
        self.pod4 = pod4
    
    yaw = 0
    straightYaw = 0

    isRotating = False

    width = 21
    length = 21


    def move(self, speed, rotate, strafe):

        angle = self.yaw
        angle = math.remainder(angle, 360.0)

        angle = angle * (math.pi/180.0)

        speed = speed * math.cos(angle) + strafe * math.sin(angle)
        strafe = strafe * math.cos(angle) - speed * math.sin(angle)


        a = (strafe - rotate) * (self.length / self.width)
        b = (strafe + rotate) * (self.length / self.width)
        c = (speed  - rotate) * (self.width  / self.length)
        d = (speed  + rotate) * (self.width  / self.length)

        self.pod1.angle = math.atan2(b, d) * 0.5 / math.pi
        self.pod2.angle = math.atan2(b, c) * 0.5 / math.pi
        self.pod3.angle = math.atan2(a, d) * 0.5 / math.pi
        self.pod4.angle = math.atan2(a, c) * 0.5 / math.pi    

        maxWheelSpeed = max(
                self.pod1.speed,
                self.pod2.speed,
                self.pod3.speed,
                self.pod4.speed)
        if (maxWheelSpeed > 1.0):
            self.pod1.speed /= maxWheelSpeed
            self.pod2.speed /= maxWheelSpeed
            self.pod3.speed /= maxWheelSpeed
            self.pod4.speed /= maxWheelSpeed
        
        self.pod1.set(self.pod1.speed, self.pod1.angle)
        self.pod2.set(self.pod2.speed, self.pod2.angle)
        self.pod3.set(self.pod3.speed, self.pod3.angle)
        self.pod4.set(self.pod4.speed, self.pod4.angle)

class DriveTrain:
    def __init__(self, joystick):
        self.js = joystick

    pod1 = Pod()
    pod2 = Pod()
    pod3 = Pod()
    pod4 = Pod()
    pods = [pod1,pod2,pod3,pod4]

    chassis = Chassis(pod2, pod1, pod4, pod3)

    speed = 0 
    strafe = 0
    rotate = 0
    rotateTimer = 0

    def exponentialInput(self):
        joyLDeadBandHigh = 1 # Limit for linear speed
        joyLDeadBandLow = 0.1
        joyRDeadBandHigh = 1.0 # Limit for rotate speed
        joyRDeadBandLow = 0.1
        leftStickMag = math.sqrt(self.speed*self.speed + self.strafe*self.strafe)
        rightStickMag = abs(self.rotate)

        allowedLJoyRange = joyLDeadBandHigh - joyLDeadBandLow
        allowedRJoyRange = joyRDeadBandHigh - joyRDeadBandLow

        if(leftStickMag > joyLDeadBandLow):
            normalizeLeftStickMag = min(1.0, (leftStickMag - joyLDeadBandLow)/allowedLJoyRange)
            leftJoyScale = normalizeLeftStickMag / leftStickMag

            self.speed *= leftJoyScale
            self.strafe *= leftJoyScale
        else:   
            self.speed = 0
            self.strafe = 0
        
        #quesocason was here
        if(rightStickMag > joyRDeadBandLow):
           normalizeRightStickMag = min(1.0,  (rightStickMag - joyRDeadBandLow)/allowedRJoyRange)
           rightJoyScale = normalizeRightStickMag / rightStickMag

           self.rotate *= rightJoyScale
        else:
            self.rotate = 0
        

        if (abs(self.speed) + abs(self.strafe) > 1):
            corner = abs(self.speed) + abs(self.strafe)

            self.speed *= corner
            self.strafe *= corner

        driveScalingExponent = 3
        rotateScalingExponent = 1 # Since rotate cap is 25%, don't do a full sq or cubed input.
        self.rotate *= 0.25
        self.speed = math.pow(abs(self.speed) , driveScalingExponent) * math.copysign( 1, self.speed)
        self.rotate = math.pow(abs(self.rotate) , rotateScalingExponent) * math.copysign(1, self.rotate)
        self.strafe = math.pow(abs(self.strafe) , driveScalingExponent) * math.copysign(1, self.strafe)
    
    def teleop(self):
        self.speed = self.js.get_axis(1)
        self.strafe = self.js.get_axis(0)
        self.rotate = self.js.get_axis(2)

        self.exponentialInput()
        # print(round(self.speed,5), round(self.strafe,5))

        yawCorrection = 0

        if (self.rotate == 0):
            if (self.chassis.isRotating):
                self.rotateTimer += 1
                if (self.rotateTimer > 10):
                    self.chassis.straightYaw = self.chassis.yaw
                    self.chassis.isRotating = False
                    self.rotateTimer = 0
            elif (self.speed != 0 or self.strafe != 0):
                pass
                #yawCorrection = self.chassis.calcYawCorrection(self.chassis.straightYaw, self.chassis.yawStraightkP)    
        else:
            self.chassis.isRotating = True
        
        self.chassis.move(self.speed, self.rotate - yawCorrection, self.strafe)
        print(self.pod1.currentAngle)



from pygame import Vector2
import pygame

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
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
js = pygame.joystick.Joystick(0)
js.init()

drivetrain = DriveTrain(js)
center = Vector2(screen.get_width() /2, screen.get_height() /2)

botWidth = 200
wheelWidth = 75
cornerTL = Vector2(center.x-botWidth, center.y-botWidth)
cornerTR = Vector2(center.x+botWidth, center.y-botWidth)
cornerBL = Vector2(center.x-botWidth, center.y+botWidth)
cornerBR = Vector2(center.x+botWidth, center.y+botWidth)
corners = [cornerTL,cornerTR,cornerBL,cornerBR]
while running:
    drivetrain.teleop()

    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("grey")

    # RENDER YOUR GAME HERE

    #robot body
    pygame.draw.rect(screen, (20,20,70), pygame.Rect(center.x-botWidth,center.y-botWidth,botWidth*2, botWidth*2))
    #robot wheels
    for coord in corners:
        pygame.draw.circle(screen, (0,0,0), coord, wheelWidth)

    # draw pod angles
    for i in range(0,4):
        podAngle = drivetrain.pods[i].currentAngle
        print(podAngle)
        endpoint = Vector2(corners[i].x - wheelWidth*(math.cos(podAngle/50)), 
                           corners[i].y - wheelWidth*(math.sin(podAngle/50))
                        )
        pygame.draw.line(screen, (0,0,200), corners[i], endpoint, 4)



    pygame.display.flip()
    clock.tick(50)

pygame.joystick.quit()
pygame.quit()