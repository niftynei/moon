from PIL import Image
from PIL import ImageDraw
import datetime
import math
import time
import subprocess
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

radius=12*10 
start=160 - radius
diameter=radius * 2

def loadIllum():
    with open(dir_path + "/circles.dat", "r") as ins:
            array = []
            for line in ins:
                line = line.rstrip('\n')
                res = line.split()
                output = {}
                output['theta'] = float(res[1][1:])
                output['R'] = float(res[2][1:])
                array.append(output)
            return array

def getCircleVals(illum, array):
    #convert illum to integer
    index = 0
    if (illum > .5):
        index = int(round((1.0 - illum) * 100))
    else:
        index = int(round(illum * 100))
    return array[index]

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

def getTimeNow():
    return datetime.datetime.now().strftime("%s")

def getPos(at):
    lat, lon =  getLatLong()
    results = subprocess.check_output([dir_path + '/moon_project',lat,lon,at])
    inputs = results.split()
    output = {}
    output['posAng'] = float(inputs[1])
    output['illum'] = float(inputs[0])
    return output

img = Image.new('RGB', (320,320), 'black')
draw =  ImageDraw.Draw(img)
illVals = loadIllum()

factor = .53
info = getPos(str(int(((2531040) * factor + 1528893780))))

print (info['illum'], factor)

vals = getCircleVals(info['illum'], illVals)

R = vals['R']
ang = vals['theta'] / 2.0
r = radius
s = R - math.sqrt(R * R - r * r)
plus = info['illum'] >= .5

if (info['illum'] == .5):
    draw.pieslice((start,start,diameter+start,diameter+start),-180,0, 'white')
    pass
elif (info['illum'] <= 0.01):
    # don't draw anything == new moon
    pass
elif (info['illum'] >= .99):
    draw.pieslice((start,start,diameter+start,diameter+start),-180,180, 'white')
elif (plus):
    draw.pieslice((start,start,diameter+start,diameter+start),-180,0, 'white')
    coords = getPlus(R,r,s)
    crescent = Image.new('RGB', (320, 320), 'black')
    dc = ImageDraw.Draw(crescent)
    dc.pieslice(coords, -90+ang, -90-ang, 'white')

    cx0 = start
    cy0 = r + start
    cx1 = 2 * r + start
    cy1 = int(r+s) + start
    cres = crescent.crop((cx0,cy0,cx1,cy1))
    img.paste(cres, (cx0,cy0,cx1,cy1))
else:
    draw.pieslice((start,start,diameter+start,diameter+start),-180,0, 'white')
    coords = getMinus(R,r,s)
    draw.pieslice(coords,90+ang,90-ang,'black')


rotated = img.rotate(info['posAng'])
rotated.show()
