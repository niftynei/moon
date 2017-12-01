from PIL import Image
from PIL import ImageDraw
import math
import subprocess

def loadIllum():
    with open("circles.dat", "r") as ins:
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
        index = int(round((1.0 - illum) * 10000))
    else:
        index = int(round(illum * 10000))
    return array[index]

def getLatLong():
    # inner sunset, sf, ca
    return '37.7749', '122.4194'

def getPlus(R, r, s):
    y0 = -2 * R + r + s
    y1 = r + s
    x0 = -1 * R + r
    x1 = r + R
    return (x0,y0,x1,y1)

def getMinus(R,r,s):
    y0 = r - s
    y1 = 2 * R + r - s
    x0 = -1 * R + r
    x1 = r + R
    return (x0,y0,x1,y1)

def getPos():
    lat, lon =  getLatLong()
    results = subprocess.check_output(['./moon_project_arm',lat,lon])
    #results = subprocess.check_output(['./moon_project',lat,lon])
    inputs = results.split()
    output = {}
    output['posAng'] = float(inputs[0][1:])
    output['illum'] = float(inputs[1][1:])
    return output

img = Image.new('RGB', (320,320), 'black')
draw = ImageDraw.Draw(img)
draw.pieslice((0,0,320,320),-180,0, 'white')
illVals = loadIllum()

# positive
info = getPos()
vals = getCircleVals(info['illum'], illVals)

R = vals['R'] * 10
ang = vals['theta'] / 2.0
r = 160
s = R - math.sqrt(R * R - r * r)
plus = info['illum'] >= .5

if (info['illum'] == .5):
    pass
elif (plus):
    coords = getPlus(R,r,s)
    crescent = Image.new('RGB', (320, 320), 'black')
    dc = ImageDraw.Draw(crescent)
    dc.pieslice(coords, -90+ang, -90-ang, 'white')

    cx0 = 0
    cy0 = r
    cx1 = 2 * r
    cy1 = int(round(r+s))
    cres = crescent.crop((cx0,cy0,cx1,cy1))
    img.paste(cres, (cx0,cy0,cx1,cy1))
else:
    coords = getMinus(R,r,s)
    draw.pieslice(coords,90+ang,90-ang,'black')

rotated = img.rotate(info['posAng'])
rotated.show()
