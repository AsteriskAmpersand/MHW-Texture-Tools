# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 02:36:37 2020

@author: AsteriskAmpersand
"""

import cv2
from pathlib import Path
import subprocess

def nmRemap(normalFile,nmPath,invert=False):
    normal = cv2.imread(str(normalFile),1)
    if invert:
        normal = 255-normal
    B,G,R = cv2.split(normal)
    output_image = cv2.merge((B*0,G,R))
    cv2.imwrite(str(nmPath),output_image)

def rmtRemap(roughnessFile=None,metalicFile=None,subsurfaceFile=None):
    rmtConverter = lambda f: f.parent / (('_'.join(f.stem.split("_")[:-1]))+"_RMT"+f.suffix)
    if roughnessFile:
        #print(roughnessFile)
        roughness = cv2.imread(str(roughnessFile), 1)
        _, _, R = cv2.split(roughness)
        default = R*0
        rmtPath = rmtConverter(roughnessFile)
    if metalicFile:        
        metalic = cv2.imread(str(metalicFile), 1)
        _, G, _ = cv2.split(metalic)
        default = G*0
        rmtPath = rmtConverter(metalicFile)
    if subsurfaceFile:
        subsurface = cv2.imread(str(subsurfaceFile), 1)
        B, _, _ = cv2.split(subsurface)
        default = B*0
        rmtPath = rmtConverter(subsurfaceFile)
    if not roughnessFile: R = 255-default
    if not metalicFile: G = default
    if not subsurfaceFile: B = default
    output_image = cv2.merge ( (B, G, R) )
    cv2.imwrite(str(rmtPath), output_image)
    return rmtPath

def convert(inputFile,formating,outputFolder=None,mipmaps=0,output = False):
    print = lambda x: output(str(x)) if output else ""
    if outputFolder is None:
        outputFolder = Path(inputFile).parent
    filtering = "LINEAR" if formating == "BC7_UNORM" else "CUBIC"
    command = ["TexConv.exe",
                "-pow2", #set resolution to power of 2
                "-wrap", #texture addressing mode set to wrap
                "-m","%d"%mipmaps, #disable mipmaps
                "-sepalpha", #fixes alpha on mipmaps
                "-nologo", #why, why is there a copyright logo embbeded even???
                "-ft","DDS", #output filetype
                "-if",filtering, #Cubic filtering
                "-y",#Overwrite if it already exists
                "-f","%s" %formating,
                '-o',str(outputFolder), #output folder
                str(inputFile)]#inputfile
    print(" ".join(command))
    result = subprocess.call(command,shell=True)
    convertTarget = outputFolder / (inputFile.stem + ".dds")
    print("MHWorldTex.exe"+" "+'"'+str(convertTarget)+'"')
    result = subprocess.call(["MHWorldTex.exe",str(convertTarget)],shell=True)
    #Offset 0x24 on the final tex requries an edit from 30 to 31. 31 is sRGB 30 is Linear
    if formating == "BC7_UNORM":
        target = convertTarget.with_suffix(".tex")
        t = target.open("rb").read()
        with open(target,"wb") as outf:
            outf.write(t[:0x24]+b'\x1E'+t[0x25:])