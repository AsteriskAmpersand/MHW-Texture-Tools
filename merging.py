# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 04:11:50 2020

@author: AsteriskAmpersand
"""
import numpy as np
import cv2

def shape(array):
    return array.shape[1],array.shape[0]

def alphaCompositeChannel(cb,ca,ab,aa):
    return (ca*aa+cb*ab*(1-aa))/(aa+ab*(1-aa))
    
def alphaCompositeAlpha(ab,aa):
    return aa+ab*(1-aa)

def breakChannels(split):
    channels = len(split)
    if channels == 1:
        return split[0],split[0],split[0]
    if channels == 2:
        return [*split]+[split[0]*0+255]
    if channels == 3:
        return split
    if channels == 4:
        return split[:3]

def overlay_transparent(base, overlay, lalpha,ralpha):
    # Extract the alpha mask of the RGBA image, convert to RGB 
    overlay = cv2.resize(overlay,shape(base))
    ralpha = cv2.resize(ralpha,shape(base))
    
    c = cv2.split(overlay)
    rb,rg,rr = breakChannels(c)
    ra = ralpha.astype(float)/255.0
    
    c = cv2.split(base)
    lb,lg,lr = breakChannels(c)
    la = lalpha.astype(float)/255.0
    
    r = alphaCompositeChannel(lr,rr,la,ra).astype(np.uint8)
    g = alphaCompositeChannel(lg,rg,la,ra).astype(np.uint8)
    b = alphaCompositeChannel(lb,rb,la,ra).astype(np.uint8)
    a = (alphaCompositeAlpha(la, ra)*255).astype(np.uint8)
    #cv2.imshow("text",overlay)
    #cv2.waitKey()
    #cv2.imshow("text",cv2.merge((b,g,r)))
    #cv2.waitKey()
    #cv2.imshow("text",ralpha)
    #cv2.waitKey()
    return a, cv2.merge((b,g,r,a))

def pullAlpha(file):
    channels = cv2.split(cv2.imread(str(file),-1))
    if len(channels) < 4:
        return channels[0]*0+255
    else:
        return channels[3]

def merging(filelist,output,alphas = None):
    if not alphas:
        alphas = [pullAlpha(file) for file in filelist]
    base = filelist[0]
    img = cv2.imread(str(base),-1)
    lalpha = cv2.resize(alphas[0],shape(img))    
    for file,ralpha in zip(filelist[1:],alphas[1:]):
        #print(file)
        overlay = cv2.imread(str(file),-1)
        lalpha,img = overlay_transparent(img,overlay,lalpha,ralpha)        
    cv2.imwrite(output,img)
    return alphas
    
