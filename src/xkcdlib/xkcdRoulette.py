import xkcd
import cv2
import imageio
import matplotlib.pyplot as plt
import numpy as np
import random
from xkcdlib.kumikolib import Kumiko

desiredheight = 350

def panelcheck(panellist):
    returnlist = []
    for panel in panellist:
        width = panel[2]
        height = panel[3]
        area = width*height
        if area <= 100000 and area > 40000 and height/width > 0.6 and height/width < 1.25:
            returnlist.append(panel)
    return returnlist

def makerandomxkcd():
    panellist = np.zeros((350,1))
    while(panellist.shape[1] < 700):
        try:
            comic = xkcd.getRandomComic()
            array = imageio.imread(comic.getImageLink())
            k= Kumiko()
            info = k.parse_url_list([comic.getImageLink()])
            panels = info[0]['panels']
            goodpanels = panelcheck(panels)
            if (len(goodpanels) == 0):
                continue
            if len(array.shape) > 2:
                array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
            #print(f'Found comic: {comic.getImageLink()} with shape {array.shape}')
            x, y , w, h = goodpanels[random.randint(0,len(goodpanels)-1)]
            #print(x,y,w,h, array.shape)
            chosenpanel = array[y:y+h, x: x+w]

            scalefactor = desiredheight / h
            chosenpanel = cv2.resize(chosenpanel, (int(w*scalefactor), desiredheight))
            #print(panellist.shape, chosenpanel.shape)
            panellist = np.hstack([panellist, chosenpanel])
        except:
            continue
    cv2.imwrite("xkcd.png", panellist)
