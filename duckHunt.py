# File Name: ludwig_grant_AS08.py
# File Path: /home/ludwigg/Python/PiDuckHunt/duckHunt.py
# Run Command: sudo python3 /home/ludwigg/Python/PiDuckHunt/duckHunt.py

# Grant Ludwig
# 10/26/19
# Duck Hunt

from graphics import *
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO # Raspberry Pi GPIO library
import random
import math
import time

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
PLAY_HEIGHT = 480

heightDifference = SCREEN_HEIGHT - PLAY_HEIGHT

screenCenterPoint = Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
playCenterPoint = Point(SCREEN_WIDTH / 2, PLAY_HEIGHT / 2 + heightDifference)

kill = False

ducks = (   "/home/ludwigg/Python/PyRpi_AS8/blueDuck.png",
            "/home/ludwigg/Python/PyRpi_AS8/blackDuck.png",
            "/home/ludwigg/Python/PyRpi_AS8/redDuck.png")
deadDucks = (   "/home/ludwigg/Python/PyRpi_AS8/blueDuckDead.png",
                "/home/ludwigg/Python/PyRpi_AS8/blackDuckDead.png",
                "/home/ludwigg/Python/PyRpi_AS8/redDuckDead.png")
duckIndex = 0

aim = Circle(playCenterPoint, 15)
innerAim = Circle(playCenterPoint, 5)
target = Image(Point(0, 0), ducks[duckIndex])
death = Image(Point(0, 0), deadDucks[duckIndex])
message = Text(Point(100, 100), "")
scoreText = Text(Point(100, 50), "")
score = 0

win = GraphWin("Pi Duck Hunt", SCREEN_WIDTH, SCREEN_HEIGHT, autoflush=False)

def getXPosition():
    global chan
    return round(chan.voltage/3.3 * SCREEN_WIDTH)

def getYPosition():
    global chan2
    return round((chan2.voltage/3.3 * PLAY_HEIGHT) + heightDifference)
    
def spawnTarget():
    global target
    global kill
    global ducks
    global duckIndex
    found = False
    target.undraw()
    duckIndex = random.randint(0,2)
    while not found:
        target = Image(Point(random.randint(20, SCREEN_WIDTH - 20), random.randint(20, SCREEN_HEIGHT - 20)), ducks[duckIndex])
        targetCenter = target.getAnchor()
        if math.sqrt((playCenterPoint.x - targetCenter.x)**2 + (playCenterPoint.y - targetCenter.y)**2) <= (260):
            found = True
    kill = False
    target.draw(win)

def shoot(channel):
    global target
    global kill
    global score
    aimCenter = aim.getCenter()
    targetCenter = target.getAnchor()
    
    if math.sqrt((aimCenter.x - targetCenter.x)**2 + (aimCenter.y - targetCenter.y)**2) <= (30):
        kill = True
        score += 1

def main():
    global aim
    global innerAim
    global target
    global kill
    global score
    global death
    
    # set coordnate plane for easy translation from the joystick position
    # xll, yll, xur, yur
    win.setCoords(SCREEN_WIDTH, 0, 0, SCREEN_HEIGHT)
    win.setBackground("Grey")
    
    message.setTextColor("white")
    message.setSize(20)
    message.draw(win)
    
    scoreText.setTextColor("white")
    scoreText.setSize(20)
    scoreText.draw(win)
    
    target.draw(win)
    spawnTarget()
    
    aim.draw(win)
    innerAim.draw(win)
    
    dog = Image(playCenterPoint, "/home/ludwigg/Python/PyRpi_AS8/dog.png")
    
    end = time.time() + 30
    deathTime = 0
    playing = True
    while(playing):
        timeLeft = round(end - time.time(), 2)
        if timeLeft <= 0:
            message.setText("Game Over!")
            scoreText.setText("Final Score: " + str(score))
            dog.draw(win)
            playing = False
        else:
            message.setText(timeLeft)
            scoreText.setText("Score: " + str(score))
            if kill:
                try:
                    death.undraw()
                except:
                    print()
                death = Image(target.getAnchor(), deadDucks[duckIndex])
                spawnTarget()
                death.draw(win)
                deathTime = time.time() + .5
                
            aim.undraw()
            innerAim.undraw()
            
            aim = Circle(Point(getXPosition(), getYPosition()), 15)
            innerAim = Circle(Point(getXPosition(), getYPosition()), 5)
            
            aim.setOutline("Red")
            innerAim.setFill("Red")
            
            aim.draw(win)
            innerAim.draw(win)
            
            if (deathTime - time.time()) < 0:
                try:
                    death.undraw()
                except:
                    print()
            
        update(60)
    
    time.sleep(5)
    win.close()

# Setup GPIO
GPIO.setwarnings(False) # Ignore warnings
GPIO.setmode(GPIO.BCM) # Use BCM Pin numbering
GPIO.setup(26, GPIO.IN)

GPIO.add_event_detect(26, GPIO.FALLING, callback=shoot, bouncetime=300)
	
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)
chan2 = AnalogIn(mcp, MCP.P1)

try:
    main()

except KeyboardInterrupt: 
    # This code runs on a Keyboard Interrupt <CNTRL>+C
    print('\n\n' + 'Program exited on a Keyboard Interrupt' + '\n') 

except: 
    # This code runs on any error
    print('\n' + 'Errors occurred causing your program to exit' + '\n')

finally: 
    # This code runs on every exit and sets any used GPIO pins to input mode.
    GPIO.cleanup()