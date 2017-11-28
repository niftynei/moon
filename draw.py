from PIL import Image
from PIL import ImageDraw
import math
import subprocess

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
    results = subprocess.check_output(['./moon_project',lat,lon])
    inputs = results.split()
    output = {}
    output['R'] = int(float(inputs[0][1:]))
    output['theta'] = float(inputs[1][1:]) / 2
    output['posAng'] = float(inputs[2][1:])
    output['illum'] = float(inputs[3][1:])
    return output

img = Image.new('RGB', (320,320), 'black')
draw = ImageDraw.Draw(img)
draw.pieslice((0,0,320,320),-180,0, 'white')

# positive
info = getPos()
R = info['R'] * 10
ang = info['theta']
r = 160
s = R - math.sqrt(R * R - r * r)
plus = info['illum'] >= .5

if (plus):
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
