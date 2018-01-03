from PIL import Image
from PIL import ImageDraw
import math
import subprocess
import os
import random
import time
import numpy as np
import scipy.misc as misc
from rgbmatrix import Adafruit_RGBmatrix

dir_path = os.path.dirname(os.path.realpath(__file__))

matrix = Adafruit_RGBmatrix(32, 1)

radius = 14 * 10
start = 160 - radius
diameter = radius * 2
color = (88,88,88)
dimen = 320
#moonColors = [(244,55,0),(86,149,86),(86,0,86),(227,55,108),(227,219,129),(0,108,129),(255,108,23),(255,196,23),(255,196,196),(101,196,196),(101,0,71),(206,0,71)]
moonColors = [(255,196,196)]

illumArr = 0

def loadIllum():
    with open(dir_path + "/circles.dat", "r") as ins:
            array = []
            for line in ins:
                line = line.rstrip('\n')
                res = line.split()
                theta = float(res[1][1:])
                R = float(res[2][1:])
                array.append([theta, R])
            return array

def getCircleVals(illum):
    global illumArr
    if (illumArr == 0):
        illumArr = loadIllum()

    #convert illum to integer
    index = 0
    if (illum > .5):
        index = int(round((1.0 - illum) * 100))
    else:
        index = int(round(illum * 100))
    return illumArr[index]

def getLatLong():
    # inner sunset, sf, ca
    return '37.7749', '122.4194'

def getPlus(R, r, s):
    y0 = -2 * R + r + s + start
    y1 = r + s + start
    x0 = -1 * R + r + start
    x1 = r + R + start
    return (x0,y0,x1,y1)

def getMinus(R,r,s):
    y0 = r - s + start
    y1 = 2 * R + r - s + start
    x0 = -1 * R + r + start
    x1 = r + R + start
    return (x0,y0,x1,y1)

def getPos():
    lat, lon =  getLatLong()
    results = subprocess.check_output([dir_path + '/moon_project_arm',lat,lon])
    inputs = results.split()
    posAngle = float(inputs[0][1:])
    illum = float(inputs[1][1:])
    return [illum, posAngle]

def pickFullMoonColor():
    pick = random.randint(0, len(moonColors) - 1)
    return moonColors[pick]


def drawMoon(img, draw, illum, R, theta):
    R = R * 10
    ang = theta / 2.0
    r = radius
    s = R - math.sqrt(R * R - r * r)

    plus = illum >= .5
    if (illum == .5):
        draw.pieslice((start,start,diameter+start,diameter+start),-180,0, fill=color)
    elif (illum <= 0.01):
        # don't show anything - new moon
        pass
    elif (illum >= .99):
        #full moon!
        fullColor = pickFullMoonColor()
        draw.pieslice((start,start,diameter+start,diameter+start),-180,180, fill=fullColor)
    elif (plus):
        coords = getPlus(R,r,s)
        crescent = Image.new('RGB', (dimen, dimen), 'black')
        dc = ImageDraw.Draw(crescent)
        dc.pieslice(coords, -90+ang, -90-ang, fill=color)

        cx0 = start
        cy0 = r + start
        cx1 = 2 * r + start
        cy1 = int(r+s) + start
        cres = crescent.crop((cx0,cy0,cx1,cy1))
        img.paste(cres, (cx0,cy0,cx1,cy1))
    else:
        draw.pieslice((start,start,diameter+start,diameter+start),-180,0, fill=color)
        coords = getMinus(R,r,s)
        draw.pieslice(coords,90+ang,90-ang,'black')

    return img


def getDownscaledImg(img):
        im2arr = np.array(img)
        resized = misc.imresize(im2arr, (32,32), interp='bilinear')
        downscaled = Image.fromarray(resized)
        return downscaled


def runStart():
    img = Image.new('RGB', (dimen,dimen), 'black')
    draw = ImageDraw.Draw(img)
    for i in range(0,101):
        illum = float(i) / 100
        theta, R = getCircleVals(illum)
        img = drawMoon(img, draw, illum, R, theta)

        # rotate just 90deg for intro
        rotated = img.rotate(90)
        downscaled = getDownscaledImg(rotated)

        matrix.Clear()
        matrix.SetImage(downscaled.im.id, 0, 0)

        time.sleep(.7)


def runMoonClock():
    img = Image.new('RGB', (dimen,dimen), 'black')
    draw = ImageDraw.Draw(img)

    while True:
        illum, posAng = getPos()
        theta, R = getCircleVals(illum)
        img = drawMoon(img, draw, illum, R, theta)

        rotated = img.rotate(posAng)

        downscaled = getDownscaledImg(rotated)
        matrix.Clear()
        matrix.SetImage(downscaled.im.id, 0, 0)

        time.sleep(5 * 60)

def testMoonColors():
    img = Image.new('RGB', (dimen,dimen), 'black')
    draw = ImageDraw.Draw(img)
    for i in range(0, len(moonColors)):
        fullColor = moonColors[i]
        draw.pieslice((start,start,diameter+start,diameter+start),-180,180, fill=fullColor)

        downscaled = getDownscaledImg(img)
        matrix.Clear()
        matrix.SetImage(downscaled.im.id, 0, 0)

        time.sleep(2)


#testMoonColors()
matrix.Clear()
runStart()
matrix.Clear()
runMoonClock()

matrix.Clear()
