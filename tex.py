# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 19:23:09 2020

@author: AsteriskAmpersand
"""

import construct as C
import copy
from pathlib import Path

mipOffsets = C.Struct(
    "mipOffset" / C.Int64sl[C.this._.mipCount],
    )

texHeader = C.Struct(
    "texString" / C.CString("utf8"),
    "version" / C.Int64sl,
    "datablock" / C.Int32sl,
    "format" / C.Int32sl,
    "mipCount" / C.Int32sl,
    "width" / C.Int32sl,
    "height" / C.Int32sl,
    "imageCount" / C.Int32sl,
    "typeData" / C.Int32sl,
    "one1" / C.Int32sl,
    "null0" / C.Int32sl[3],
    "neg0" / C.Int32sl,
    "null1" / C.Int32sl[2],
    "special" / C.Int32sl,
    "null2" / C.Int32sl[4],
    "neg1" / C.Int32sl[8],
    "flags" / C.Byte[32],
    "nullx" / C.Int32sl[8],
    "offsets" / mipOffsets[C.this.imageCount],
    )

class dummyMipOffset ():
    def __init__(self,entry):
        self.mipOffset = entry

def unpack(TEXPath):
    texFile = open(TEXPath,"rb")
    texData = texFile.read()
    texHead = texHeader.parse(texData)
    opf = []
    if texHead.imageCount > 1:
        path = Path(TEXPath)
        filenames = lambda x : path.parent / (path.stem + "%02d"%x + path.suffix)
        sampleOffset = [val-8*texHead.mipCount*(texHead.imageCount-1) for val in texHead.offsets[0].mipOffset]
        for ix,(start,end) in enumerate(zip(texHead.offsets,list(texHead.offsets[1:])+[dummyMipOffset([len(texData)])])):
            header = copy.deepcopy(texHead)
            header.imageCount = 1
            #header.offsets = sampleOffset
            texture = texData[start.mipOffset[0]:end.mipOffset[0]]
            
            header = {**{key.name:getattr(header,key.name) for key in texHeader.subcons}, 
                      "offsets":[{"mipOffset":sampleOffset}]}
            data = texHeader.build(header)+texture
            with open(filenames(ix),"wb") as outf:
                outf.write(data)
            opf.append(filenames(ix))
    else: return [TEXPath]
    return opf

def pack(TEXPathList,outpf):
    texFile = open(TEXPathList[0],"rb")
    texData = texFile.read()
    texHead = texHeader.parse(texData)
    texHead.imageCount = len(TEXPathList)
    headerAddedLen = 8*texHead.mipCount*(texHead.imageCount-1)
    mipLen = len(texData) - texHead.offsets[0].mipOffset[0]
    baseOffset = texHead.offsets[0].mipOffset
    finalOffsets = []
    data = b""
    for ix,tex in enumerate(TEXPathList):
        finalOffsets.append({"mipOffset":[o+ix*mipLen+headerAddedLen for o in baseOffset]})
        texFile = open(TEXPathList[0],"rb")
        texData = texFile.read()
        data += texData[baseOffset[0]:]
    texHead.offsets = finalOffsets
    with open(outpf,"wb") as outf:
        outf.write(texHeader.build(texHead)+data)
    return outpf

"""
if __name__ in "__main__":
    for TEXPath in Path(r"E:\\MHW\ChunkG0").rglob("*.tex"): 
        texFile = open(TEXPath,"rb")
        texData = texFile.read()
        texHead = texHeader.parse(texData)
        if texHead.imageCount > 1:
            print(TEXPath)
"""  