import numpy as np
import cv2
import math
from Im_Mine import *
from scipy.interpolate import interp1d

InWidth = 1280
Inheight= 720
sampling = 8

x = np.arange(0, InWidth+1, sampling)
y = np.arange(0, Inheight+1, sampling)
if(len(x)%2):
    x = np.append(x,[0])
X,Y = np.meshgrid(x, y)
LutOrg = np.dstack([Y, X])

lutW = len(x)
lutH = len(y)


TgtMat = np.zeros((lutH, lutW,2), np.float)
LutMat = np.zeros((lutH, lutW,2), np.int32)
img_Ox = InWidth/2
img_Oy = Inheight/2

Dy = abs(LutOrg[0][0][0] - img_Oy)
Dx = abs(LutOrg[0][0][1] - img_Ox)
rrMax = 420#(math.sqrt((Dx * Dx) + (Dy * Dy)))
RrZoom = 1

print InWidth, Inheight, sampling, img_Ox,img_Oy,lutW, lutH
print Dy,Dx,rrMax , round(math.sqrt((Dx * Dx) + (Dy * Dy)),1)/2


for y in range(0, lutH):
    for x in range(0, lutW):
        Dy = float(abs(LutOrg[y][x][0] - img_Oy))
        Dx = float(abs(LutOrg[y][x][1] - img_Ox))
        RR = math.sqrt((Dx * Dx) + (Dy * Dy))

        if Dx:
            theta = math.atan(Dy / Dx)
        else:
            theta = 90 * math.pi / 180

        NewRr = ((rrMax) * math.tan(RR / rrMax)) / RrZoom
        NewdY = (NewRr * np.sin(theta))
        NewdX = (NewRr * np.cos(theta))

        if LutOrg[y][x][0] < img_Oy:
            TgtMat[y][x][0] = (img_Oy - NewdY)
        else:
            TgtMat[y][x][0] = (img_Oy + NewdY)

        if LutOrg[y][x][1] <= img_Ox:
            TgtMat[y][x][1] = (img_Ox - NewdX)
        else:
            TgtMat[y][x][1] = (img_Ox + NewdX)



for y in range(0, lutH):
    for x in range(0, lutW):
        Dy = float(abs(LutOrg[y][x][0] - img_Oy))
        Dx = float(abs(LutOrg[y][x][1] - img_Ox))
        RR = math.sqrt((Dx * Dx) + (Dy * Dy))
        if Dx:
            theta = math.acos(Dx / RR)
        else:
            theta = 90 * math.pi / 180
        LutRr = (rrMax * math.atan(RR/rrMax))/ RrZoom
        LutdY = (LutRr * np.sin(theta))
        LutdX = (LutRr * np.cos(theta))

        if y <= (lutH>>1):
            LutMat[y][x][0] = (img_Oy - LutdY)
        else:
            LutMat[y][x][0] = (img_Oy + LutdY)
        if x < (lutW>>1):
            LutMat[y][x][1] = (img_Ox - LutdX)
        else:
            LutMat[y][x][1] = (img_Ox + LutdX)

        if LutMat[y][x][0] <0:
            LutMat[y][x][0] = 0
        if LutMat[y][x][1] < 0:
            LutMat[y][x][1] = 0

#####   Pos  ==>> Lut
OutData = np.zeros(lutH*lutW, np.uint32)
for y in range(0, lutH):
    for x in range(0, lutW,2):
        LData = (LutMat[y][x+1][0] * 16) << 15
        LData |=  (LutMat[y][x+1][1]*16)&0x00007fff
        LData = LongSwap(LData)
        OutData[(y * lutW) + x] = LData

        LData = (LutMat[y][x][0] * 16) << 15
        LData |= (LutMat[y][x][1] * 16) & 0x00007fff
        LData = LongSwap(LData)
        OutData[(y * lutW) + x+1] = LData

header = np.array([0x4C,0x55,0x54,0x20,0x00,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], np.uint8)
f = open("Out2.lut", 'wb')
f.write(header)
f.write(OutData)
Wrlen = 1024-(((4*len(OutData)))%1024)
ModData = np.zeros(Wrlen, np.uint8)
f.write(ModData)
f.close()


##############################################################################################################
"""
from scipy import interpolate
x = [0, 10]
y = [50,100]
f = interpolate.interp1d(x, y)
for d in range(0, 11):
    print d,f(d)
"""
"""
from scipy.interpolate import Rbf

x = [0, 10]
y = [50,100]
z = [100,200]
rbf = Rbf(x, y, z, epsilon=2)

for d in range(0, 11):
    print rbf(d)
"""

##############################################################################################################

img_color = cv2.imread( 'LDC.jpg', cv2.COLOR_BGR2RGB )
jpgheight, jpgwidth, jpgchannel = img_color.shape
black_image = np.zeros((lutH-1, lutW-2, 3), np.uint8)
for y in range(0, lutH-1):
    for x in range(0, lutW-2):
        black_image[y,x, 0] = img_color[LutMat[y][x][0], LutMat[y][x][1], 0]
        black_image[y,x, 1] = img_color[LutMat[y][x][0], LutMat[y][x][1], 1]
        black_image[y,x, 2] = img_color[LutMat[y][x][0], LutMat[y][x][1], 2]
black_image = cv2.resize(black_image, (1280, 720),interpolation = cv2.INTER_CUBIC)
#cv2.imshow("image", black_image)
cv2.imwrite('OUT2.png',black_image)
#kwyval = cv2.waitKey()

print "end"


