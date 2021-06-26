# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 21:57:35 2020

@author: AsteriskAmpersand
"""
import sys
import os
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog
from mainWindow import Ui_MainWindow
from remapping import rmtRemap, nmRemap, convert
from merging import merging
from tex import pack,unpack
from pathlib import Path
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, arguments):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("A**& Texture Tools")
        self.connect()
        self.show()
    def execute(self):
        if self.ui.input.text():
            self.ui.console.append("Parsing %s"%self.ui.input.text())
            plist = list(Path(self.ui.input.text()).glob("*.PNG"))+list(Path(self.ui.input.text()).glob("*.TGA"))
            grouping = self.group(plist)
            for group in grouping.values():
                self.parser(group)
                
    def connect(self):
        self.ui.convert.clicked.connect(self.execute)
        self.ui.inputFind.clicked.connect(self.getInput)
        self.ui.outputFind.clicked.connect(self.getOutput)
        self.ui.rename.clicked.connect(self.rename)
        
        self.ui.mUp.pressed.connect(self.mMoveUp)
        self.ui.mDown.pressed.connect(self.mMoveDown)
        self.ui.mAdd.pressed.connect(self.mAdd)
        self.ui.mRemove.pressed.connect(self.mDelete)
        self.ui.merge.pressed.connect(self.merge)
        
        self.ui.pUp.pressed.connect(self.pMoveUp)
        self.ui.pDown.pressed.connect(self.pMoveDown)
        self.ui.pAdd.pressed.connect(self.pAdd)
        self.ui.pRemove.pressed.connect(self.pDelete)
        self.ui.pack.pressed.connect(self.pack)
        self.ui.unpack.pressed.connect(self.unpack)
        self.ui.packFind.pressed.connect(self.getPacked)
        self.ui.unpackFind.pressed.connect(self.getUnpacked)        

    def mAdd(self):self.add(self.ui.mPaths,"PNG")
    def mAddItem(self,item):self.addItem(item,self.ui.mPaths)
    def mDelete(self):self.delete(self.ui.mPaths)
    def mMoveUp(self):self.moveUp(self.ui.mPaths)
    def mMoveDown(self):self.moveDown(self.ui.mPaths)
    
    def pAdd(self):self.add(self.ui.pPaths,"TEX")
    def pAddItem(self,item):self.addItem(item,self.ui.pPaths)
    def pDelete(self):self.delete(self.ui.pPaths)
    def pMoveUp(self):self.moveUp(self.ui.pPaths)
    def pMoveDown(self):self.moveDown(self.ui.pPaths)
    
    def pack(self):
        iterablePaths = list((self.ui.pPaths.item(i) for i in range(self.ui.pPaths.count())))
        o = pack([path.text() for path in iterablePaths], self.ui.packPath.text())
        self.ui.console.append("Packed %d textures into %s"%(len(iterablePaths),self.ui.packPath.text()))
        
    def unpack(self):
        output = unpack(self.ui.unpackPath.text())
        self.ui.console.append("Converted %s into %d files:"%(self.ui.unpackPath.text(),len(output)))
        for o in output:
            self.ui.console.append("\t%s"%o)
                
    def extensionGroup(self,dlist,plist):
        extensions = {}#{"BML":[]}
        for diffuse,paths in zip(dlist,plist):
            #extensions["BML"].append(diffuse)
            for p in paths:
                if str(p)!= str(diffuse):
                    split = p.stem.split("_")
                    base,extension = '_'.join(split[:-1]),split[-1]
                    if extension not in extensions:
                        extensions[extension] = []
                    extensions[extension].append(p)
        return extensions
                    
    def merge(self):
        dlist = [Path(path.text()) for path in iter((self.ui.mPaths.item(i) for i in range(self.ui.mPaths.count())))]
        plist = [p.parent.glob('_'.join(p.stem.split("_")[:-1])+"_*"+p.suffix) for p in dlist]
        groupings = self.extensionGroup(dlist,plist)
        output = lambda y,x: str(x.parent / ("Merged_" + y + x.suffix))
        extension = str(dlist[0].stem).split("_")[-1]
        alphas = merging(dlist, output(extension,dlist[0]))
        self.ui.console.append("Merging %s:"%extension)
        for file in dlist:
            self.ui.console.append("\t"+str(file))
        for extension in groupings:
            merging(groupings[extension],output(extension,groupings[extension][0]),alphas)
            self.ui.console.append("Merging %s:"%extension)
            for file in groupings[extension]:
                self.ui.console.append("\t"+str(file))
    def getUnpacked(self):
       file = QFileDialog.getOpenFileName(self, "Select TEX File", "*.tex")[0]
       if file:
           self.ui.unpackPath.setText(file)     
    def getPacked(self):
       file = QFileDialog.getSaveFileName(self, "Select Destination File", "*.tex")[0]
       if file:
           self.ui.packPath.setText(file)   
    def getInput(self):
       folder = QFileDialog.getExistingDirectory(self, "Open Input Folder", "")
       if folder:
           self.ui.input.setText(folder)   
    def getInput(self):
       folder = QFileDialog.getExistingDirectory(self, "Open Input Folder", "")
       if folder:
           self.ui.input.setText(folder)   
    def getOutput(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Output Folder", "")
        if folder:
            self.ui.output.setText(folder)
    def group(self,pathList):
        categories = {}
        for path in pathList:
            self.ui.console.append("Adding %s to Conversion List"%path)
            parts = path.stem.split("_")
            extension = parts[-1]
            body = '_'.join(parts[0:-1])
            if body not in categories:
                categories[body] = {}
            categories[body][extension] = path
        return categories
    def parser(self,extensionDict):
        ui = self.ui
        outf = Path(self.ui.output.text() if self.ui.output.text() else self.ui.input.text())
        def convertLoad(code):
            if getattr(ui,"s"+code).text() in extensionDict:
                File = extensionDict[getattr(ui,"s"+code).text()]
                replace = lambda x: x.replace(getattr(ui,"s"+code).text(),getattr(ui,"t"+code).text())
                self.convert(File,outf, getattr(ui,"f"+code).currentText(),replace)
        for code in ["BML","EM","CMM"]:
            convertLoad(code)
        if ui.sNM.text() in extensionDict:
            NM = extensionDict[ui.sNM.text()]
            replace = lambda x: x.replace(ui.sNM.text(),ui.tNM.text())
            self.convertNormal(NM,outf, ui.fNM.currentText(),replace)
        if ui.sR.text() in extensionDict or ui.sM.text() in extensionDict or ui.sT.text() in extensionDict:            
            self.rmtParser(extensionDict)
    def rmtParser(self,extensionDict):
        ui = self.ui
        RFile = extensionDict[ui.sR.text()] if ui.sR.text() in extensionDict else None
        MFile = extensionDict[ui.sM.text()] if ui.sM.text() in extensionDict else None
        TFile = extensionDict[ui.sT.text()] if ui.sT.text() in extensionDict else None
        RMTFile = rmtRemap(RFile,MFile,TFile)
        outf = Path(self.ui.output.text() if self.ui.output.text() else self.ui.input.text())
        code = "RMT"
        replace = lambda x: x.replace("RMT",getattr(ui,"t"+code).text())
        self.convert(RMTFile,outf, getattr(ui,"f"+code).currentText(),replace)
    def convertNormal(self,inf,outf,form,replace):
        try:
            nmRemap(inf,inf,invert=self.ui.invertNM.checkState())
        except Exception as e:
            self.ui.console.append("Failure to convert %s: %s"%(inf,e))
            return
        self.convert(inf,outf,form,replace)
    def convert(self,inf,outf,form,replace):
        self.ui.console.update()
        self.ui.console.append("Converting %s"%inf)
        try:
            convert(inf,form,outf,output = self.ui.console.append if self.ui.debug.checkState() else False)
            ifname = outf / (inf.stem+".tex")
            ofname = outf / replace(inf.stem+".tex")
            os.replace(ifname,ofname)
            os.remove(ifname.with_suffix(".dds"))                
            return True
        except Exception as e:
            self.ui.console.append("Failure to convert %s: %s"%(inf,e))
            raise
            return False
        #filepath.parent / (filepath.stem + string + filepath.suffix)
    def rename(self):
        if not self.ui.output.text():
            if not self.ui.input.text():
                return
            folder = self.ui.input.text()
        else:
            folder = self.ui.output.text()
        for file in Path(folder).glob("*.tex"):
            os.replace(file, str(file.parent/(file.stem.replace(self.ui.find.text(),self.ui.replace.text())+file.suffix)))
        self.ui.console.append("Replaced all instances of %s in tex files to %s"%(self.ui.find.text(),self.ui.replace.text()))
            
    def add(self,paths,form):
        dialog = QFileDialog.getOpenFileName(self, "Open %s"%form, "", "%s Texture File (*.%s)"%(form,form))[0]
        if dialog:
            item = QtWidgets.QListWidgetItem(dialog)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.addItem(item,paths)
        return dialog
    def addItem(self,item,paths):
        paths.addItem(item)
    def delete(self,paths):
        if paths.currentRow() == -1:
            # no selection. delete last row
            row_num = paths.count() - 1
        else:
            row_num = paths.currentRow()
        item = paths.takeItem(row_num)
        del item
    def moveUp(self,paths):
        row_num = paths.currentRow()
        if row_num > 0:            
            row = paths.itemWidget(paths.currentItem())
            itemN = paths.currentItem().clone()
            paths.insertItem(row_num -1, itemN)
            paths.setItemWidget(itemN, row)
            paths.takeItem(row_num+1)
            paths.setCurrentRow(row_num-1)
    def moveDown(self,paths):
        row_num = paths.currentRow()
        if row_num == -1:
            # no selection. abort
            return
        elif row_num < paths.count()-1:
            row = paths.itemWidget(paths.currentItem())
            itemN = paths.currentItem().clone()
            paths.insertItem(row_num + 2, itemN)
            paths.setItemWidget(itemN, row)
            paths.takeItem(row_num)
            paths.setCurrentRow(row_num+1)   
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    args = app.arguments()[1:]
    window = MainWindow(args)
    sys.exit(app.exec_())
    