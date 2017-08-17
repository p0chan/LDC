import numpy as np
import cv2
import math
import array
import sys
from Im_Mine import *
"""
def LongSwap(LL):
    ll  = (LL     &0xff)<<24
    ll |= (LL >> 8  &0xff)<<16
    ll |= (LL >> 16 & 0xff) << 8
    ll |= (LL >> 24 & 0xff)
    return ll
"""

height = 720
width = 1280
ssampling = 8

lutW = int(math.ceil((width / 2.)  / ssampling) *2 + 1)
lutH = int(math.ceil((height / 2.) / ssampling) *2 + 1)

if(lutW%2):
    lutW+=1

print width,height,ssampling,lutW,lutH

f = open("720.lut", 'rb')
filedata = f.read()
f.close()

filedata = array.array('L',filedata)
filedata = np.array(filedata)
#print filedata
#print "0x%x"%filedata[4]
#print "0x%x"%filedata[4].byteswap()


#####   Lut  ==>> Pos
Lut = np.zeros((height,width,2), np.int)
for y in range(0, lutH):
    for x in range(0, lutW,2):
        uData = LongSwap(filedata[4 + (y * (lutW)) + x + 1])

        if (x+1 == lutW - 1):
            fX = (uData & 0x00007fff) / 16.0
            fY = ((uData >> 15) & 0x7fff) / 16.0
        else:
            fX = (uData & 0x00007fff) / 16.0
            fY = ((uData >> 15) & 0x7fff) / 16.0
        Lut[y][x][0] = fY+1
        Lut[y][x][1] = fX+1
        #print y,x+1,"0x%08x" % uData, " => ", "y=%03d" % fY, "X=%04d" % fX

        uData = LongSwap(filedata[4 + (y * (lutW)) + x])
        if (x == lutW - 1):
            fX = (uData & 0x00007fff) / 16.0
            fY = ((uData >> 15) & 0x7fff) / 16.0
        else:
            fX = (uData & 0x00007fff) / 16.0
            fY = ((uData >> 15) & 0x7fff) / 16.0
        Lut[y][x+1][0] = fY+1
        Lut[y][x+1][1] = fX+1
        #print y, x, "0x%08x" % uData, " => ", "y=%03d" % fY, "X=%04d" % fX

"""
for y in range(0, lutH):
    for x in range(0, lutW,1):
        print Lut[y][x][0], Lut[y][x][1]
"""
x = np.arange(0, 1281, 8)
y = np.arange(0, 721, 8)
if(len(x)%2):
    x = np.append(x,[0])
X,Y = np.meshgrid(x, y)
Lut = np.dstack([Y, X])
"""
for y in range(0, lutH):
    for x in range(0, lutW):
        print Lut[y][x][0], Lut[y][x][1], "==" , Lut2[y][x][0], Lut2[y][x][1]
exit()
"""

#####   Pos  ==>> Lut
OutData = np.zeros(lutH*(lutW), np.int32)
""""""
for y in range(0, lutH):
    for x in range(0, lutW,2):
        LData = (Lut[y][x+1][0] * 16) << 15
        LData |=  (Lut[y][x+1][1]*16)&0x00007fff
        LData = LongSwap(LData)
        OutData[(y * (lutW)) + x] = LData

        LData = (Lut[y][x][0] * 16) << 15
        LData |= (Lut[y][x][1] * 16) & 0x00007fff
        LData = LongSwap(LData)
        OutData[(y * (lutW )) + x+1] = LData

"""
for y in range(0, lutH*(lutW+1)):
    print "0x%08x" % OutData[y]
"""

header = np.array([0x4C,0x55,0x54,0x20,0x00,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], np.uint8)

#print "0x%x"%sys.getsizeof(OutData)
#print "0x%x"%OutData.size
#print "0x%x"%len(OutData) , "0x%x"%(lutH*(lutW+1))
#print "0x%x"%(lutH*(lutW+1)*4)


f = open("Out.lut", 'wb')
f.write(header)
f.write(OutData)
Wrlen = 1024-(((4*len(OutData)))%1024)
ModData = np.zeros(Wrlen, np.uint8)
f.write(ModData)
f.close()