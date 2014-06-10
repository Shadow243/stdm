# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import shutil
import platform
from exceptions import NameError
FILE="stdmConfig.xml"
htmlLICENSE="license.htm"
LICENSE="LICENSE.txt"
HTML="stdm_schema.html"
SQL="stdmConfig.sql"
CONFIG="Config"
HELP="stdm.chm"
xmldoc=os.path.dirname(os.path.abspath(__file__))
#from stdm.config import activeProfile
from stdm.settings import RegistryConfig

class FilePaths(object):
    def __init__(self, path=None):
        self._file=xmldoc
        self.baseDir=None
        self._html=''
        self._sql=''
        self.userPath=None
        self.actualPath=None
        self.config = RegistryConfig()
        #try:
        self.checkPreviousSetting()
        #except:
            #pass
    
    def checkPreviousSetting(self):    
        self.defaultConfigPath()
        try:
            pathSettings=self.config.read([CONFIG])
            if pathSettings:
                self.setUserConfigPath(pathSettings[CONFIG])
            else:
                self.setUserConfigPath()
        except Exception as ex:
            pass
                        
    def XMLFile(self):
        #this function returns the default xml file with configuration
        #self.setConfigPath()
        return self._file

    def cacheFile(self):
        #To implemented a backup file for comparing edits everytime the user makes changes
        path=self.userPath+'/temp/%s'%FILE
        return path
    
    def cachePath(self):
        return self.userPath+'/temp'

    def STDMSettingsPath(self):
        #To be implemented to write new file with user edits
        
        pass
    
    def HtmlFile(self):
        #Read the html representation of the schema
        self._html=self.userPath+'/%s'%HTML
        return self._html
    
    def SQLFile(self):
        #Read the html representation of the schema
        self._sql=self.userPath+'/%s'%SQL
        return self._sql
    
    def baseSQLPath(self):
        path= self.baseDir+'/%s'%FILE
        #path=self.userPath+'/temp/%s'%FILE
        return path
    
    def HelpContents(self):
        return self.actualPath+'/%s'%HELP
        
    def defaultConfigPath(self):
        '''returns the path with configuration file'''
        basePath=str(self._file).rfind("\\")
        actualPath=str(self._file)[:basePath]
        self.actualPath=actualPath
        self.baseDir=actualPath+"/template/"
        self._file=self.baseDir+FILE        
    
    def setUserConfigPath(self,path=None):
        ''' set new path with user configuration'''
        #self.defaultConfigPath()
        self.userPath=self.localPath()
        self.createDir(self.userPath)
        cachePath=self.userPath+'/temp'
        self.createDir(cachePath)
        self.userConfigPath()
    
    def userConfigPath(self,path=None):
        #Copy template files to the user directory
        try:
            for fileN in [FILE,HTML,SQL]:
                if not os.path.isfile(self.userPath+'/%s'%fileN):
                    baseFile=self.baseDir +'/%s'%fileN
                    shutil.copy(baseFile,self.userPath)
        except IOError as ex:
            raise ex
    
    def setUserXMLFile(self):
        '''default path to the config file'''
        xml=self.userPath+'/%s'%FILE
        return xml
    
    def localPath(self):
        '''look for users path based on platform, need to implement for unix systems'''
        profPath=None
        if platform.system() == "Windows":
            userPath = os.environ["USERPROFILE"]
            profPath = userPath + "/.stdm"
        return str(profPath).replace("\\", "/")
    
    def setLocalPath(self,path=None):
        if path:
            self.userPath=path
        if not path:
            self.userPath=self.localPath()
            
    def createDir(self,dirPath):
        if os.access(dirPath, os.F_OK)==False:
            os.makedirs(dirPath)    
            return dirPath
     
    
    def STDMLicenseDoc(self):
        '''load STDM license file for viewing'''
        self.licPath=self.actualPath+'/%s'%LICENSE
        return self.actualPath+'/%s'%LICENSE
        
    def createBackupSettings(self):
        '''incase the user want to keep track of the old file when current file changes'''
        if os.path.isfile(self.cacheFile()):
            os.remove(self.cacheFile())
        shutil.copy(self.setUserXMLFile(), self.cachePath())
        
            
    