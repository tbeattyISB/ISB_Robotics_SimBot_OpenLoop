import pygame
import math
from threading import Thread, Timer
from sys import exit

displayw = 800
displayh = 600
wallPos = 700
simSpeed = 40


class Graph(object):
    def __init__(self, window):
        self.window = window
        self.data = [wallPos];
        self.xScale = 0.0004 * math.pow(simSpeed, 2) - 0.0637 * simSpeed + 3.15
        self.yScale = 0.1
        self.timeScale = 0.075

    def showGraph(self):
        myfont = pygame.font.SysFont('Aerial', 20)
        pygame.draw.line(self.window, (100, 100, 100), (30, 500), (750, 500))
        textsurface = myfont.render('Sensor', True, (0, 0, 0))
        textsurface = pygame.transform.rotate(textsurface, 90)
        self.window.blit(textsurface, (30, 400))
        pygame.draw.line(self.window, (100, 100, 100), (50, 400), (50, 520))
        textsurface = myfont.render('Time', True, (0, 0, 0))
        self.window.blit(textsurface, (600, 510))
        pygame.draw.line(self.window, (150, 150, 255), (50, 500 - 700 * self.yScale),
                         (2000 * self.timeScale, 500 - 700 * self.yScale), 3)
        pygame.draw.line(self.window, (150, 150, 255), (2000 * self.timeScale, 500 - 700 * self.yScale),
                         (2000 * self.timeScale, 500 - 300 * self.yScale),
                         3)
        pygame.draw.line(self.window, (150, 150, 255), (2000 * self.timeScale, 500 - 300 * self.yScale),
                         (750, 500 - 300 * self.yScale),
                         3)

    def update(self):
        length = len(self.data) - 1
        pygame.draw.line(self.window, (255, 150, 150),
                         (50 + self.xScale * (length - 1), 500 - self.yScale * self.data[length - 1]),
                         (50 + self.xScale * length, 500 - self.yScale * self.data[length]), 3)

    def addData(self, value):
        self.data.append(value)


class Wall(object):
    def __init__(self, x, y, window):
        self.x = x
        self.y = y
        self.image = pygame.image.load("wall.png")
        self.window = window

    def draw(self):
        global wallPos
        mouse = pygame.mouse.get_pos()[0]
        if mouse > 300:
            wallPos = mouse
        self.window.blit(self.image, (wallPos, self.y))


# Simple player object
class Player(object):
    def __init__(self, x, y, window):
        self.__x = x
        self.y = y
        self.mass = 200
        self.__v = 0
        self.power = 0
        self.sensorSampleRate = 0.2
        self.sensor = 800
        self.image = pygame.image.load("robot.png")
        # Robot icon made by Turkkub fro www.flaticon.com:  <a href="https://www.flaticon.com/authors/turkkub"        # self.image = pygame.transform.rotate(self.image, 270)
        self.window = window
        self.update_ultrasonic()
        self.stopped = True

    def draw(self):
        # Force = motor - friction - resistance
        fric = self.mass / 10
        totalAccel = (0.2 * math.copysign(math.pow(self.power, 2), self.power) - math.copysign(fric,
                                                                                               self.__v or self.power) - 2 * math.copysign(
            math.pow(self.__v, 2), self.__v)) / self.mass
        self.__v = self.__v + totalAccel
        if (abs(self.power) < 10 and abs(self.__v) < 5):
            self.__v = 0
            if (self.stopped == False):
                print(self.ultrasonic_sensor())
                self.stopped = True
        else:
            self.stopped = False
        self.__x += self.__v
        self.window.blit(self.image, (self.__x, self.y))

    # Method to move object (special input of speedx and speedy)
    def run(self, power):
        if power > 100:
            power = 100
        if power < -100:
            power = -100
        self.power = power

    def wait(self, time):
        pygame.time.wait(time)
        print(self.ultrasonic_sensor())

    def setPayload(self, mass):
        if (mass < 0):
            mass = 0
        if (mass > 20):
            mass = 20
        self.mass = 200 + mass * 50

    def ultrasonic_sensor(self):
        return self.sensor

    def set_timeout(self, func, sec):
        t = None

        def func_wrapper():
            func()
            t.cancel()

        t = Timer(sec, func_wrapper)
        t.start()

    def update_ultrasonic(self):
        global wallPos
        self.sensor = wallPos - self.__x
        self.set_timeout(self.update_ultrasonic, 0.002)


# Main Class
class MainRun(object):
    def __init__(self, program):
        pygame.init()
        pygame.font.init()

        global displayw
        global displayh
        self.window = pygame.display.set_mode((displayw, displayh))
        self.windowclock = pygame.time.Clock()
        self.program = program
        self.Main()

    def Main(self):
        global wallPos
        stopped = False

        # Creating the player objects
        wall = Wall(wallPos, 30, self.window)
        player = Player(0, 100, self.window)
        graph = Graph(self.window)

        cont = Thread(target=self.program, args=(player,))
        cont.daemon = True

        # When you want to draw the player object use its draw() method
        self.window.fill((255, 255, 255))
        player.draw()
        wall.draw()
        graph.showGraph()
        pygame.display.update()
        cont.start()

        while not stopped:
            self.window.fill((255, 255, 255),
                             (0, 0, displayw, displayh / 2))  # Tuple for filling display... Current is white

            # Event Tasking
            # Add all your event tasking things here
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stopped = True


            # And be sure to redraw your player
            player.draw()
            wall.draw()
            pygame.draw.line(self.window, (150, 150, 255), (wallPos - 250, 30), (wallPos - 250, 200), 3)
            graph.addData(player.ultrasonic_sensor())
            graph.update()

            # Remember to update your clock and display at the end
            pygame.display.update()
            self.windowclock.tick(simSpeed)
        pygame.display.quit()
        pygame.quit()
        exit()