#----------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2021-2022 5@xes
# 
# UniversalCuraSettings is released under the terms of the AGPLv3 or higher.
#
# Version 0.0.1  :  First prototype
# Version 0.0.2  :  Add the choice of the Nozzle Size
# Version 0.0.3  :  New options in the different Intent
# Version 0.0.5  :  Change the name back to Universal Cura Settings
# Version 0.0.6  :  test 01-05-2021
# Version 0.0.7  :  Creation Top Surface settings
# Version 0.0.8  :  Mechanical settings, test parts : Customizable nail clamp https://www.thingiverse.com/thing:4816588
# Version 0.0.9  :  Modification Standard
# Version 0.0.10 :  Modification Figurine
# Version 0.0.11 :  Modification Figurine
# Version 0.0.12 :  Add Support intent
# Version 0.0.13 :  vase
# Version 0.0.14 :  Update xy_offset_layer_0
# Version 0.0.15 :  Extruder type : unknow -> no modification of the retract parameter
#                   Nozzle Size : Not specified -> no modification of the nozzle diameter
#                   Material : unknow -> no modification of the temperature parameter
# Version 0.0.16 :  New test and parameters
# Version 0.0.17 :  https://github.com/5axes/UniversalCuraSettings/issues/25
# Version 0.0.18 :  Change on Support creation https://github.com/5axes/UniversalCuraSettings/discussions/22#discussioncomment-2177352
#                   New Save Material Intent
# Version 0.0.19 :  Change on Save Material
# Version 0.0.20 :  Add Extra Quality 
#
# Version 0.1.0  :  Update Cura 5.0
# Version 0.1.1  :  Update Cura 5.0
# Version 0.1.2  :  Change comment in the log file And Add self.StandardFixed = 0  
# Version 0.1.3  :  Intent modification for Cura 5.0
#----------------------------------------------------------------------------------------------------------------------


VERSION_QT5 = False
try:
    from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt6.QtGui import QDesktopServices
    from PyQt6.QtWidgets import QFileDialog, QMessageBox
except ImportError:
    from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
    from PyQt5.QtGui import QDesktopServices
    from PyQt5.QtWidgets import QFileDialog, QMessageBox
    VERSION_QT5 = True



from UM.Extension import Extension
from UM.PluginRegistry import PluginRegistry
from UM.Application import Application
from cura.CuraApplication import CuraApplication
from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Version import Version

import os
import platform
import os.path
import sys
import re
import math

from datetime import datetime
# from typing import cast, Dict, List, Optional, Tuple, Any, Set

# Code from Aldo Hoeben / fieldOfView for this tips
try:
    import csv
except ImportError:
    # older versions of Cura somehow ship with a python version that does not include
    # this file, so a local copy is supplied as a fallback
    # thanks to Aldo Hoeben / fieldOfView for this tips
    from . import csv

from UM.Extension import Extension
from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

class UniversalCuraSettings(Extension, QObject,):
  
    # The QT signal, which signals an update for user information text
    userInfoTextChanged = pyqtSignal()
    userModeChanged = pyqtSignal()
    
    
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)
        
        self._Section =""

        #Initialize variables
        self._continueDialog = None
        self._mode = "standard"
        self._extruder = "unknow"
        self._material = "unknow"
        self._nozzle = "0.4"
        self.StandardFixed=0
        
        # set the preferences to store the default value
        self._application = Application.getInstance()
        self._preferences = self._application.getPreferences()
        self._preferences.addPreference("UniversalCuraSettings/dialog_path", "")
        self._preferences.addPreference("UniversalCuraSettings/mode", "standard")
        self._preferences.addPreference("UniversalCuraSettings/extruder", "unknow")
        self._preferences.addPreference("UniversalCuraSettings/material", "unknow")
        self._preferences.addPreference("UniversalCuraSettings/nozzle", "0.4")

        
        # Mode
        self._mode = self._preferences.getValue("UniversalCuraSettings/mode")
        # Extruder type
        self._extruder= self._preferences.getValue("UniversalCuraSettings/extruder") 
        # Material type
        self._material= self._preferences.getValue("UniversalCuraSettings/material")
        # Nozzle size
        self._nozzle= self._preferences.getValue("UniversalCuraSettings/nozzle")
        
        # Test version for futur release 4.9 or Arachne
        self.Major=1
        self.Minor=0

        # Test version for futur release 4.9
        # Logger.log('d', "Info Version CuraVersion --> " + str(Version(CuraVersion)))
        Logger.log('d', "Info CuraVersion --> " + str(CuraVersion))        
        
        #if "master" in CuraVersion or "beta" in CuraVersion or "BETA" in CuraVersion:
        if "master" in CuraVersion:
            # Master is always a developement version.
            self.Major=4
            self.Minor=13  
        else:
            try:
                self.Major = int(CuraVersion.split(".")[0])
                self.Minor = int(CuraVersion.split(".")[1])
                # Logger.log('d', "Info Major --> " + str(self.Major)) 
                # Logger.log('d', "Info Minor --> " + str(self.Minor)) 
            except:
                pass
 
        # Shortcut
        if VERSION_QT5:
            self._qml_folder = "qml_qt5" 
        else:
            self._qml_folder = "qml_qt6" 

        self._qml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._qml_folder, "UniversalCuraSettings.qml")

        
        # Thanks to Aldo Hoeben / fieldOfView for this code
        # QFileDialog.Options
        if VERSION_QT5:
            self._dialog_options = QFileDialog.Options()
            if sys.platform == "linux" and "KDE_FULL_SESSION" in os.environ:
                self._dialog_options |= QFileDialog.DontUseNativeDialog
        else:
            self._dialog_options = None

        self.setMenuName(catalog.i18nc("@item:inmenu", "Universal Settings"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set Universal Settings"), self.setDefProfile)
        self.addMenuItem("", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Export current profile"), self.exportData)
        self.addMenuItem(" ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Merge a profile"), self.importData)

        #Initialize variables
        self._continueDialog = None
 
    #===== Text Output ===================================================================================================
    # Writes the message to the log, includes timestamp, length is fixed
    def writeToLog(self, str):
        Logger.log("d", "Universal Cura Settings = %s", str)
        
    #==== User Input =====================================================================================================
    def setDefProfile(self) -> None:
        if self._continueDialog is None:
            self._continueDialog = self._createDialogue()
        self._continueDialog.show()
        
    @pyqtProperty(str, notify= userModeChanged)
    def modeInput(self):
        return str(self._mode) 
 
    @pyqtProperty(str, notify= userModeChanged)
    def extruderInput(self):
        return str(self._extruder) 

    @pyqtProperty(str, notify= userModeChanged)
    def materialInput(self):
        return str(self._material)  

    @pyqtProperty(str, notify= userModeChanged)
    def nozzleInput(self):
        return str(self._nozzle)
        
    #This method builds the dialog from the qml file and registers this class
    #as the manager variable
    def _createDialogue(self):
        # qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "UniversalCuraSettings.qml")
        component_with_context = Application.getInstance().createQmlComponent(self._qml_path, {"manager": self})
        return component_with_context
 
    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def nozzleEntered(self, text) -> None:
        self._nozzle = text

        # self.writeToLog("Set UniversalCuraSettings/Nozzle set to : " + text)
        self._preferences.setValue("UniversalCuraSettings/nozzle", self._nozzle)
        
    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def modeEntered(self, text) -> None:
        self._mode = text

        # self.writeToLog("Set UniversalCuraSettings/Mode set to : " + text)
        self._preferences.setValue("UniversalCuraSettings/mode", self._mode)

    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def materialEntered(self, text) -> None:
        self._material = text

        # self.writeToLog("Set UniversalCuraSettings/Material set to : " + text)
        self._preferences.setValue("UniversalCuraSettings/material", self._material)

    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def extruderEntered(self, text) -> None:
        self._extruder = text

        # self.writeToLog("Set UniversalCuraSettings/Extruder set to : " + text)
        self._preferences.setValue("UniversalCuraSettings/extruder", self._extruder) 

    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def modeApply(self, text) -> None:
        self._mode = text
        self.setProfile() 
        #self.writeToLog("Mode Apply to : " + text)
        
    #==== Previous code for Export/Import CSV =====================================================================================================    
    def exportData(self) -> None:
        # thanks to Aldo Hoeben / fieldOfView for this part of the code
        file_name = ""
        if VERSION_QT5:
            file_name = QFileDialog.getSaveFileName(
                parent = None,
                caption = catalog.i18nc("@title:window", "Save as"),
                directory = self._preferences.getValue("import_export_tools/dialog_path"),
                filter = "CSV files (*.csv)",
                options = self._dialog_options
            )[0]
        else:
            dialog = QFileDialog()
            dialog.setWindowTitle(catalog.i18nc("@title:window", "Save as"))
            dialog.setDirectory(self._preferences.getValue("import_export_tools/dialog_path"))
            dialog.setNameFilters(["CSV files (*.csv)"])
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            if dialog.exec():
                file_name = dialog.selectedFiles()[0]

        if not file_name:
            Logger.log("d", "No file to export selected")
            return

        self._preferences.setValue("UniversalCuraSettings/dialog_path", os.path.dirname(file_name))
        # -----
        
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        #Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        
        exported_count = 0
        try:
            with open(file_name, 'w', newline='') as csv_file:
                # csv.QUOTE_MINIMAL  or csv.QUOTE_NONNUMERIC ?
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                # E_dialect = csv.get_dialect("excel")
                # csv_writer = csv.writer(csv_file, dialect=E_dialect)
                
                csv_writer.writerow([
                    "Section",
                    "Extruder",
                    "Key",
                    "Type",
                    "Value"
                ])
                 
                # Date
                self._WriteRow(csv_writer,"general",0,"Date","str",datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                # Platform
                self._WriteRow(csv_writer,"general",0,"Os","str",str(platform.system()) + " " + str(platform.version())) 
                # Version  
                self._WriteRow(csv_writer,"general",0,"Cura_Version","str",CuraVersion)
                # Profile
                P_Name = global_stack.qualityChanges.getMetaData().get("name", "")
                self._WriteRow(csv_writer,"general",0,"Profile","str",P_Name)
                # Quality
                Q_Name = global_stack.quality.getMetaData().get("name", "")
                self._WriteRow(csv_writer,"general",0,"Quality","str",Q_Name)
                # Extruder_Count
                self._WriteRow(csv_writer,"general",0,"Extruder_Count","int",str(extruder_count))
                
                # Material
                extruders = list(global_stack.extruders.values())  
 
                # Define every section to get the same order as in the Cura Interface
                # Modification from global_stack to extruders[0]
                i=0
                for Extrud in list(global_stack.extruders.values()):    
                    i += 1                        
                    self._doTree(Extrud,"resolution",csv_writer,0,i)
                    self._doTree(Extrud,"shell",csv_writer,0,i)
                    # New section Arachne and 4.9 ?
                    if self.Major > 4 or ( self.Major == 4 and self.Minor >= 9 ) :
                        self._doTree(Extrud,"top_bottom",csv_writer,0,i)
                    self._doTree(Extrud,"infill",csv_writer,0,i)
                    self._doTree(Extrud,"material",csv_writer,0,i)
                    self._doTree(Extrud,"speed",csv_writer,0,i)
                    self._doTree(Extrud,"travel",csv_writer,0,i)
                    self._doTree(Extrud,"cooling",csv_writer,0,i)
                    # If single extruder doesn't export the data
                    if extruder_count>1 :
                        self._doTree(Extrud,"dual",csv_writer,0,i)
                        
                    self._doTree(Extrud,"support",csv_writer,0,i)
                    self._doTree(Extrud,"platform_adhesion",csv_writer,0,i)                   
                    self._doTree(Extrud,"meshfix",csv_writer,0,i)             
                    self._doTree(Extrud,"blackmagic",csv_writer,0,i)
                    self._doTree(Extrud,"experimental",csv_writer,0,i)
                    
                    # machine_settings
                    self._Section ="machine_settings"
                    # self._doTree(Extrud,"machine_nozzle_size",csv_writer,0,i)
                    
        except:
            Logger.logException("e", "Could not export profile to the selected file")
            return

        Message().hide()
        Message("Exported data for profil %s" % P_Name, title = "Import Export CSV Profiles Tools").show()

    def _WriteRow(self,csvwriter,Section,Extrud,Key,KType,ValStr):
        
        csvwriter.writerow([
                     Section,
                     "%d" % Extrud,
                     Key,
                     KType,
                     str(ValStr)
                ])
               
    def _doTree(self,stack,key,csvwriter,depth,extrud):   
        #output node     
        Pos=0
        if stack.getProperty(key,"type") == "category":
            self._Section=key
        else:
            if stack.getProperty(key,"enabled") == True:
                GetType=stack.getProperty(key,"type")
                GetVal=stack.getProperty(key,"value")
                
                if str(GetType)=='float':
                    # GelValStr="{:.2f}".format(GetVal).replace(".00", "")  # Formatage
                    GelValStr="{:.4f}".format(GetVal).rstrip("0").rstrip(".") # Formatage
                else:
                    # enum = Option list
                    if str(GetType)=='enum':
                        definition_option=key + " option " + str(GetVal)
                        get_option=str(GetVal)
                        GetOption=stack.getProperty(key,"options")
                        GetOptionDetail=GetOption[get_option]
                        GelValStr=str(GetVal)
                        # Logger.log("d", "GetType_doTree = %s ; %s ; %s ; %s",definition_option, GelValStr, GetOption, GetOptionDetail)
                    else:
                        GelValStr=str(GetVal)
                
                self._WriteRow(csvwriter,self._Section,extrud,key,str(GetType),GelValStr)
                depth += 1

        #look for children
        if len(CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children) > 0:
            for i in CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children:       
                self._doTree(stack,i.key,csvwriter,depth,extrud)       
                
    def importData(self) -> None:
        # thanks to Aldo Hoeben / fieldOfView for this part of the code
        file_name = ""
        if VERSION_QT5:
            file_name = QFileDialog.getOpenFileName(
                parent = None,
                caption = catalog.i18nc("@title:window", "Open File"),
                directory = self._preferences.getValue("import_export_tools/dialog_path"),
                filter = "CSV files (*.csv)",
                options = self._dialog_options
            )[0]
        else:
            dialog = QFileDialog()
            dialog.setWindowTitle(catalog.i18nc("@title:window", "Open File"))
            dialog.setDirectory(self._preferences.getValue("import_export_tools/dialog_path"))
            dialog.setNameFilters(["CSV files (*.csv)"])
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            if dialog.exec():
                file_name = dialog.selectedFiles()[0]

        if not file_name:
            Logger.log("d", "No file to import from selected")
            return

        self._preferences.setValue("import_export_tools/dialog_path", os.path.dirname(file_name))
        # -----
        
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()
        global_stack = machine_manager.activeMachine

        #Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        
        extruders = list(global_stack.extruders.values())   
        
        imported_count = 0
        CPro = ""
        try:
            with open(file_name, 'r', newline='') as csv_file:
                C_dialect = csv.Sniffer().sniff(csv_file.read(1024))
                # Reset to begining file position
                csv_file.seek(0, 0)
                Logger.log("d", "Csv Import %s : Delimiter = %s Quotechar = %s", file_name, C_dialect.delimiter, C_dialect.quotechar)
                # csv.QUOTE_MINIMAL  or csv.QUOTE_NONNUMERIC ?
                # csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_reader = csv.reader(csv_file, dialect=C_dialect)
                line_number = -1
                for row in csv_reader:
                    line_number += 1
                    if line_number == 0:
                        if len(row) < 4:
                            continue         
                    else:
                        # Logger.log("d", "Import Data = %s | %s | %s | %s | %s",row[0], row[1], row[2], row[3], row[4])
                        try:
                            #(section, extrud, kkey, ktype, kvalue) = row[0:4]
                            section=row[0]
                            extrud=int(row[1])
                            extrud -= 1
                            kkey=row[2]
                            ktype=row[3]
                            kvalue=row[4]
                            
                            #Logger.log("d", "Current Data = %s | %d | %s | %s | %s", section,extrud, kkey, ktype, kvalue)  
                            if extrud<extruder_count:
                                try:
                                    container=extruders[extrud]
                                    try:
                                        prop_value = container.getProperty(kkey, "value")
                                        if prop_value != None :
                                            
                                            settable_per_extruder= container.getProperty(kkey, "settable_per_extruder")
                                            # Logger.log("d", "%s settable_per_extruder : %s", kkey, str(settable_per_extruder))
                                            
                                            if ktype == "str" or ktype == "enum":
                                                if prop_value != kvalue :
                                                    if extrud == 0 : stack.setProperty(kkey,"value",kvalue)
                                                    if settable_per_extruder == True : 
                                                        container.setProperty(kkey,"value",kvalue)
                                                        Logger.log("d", "prop_value changed: %s = %s / %s", kkey ,kvalue, prop_value)
                                                    else:
                                                        Logger.log("d", "%s not settable_per_extruder", kkey)
                                                    imported_count += 1
                                                    
                                            elif ktype == "bool" :
                                                if kvalue == "True" or kvalue == "true" :
                                                    C_bool=True
                                                else:
                                                    C_bool=False
                                                
                                                if prop_value != C_bool :
                                                    if extrud == 0 : stack.setProperty(kkey,"value",C_bool)
                                                    if settable_per_extruder == True : 
                                                        container.setProperty(kkey,"value",C_bool)
                                                        Logger.log("d", "prop_value changed: %s = %s / %s", kkey ,C_bool, prop_value)
                                                    else:
                                                        Logger.log("d", "%s not settable_per_extruder", kkey)
                                                    imported_count += 1
                                                    
                                            elif ktype == "int" :
                                                if prop_value != int(kvalue) :
                                                    if extrud == 0 : stack.setProperty(kkey,"value",int(kvalue))
                                                    if settable_per_extruder == True :
                                                        container.setProperty(kkey,"value",int(kvalue))
                                                        Logger.log("d", "prop_value changed: %s = %s / %s", kkey ,kvalue, prop_value)
                                                    else:
                                                        Logger.log("d", "%s not settable_per_extruder", kkey)
                                                    imported_count += 1
                                            
                                            elif ktype == "float" :
                                                TransVal=round(float(kvalue),4)
                                                if round(prop_value,4) != TransVal :
                                                    if extrud == 0 : stack.setProperty(kkey,"value",TransVal)
                                                    if settable_per_extruder == True : 
                                                        container.setProperty(kkey,"value",TransVal)
                                                        Logger.log("d", "prop_value changed: %s = %s / %s", kkey ,TransVal, prop_value)
                                                    else:
                                                        Logger.log("d", "%s not settable_per_extruder", kkey)
                                                    imported_count += 1
                                            else :
                                                Logger.log("d", "Value type Else = %d | %s | %s | %s",extrud, kkey, ktype, kvalue)
                                        else:
                                            # Logger.log("d", "Value None = %d | %s | %s | %s",extrud, kkey, ktype, kvalue)
                                            if kkey=="Profile" :
                                                CPro=kvalue
                                                
                                    except:
                                        Logger.log("e", "Error kkey: %s" % kkey)
                                        continue                                       
                                except:
                                    Logger.log("e", "Error Extruder: %s" % row)
                                    continue                             
                        except:
                            Logger.log("e", "Row does not have enough data: %s" % row)
                            continue
                            
        except:
            Logger.logException("e", "Could not import settings from the selected file")
            return

        Message().hide()
        Message("Imported profil %d changed keys from %s" % (imported_count, CPro) , title = "Import Export CSV Profiles Tools").show()

    def _getValue(self,key) -> str:
        
        stack = CuraApplication.getInstance().getGlobalContainerStack()
        
        # settable_per_extruder
        # type 
        GetType=stack.getProperty(key,"type")
        GetVal=stack.getProperty(key,"value")
        GetExtruder=stack.getProperty(key,"settable_per_extruder")
        
        if str(GetType)=='float':
            # GelValStr="{:.2f}".format(GetVal).replace(".00", "")  # Formatage
            GelValStr="{:.4f}".format(GetVal).rstrip("0").rstrip(".") # Formatage thanks to r_moeller
        else:
            # enum = Option list
            if str(GetType)=='enum':
                definition_option=key + " option " + str(GetVal)
                get_option=str(GetVal)
                GetOption=stack.getProperty(key,"options")
                GetOptionDetail=GetOption[get_option]
                # GelValStr=i18n_catalog.i18nc(definition_option, GetOptionDetail)
                GelValStr=GetOptionDetail
                # Logger.log("d", "GetType_doTree = %s ; %s ; %s ; %s",definition_option, GelValStr, GetOption, GetOptionDetail)
            else:
                GelValStr=str(GetVal)      
        
        return GelValStr
        
    def _setValue(self,key,c_val) -> int:
        # self.writeToLog("setValue key : " + key)
        machine_manager = CuraApplication.getInstance().getMachineManager()  
        stack = CuraApplication.getInstance().getGlobalContainerStack()
        
        # settable_per_extruder
        # type 
        GetType=stack.getProperty(key,"type")
        GetVal=stack.getProperty(key,"value")
        GetExtruder=stack.getProperty(key,"settable_per_extruder")

                   
        if GetExtruder == True:
            global_stack = machine_manager.activeMachine
            # extruders = list(global_stack.extruders.values()) 
            extruder_stack = CuraApplication.getInstance().getExtruderManager().getActiveExtruderStacks()            
            for Extrud in extruder_stack:
                PosE = int(Extrud.getMetaDataEntry("position"))
                PosE += 1
                GetVal= Extrud.getProperty(key,"value")
                if GetVal != c_val :
                    Extrud.setProperty(key,"value",c_val)
                    text_message = "setValue Extruder " + str(PosE)
                    text_message += " : "
                    text_message += key
                    text_message += " : "
                    self.writeToLog(text_message + str(c_val))
                    modified_c = 1
                else:
                    modified_c = 0                
        else:
            if GetVal != c_val : 
                stack.setProperty(key,"value",c_val)
                text_message = "setValue   Global   : "
                text_message += key
                text_message += " : "                
                self.writeToLog(text_message + str(c_val)) 
                modified_c = 1            
            else:
                modified_c = 0
        
        return modified_c
    
    # Layer_Height according to machine_nozzle_size & self._mode
    # if not defined = 0 then the value will be not set by the plugin
    def _defineLayer_Height(self,c_val) -> float:
 
        self.writeToLog("------------------------------------------")
        self.writeToLog("| defineLayer_Height type    : " + str(self._mode) + " |")
        self.writeToLog("------------------------------------------")
        
        layer_height = 0.5 * c_val
         # Profile Mode settings
        if self._mode == "standard" :
            layer_height = 0.5 * c_val
            
        elif self._mode == "mechanical" :
            layer_height = 0.5 * c_val    
        
        elif self._mode == "figurine" :
            layer_height = 0.3 * c_val

        elif self._mode == "small part" :
            layer_height = 0.4 * c_val
            
        elif self._mode == "prototype" :
            layer_height = 0.6 * c_val
            
        else:
            layer_height = 0  
        
        self.writeToLog("layer_height defined : " + str(layer_height))
        return layer_height

    # Line_Width according to machine_nozzle_size & self._mode
    def _defineLine_Width(self,c_val) -> float:
    
        self.writeToLog("------------------------------------------")
        self.writeToLog("| defineLine_Width type    : " + str(self._mode) + " |")
        self.writeToLog("------------------------------------------")
        
        line_width = c_val
         # Profile Mode settings
        if self._mode == "standard" :
            layer_height = c_val
            
        elif self._mode == "figurine" :
            layer_height = c_val
            
        elif self._mode == "prototype" :
            line_width = 1.075 * c_val
            
        elif self._mode == "vase" :
            line_width = 1.075 * c_val
            
        else:
            line_width = c_val   
        
        self.writeToLog("Line_Width defined : " + str(line_width))
        
        return line_width

    # Material_Print_Temperature according to machine_nozzle_size & self._material
    def _defineMaterial_Print_Temperature(self,c_val) -> float:
        self.writeToLog("--------------------------------------------")
        self.writeToLog("| Material_print_temperature type    : " + str(self._material) + " |")
        self.writeToLog("--------------------------------------------")
        material_print_temperature = 200
         # Profile Mode settings
        if self._material == "pla" :
            material_print_temperature = 205 + round(c_val*12.5,0)

        elif self._material == "tpu" :
            material_print_temperature = 205 + round(c_val*12.5,0)
            
        elif self._material == "abs" :
            material_print_temperature = 225 + round(c_val*12.5,0)
            
        elif self._material == "petg" :
            material_print_temperature = 220 + round(c_val*12.5,0)
                        
        else:
            material_print_temperature = self._getValue("material_print_temperature")  
        
        self.writeToLog("Material_print_temperature defined : " + str(material_print_temperature))
        
        return material_print_temperature
        
    #==== Define the Profile =====================================================================================================   
    # 
    # Global
    #---------------
    # "support"
    # "platform_adhesion"
    # "blackmagic"
    # "experimental"
    # "machine_settings"
    #
    # by extruder
    #---------------
    # "resolution"
    # "shell"
    # New section Arachne and 4.9 ?
    # if VersC > 4.8:
    # 	"top_bottom"
    # "infill"
    # "material"
    # "speed"
    # "travel"
    # "cooling"
    # "dual"support_top_distance
    # "meshfix"		    
    def setProfile(self) -> None:
        self.writeToLog("Cura current release       : " + str(self.Major) + "." + str(self.Minor) )
        self.writeToLog("With Profile Mode          : " + self._mode)
        self.writeToLog("With Extruder Mode         : " + self._extruder)
        self.writeToLog("With Material              : " + self._material)
        self.writeToLog("With Nozzle Size           : " + self._nozzle)
        
        # Settyings from the interface
        currMode = self._mode
        currExtruder = self._extruder
        currMaterial = self._material
        currNozzle = self._nozzle
        modified_count = 0 
        
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        # Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        # Profile
        P_Name = global_stack.qualityChanges.getMetaData().get("name", "")
        # Quality
        Q_Name = global_stack.quality.getMetaData().get("name", "")

        # Get machine_nozzle_size and modify according to the 
        machine_nozzle_size=stack.getProperty("machine_nozzle_size", "value")
        self.writeToLog("Actual machine_nozzle_size : " + str(machine_nozzle_size))
        
        if currNozzle != "not specified" :
            if float(currNozzle) != machine_nozzle_size:
                machine_nozzle_size=float(currNozzle)
                modified_count += self._setValue("machine_nozzle_size",machine_nozzle_size)
            
        #------------------------------------------------------
        # Extruder get Material (Useless for the moment )
        #------------------------------------------------------
        # extruders = list(global_stack.extruders.values())   
        extruder_stack = CuraApplication.getInstance().getExtruderManager().getActiveExtruderStacks()        
        for Extrud in extruder_stack:
            # Material
            M_Name = Extrud.material.getMetaData().get("material", "")
            self.writeToLog("Current extruders material : " + M_Name)
              
        #------------------
        # Global stack
        #------------------
        # Reinit
        if self.StandardFixed==0:
            self.writeToLog("--------------------------------------------------")
            self.writeToLog("| Universal Cura settings Init Global Parameters |")
            self.writeToLog("--------------------------------------------------")
            modified_count += self._setValue("magic_spiralize",False)

            # layer_height 
            cval=self._defineLayer_Height(machine_nozzle_size)
            if cval>0 :
                modified_count += self._setValue("layer_height",cval)
                modified_count += self._setValue("layer_height_0",round((cval+0.04),1))
            
            # General settings
            modified_count += self._setValue("adaptive_layer_height_threshold",250)
            modified_count += self._setValue("adaptive_layer_height_variation",0.03)
            modified_count += self._setValue("adhesion_type",'skirt')
            
            if self.Major > 4 or ( self.Major == 4 and self.Minor >= 12 ) :
                modified_count += self._setValue("retraction_combing",'no_outer_surfaces')
            else :
                modified_count += self._setValue("retraction_combing",'infill')          
            
            modified_count += self._setValue("speed_slowdown_layers",1)
            modified_count += self._setValue("support_enable",False)
            modified_count += self._setValue("support_type",'buildplate')
            modified_count += self._setValue("travel_retract_before_outer_wall",True)

            modified_count += self._setValue("skin_no_small_gaps_heuristic",False)
            
            modified_count += self._setValue("acceleration_enabled",True)
            modified_count += self._setValue("acceleration_infill",1000)
            modified_count += self._setValue("acceleration_print_layer_0",500)
            modified_count += self._setValue("acceleration_roofing",500)
            modified_count += self._setValue("acceleration_skirt_brim",500)
            modified_count += self._setValue("acceleration_support_infill",1000)
            modified_count += self._setValue("acceleration_topbottom",500)
            modified_count += self._setValue("acceleration_travel",1000)
            modified_count += self._setValue("acceleration_wall_0",500)
            modified_count += self._setValue("acceleration_wall_x",800)

            modified_count += self._setValue("jerk_enabled",True)
            modified_count += self._setValue("jerk_infill",15)
            modified_count += self._setValue("jerk_layer_0",8)
            modified_count += self._setValue("jerk_print_layer_0",8)
            modified_count += self._setValue("jerk_support",15)
            modified_count += self._setValue("jerk_roofing",8)
            modified_count += self._setValue("jerk_skirt_brim",8)
            modified_count += self._setValue("jerk_support_infill",15)
            modified_count += self._setValue("jerk_topbottom",8)
            modified_count += self._setValue("jerk_travel",20)
            modified_count += self._setValue("jerk_wall_0",8)
            modified_count += self._setValue("jerk_wall_x",10)
            
            modified_count += self._setValue("top_layers",5)
            modified_count += self._setValue("bottom_layers",5)
            # "Skin Removal Width"
            modified_count += self._setValue("bottom_skin_preshrink",1.2)
            modified_count += self._setValue("brim_line_count",10)
            
            modified_count += self._setValue("conical_overhang_angle",70)
            
            modified_count += self._setValue("cool_fan_enabled",True)
            modified_count += self._setValue("cool_fan_full_at_height",1)
            modified_count += self._setValue("cool_fan_full_layer",5)
            modified_count += self._setValue("cool_fan_speed",100)
            modified_count += self._setValue("cool_min_layer_time",5)
            modified_count += self._setValue("cool_min_speed",15)
            
            # https://github.com/5axes/UniversalCuraSettings/discussions/22#discussioncomment-2177352
            modified_count += self._setValue("gradual_support_infill_steps",0)
            # modified_count += self._setValue("gradual_support_infill_step_height",1.5)
            
            modified_count += self._setValue("infill_before_walls",False)
            modified_count += self._setValue("infill_enable_travel_optimization",True)
            modified_count += self._setValue("infill_line_width",0.5)
            
            modified_count += self._setValue("infill_pattern",'zigzag')
            
            modified_count += self._setValue("infill_wall_line_count",1)

            modified_count += self._setValue("ironing_enabled",False)
            modified_count += self._setValue("limit_support_retractions",False)


            modified_count += self._setValue("skirt_gap",8)
            modified_count += self._setValue("skirt_line_count",2)
            
            modified_count += self._setValue("small_feature_speed_factor",100)
            modified_count += self._setValue("small_feature_speed_factor_0",50)
            modified_count += self._setValue("small_hole_max_size",3.25)
            modified_count += self._setValue("small_feature_max_length",5)
            
            modified_count += self._setValue("speed_print",40)
            modified_count += self._setValue("speed_infill",60)
            modified_count += self._setValue("speed_layer_0",20)
            modified_count += self._setValue("speed_roofing",40)
            modified_count += self._setValue("speed_topbottom",60)
            modified_count += self._setValue("speed_travel",150)
            modified_count += self._setValue("speed_wall_0",30)
            modified_count += self._setValue("speed_wall_x",40)
            
            modified_count += self._setValue("support_enable",False)
            modified_count += self._setValue("support_structure",'normal')
            modified_count += self._setValue("support_type",'buildplate')
            modified_count += self._setValue("support_angle",67)
            modified_count += self._setValue("support_bottom_density",97)

            modified_count += self._setValue("support_roof_enable",True)
            modified_count += self._setValue("support_xy_overrides_z",'xy_overrides_z')
                  
            # modified_count += self._setValue("top_layers",7)
            modified_count += self._setValue("travel_avoid_distance",1)
            modified_count += self._setValue("travel_avoid_other_parts",True)
            modified_count += self._setValue("travel_avoid_supports",True)
            
            modified_count += self._setValue("travel_retract_before_outer_wall",True)
            
            modified_count += self._setValue("wall_line_count",3)
            
            # modified_count += self._setValue("wall_transition_angle",25)
            if self.Major < 5 :
                modified_count += self._setValue("wall_min_flow",15)
                modified_count += self._setValue("wall_min_flow_retract",True)
                modified_count += self._setValue("travel_compensate_overlapping_walls_0_enabled",False)
            
            modified_count += self._setValue("z_seam_relative",True)
            modified_count += self._setValue("z_seam_type",'sharpest_corner')
            # "Hide Seam"
            modified_count += self._setValue("z_seam_corner",'z_seam_corner_inner')
            
            modified_count += self._setValue("bridge_settings_enabled",True)
            # modified_count += self._setValue("xy_offset_layer_0",-0.0625*machine_nozzle_size)
            modified_count += self._setValue("xy_offset_layer_0",-0.125*machine_nozzle_size)
            
            # Settings according to value calculation
            _top_bottom_pattern = self._getValue("top_bottom_pattern")
            
            if _top_bottom_pattern != 'concentric':
                modified_count += self._setValue("skin_overlap",12)           
            else:
                modified_count += self._setValue("skin_overlap",16)

            _line_width = float(self._getValue("line_width"))
            modified_count += self._setValue("skin_line_width",_line_width)

            _material_flow = float(self._getValue("material_flow"))
            if self._material != "unknow" :
                modified_count += self._setValue("infill_material_flow",_material_flow)
            
            _speed_travel = float(self._getValue("speed_travel"))
            _speed_print = float(self._getValue("speed_print"))
            
            _support_brim_width = float(self._getValue("support_brim_width"))
            _skirt_brim_line_width = float(self._getValue("skirt_brim_line_width"))
            _initial_layer_line_width_factor = float(self._getValue("initial_layer_line_width_factor"))
            
            _support_brim_line_count = math.ceil(_support_brim_width / (_skirt_brim_line_width * _initial_layer_line_width_factor / 100.0))
            modified_count += self._setValue("support_brim_line_count",_support_brim_line_count)

            _support_interface_pattern=self._getValue("support_interface_pattern")

            _line_width = float(self._getValue("line_width"))
            _wall_line_width = float(self._getValue("wall_line_width"))
            _wall_line_width_0 = float(self._getValue("wall_line_width_0"))
            _wall_line_width_x = float(self._getValue("wall_line_width_x"))
            _wall_line_count = int(self._getValue("wall_line_count"))
            # skin_preshrink = wall_line_width_0 + ((wall_line_count - 1) * wall_line_width_x)
            _skin_preshrink = _wall_line_width_0 + (_wall_line_count * _wall_line_width_x)
            _layer_height= float(self._getValue("layer_height"))

            modified_count += self._setValue("infill_wipe_dist",round((_line_width*0.5),1))

            
            modified_count += self._setValue("support_roof_height",round((_layer_height*6),1))
            modified_count += self._setValue("support_roof_offset",round((_layer_height*3),1))
            modified_count += self._setValue("support_top_distance",_layer_height)

            modified_count += self._setValue("support_wall_count",1)
            modified_count += self._setValue("support_xy_distance",_line_width)
            modified_count += self._setValue("support_z_distance",_layer_height)
     
            modified_count += self._setValue("support_bottom_distance",_layer_height)
            modified_count += self._setValue("support_bottom_enable",True)
            modified_count += self._setValue("support_bottom_height",round((_layer_height*4),1))
            modified_count += self._setValue("support_brim_enable",True)
            modified_count += self._setValue("support_brim_width",3)       
            modified_count += self._setValue("support_infill_rate",7)
            modified_count += self._setValue("support_join_distance",3)
            modified_count += self._setValue("support_offset",round((_layer_height*3),1))
            
            modified_count += self._setValue("support_interface_enable",True)
            modified_count += self._setValue("support_interface_line_width",round((_line_width*1.3),1))
            
            modified_count += self._setValue("support_interface_pattern",'zigzag')
            modified_count += self._setValue("support_interface_skip_height",_layer_height)
            
            modified_count += self._setValue("optimize_wall_printing_order",True)
            modified_count += self._setValue("adaptive_layer_height_enabled",False)
            if self.Major < 5 :
                modified_count += self._setValue("filter_out_tiny_gaps",True)
            
            # modified_count += self._setValue("skin_monotonic",True)
            # modified_count += self._setValue("roofing_monotonic",True)

            #-------------------------
            # New parameters Cura 5.0
            #-------------------------
            if self.Major > 4 :
                self.writeToLog("-----------------------------")
                self.writeToLog("|    Parameters Cura 5.0    |")
                self.writeToLog("-----------------------------")
                # Wall Transition Length	            0.4	mm                  "wall_transition_length":
                modified_count += self._setValue("wall_transition_length",_line_width)
                # Wall Distribution Count	            1	                    "wall_distribution_count":
                # Wall Transitioning Threshold Angle	10	°                   "wall_transition_angle":
                # Wall Transitioning Filter Distance	100	mm                  "wall_transition_filter_distance":
                # Wall Transitioning Filter Margin	    0.1	mm                  "wall_transition_filter_deviation":      
                # Wall Ordering	                        Outside To Inside	    "inset_direction"
                #                                                               "inside_out": "Inside To Outside",
                #                                                               "outside_in": "Outside To Inside"
                modified_count += self._setValue("inset_direction",'inside_out')
                # Minimum Wall Line Width	            0.34	mm              "min_wall_line_width":
                val_calc=float(currNozzle) * 0.85
                modified_count += self._setValue("min_wall_line_width",round(val_calc,2))            
                # Minimum Even Wall Line Width	        0.34	mm              "min_even_wall_line_width":
                # Split Middle Line Threshold	        70	%                   "wall_split_middle_threshold":
                # Minimum Odd Wall Line Width	        0.34	mm              "min_odd_wall_line_width":
                # Add Middle Line Threshold	            85	%                   "wall_add_middle_threshold":
                # Minimum Feature Size	                0.1	mm                  "min_feature_size": 
                # Minimum Thin Wall Line Width	        0.34	mm              "min_bead_width":     
                # Flow Equalization Ratio	            100	%                   "speed_equalize_flow_width_factor":
                modified_count += self._setValue("speed_equalize_flow_width_factor",100)
                # Alternate Wall Directions	            False	                "material_alternate_walls":
                # Remove Raft Inside Corners	        False	                "raft_remove_inside_corners":
                # Raft Base Wall Count	                1                       "raft_base_wall_count":
                # Scale Fan Speed To 0-1	            False	                "machine_scale_fan_speed_zero_to_one":
                self.StandardFixed=1
 
        # Get actual values
        _top_bottom_pattern = self._getValue("top_bottom_pattern")
        _line_width = float(self._getValue("line_width"))
        _material_flow = float(self._getValue("material_flow"))            
        _speed_travel = float(self._getValue("speed_travel"))
        _speed_print = float(self._getValue("speed_print"))
        _support_brim_width = float(self._getValue("support_brim_width"))
        _skirt_brim_line_width = float(self._getValue("skirt_brim_line_width"))
        _initial_layer_line_width_factor = float(self._getValue("initial_layer_line_width_factor"))           
        _support_brim_line_count = self._getValue("support_brim_line_count")
        _support_interface_pattern=self._getValue("support_interface_pattern")
        _wall_line_width = float(self._getValue("wall_line_width"))
        _wall_line_width_0 = float(self._getValue("wall_line_width_0"))
        _wall_line_width_x = float(self._getValue("wall_line_width_x"))
        _wall_line_count = int(self._getValue("wall_line_count"))
        _layer_height= float(self._getValue("layer_height"))
        _skin_preshrink= float(self._getValue("skin_preshrink"))
            
        self.writeToLog("----------------------------------------")
        self.writeToLog("| Parameters Profile Mode : " + currMode + " |")
        self.writeToLog("----------------------------------------")
        # Profile Mode settings
        if currMode == "standard" : 
            modified_count += self._setValue("meshfix_union_all_remove_holes",False)
            if self.Major < 5 :
                modified_count += self._setValue("fill_perimeter_gaps",'nowhere')
            
            modified_count += self._setValue("retraction_enable",True)
            modified_count += self._setValue("roofing_layer_count",1)
            modified_count += self._setValue("skin_outline_count",0)
            
            modified_count += self._setValue("support_roof_pattern",_support_interface_pattern)
            modified_count += self._setValue("support_xy_distance_overhang",(machine_nozzle_size / 2))
        
            modified_count += self._setValue("support_roof_density",97)
            
            modified_count += self._setValue("retraction_hop_enabled",False)
            
            modified_count += self._setValue("support_use_towers",False)
            modified_count += self._setValue("support_tower_diameter",6)
            modified_count += self._setValue("support_tower_roof_angle",60)

            modified_count += self._setValue("meshfix_maximum_deviation",0.02)
            modified_count += self._setValue("meshfix_maximum_resolution",0.2)            

            modified_count += self._setValue("support_tree_angle",45)
            modified_count += self._setValue("support_tree_branch_diameter_angle",2.5)
            modified_count += self._setValue("support_tree_branch_distance",0.5)
            modified_count += self._setValue("support_tree_collision_resolution",0.15)
 
 
            # modified_count += self._setValue("top_thickness",1) 
            
            # must be set in relation with the line width
            _roofing_line_width = round((0.9 * _line_width),1)
            modified_count += self._setValue("roofing_line_width",_roofing_line_width)
            
            modified_count += self._setValue("infill_sparse_density",10)

            modified_count += self._setValue("max_skin_angle_for_expansion",90)
            modified_count += self._setValue("min_infill_area",10)
            modified_count += self._setValue("min_skin_width_for_expansion",0.1)

            modified_count += self._setValue("coasting_enable",False)
            modified_count += self._setValue("coasting_speed",100)
            modified_count += self._setValue("coasting_volume",0.02)
        
        elif currMode == "mechanical" :            
            modified_count += self._setValue("brim_line_count",10)
            modified_count += self._setValue("fill_outline_gaps",True)
            modified_count += self._setValue("wall_0_inset",0.02)
            
            modified_count += self._setValue("infill_sparse_density",15)
            
            modified_count += self._setValue("z_seam_corner",'z_seam_corner_weighted')
 
        elif currMode == "top surface" :  
            modified_count += self._setValue("ironing_enabled",True)
            modified_count += self._setValue("ironing_only_highest_layer",True)
            
            modified_count += self._setValue("jerk_ironing",17) 
            modified_count += self._setValue("ironing_flow",8.0)
            modified_count += self._setValue("ironing_inset",round((machine_nozzle_size *0.375),2))
            modified_count += self._setValue("ironing_line_spacing",round((machine_nozzle_size *0.375),2))
            modified_count += self._setValue("acceleration_ironing",1000)     
            # 30% Speed_print
            modified_count += self._setValue("speed_ironing",(_speed_print*1.3))

            modified_count += self._setValue("skin_monotonic",True)
            modified_count += self._setValue("roofing_monotonic",True)
            modified_count += self._setValue("ironing_monotonic",True)
        
        elif currMode == "extra quality" :  
            modified_count += self._setValue("top_layers",5)
            modified_count += self._setValue("bottom_layers",5)
            modified_count += self._setValue("wall_line_count",3)
            modified_count += self._setValue("speed_wall_0",25)
            modified_count += self._setValue("acceleration_wall_0",300)
            modified_count += self._setValue("jerk_wall_0",5)
            
        elif currMode == "save material" :
            modified_count += self._setValue("gradual_support_infill_steps",1)
            modified_count += self._setValue("gradual_support_infill_step_height",1.5)
            modified_count += self._setValue("top_layers",4)
            modified_count += self._setValue("bottom_layers",4)
            modified_count += self._setValue("wall_line_count",2)
            modified_count += self._setValue("infill_material_flow",80)
            modified_count += self._setValue("infill_wall_line_count",0)
            modified_count += self._setValue("infill_sparse_density",5)
            if self.Major < 5 :
                modified_count += self._setValue("fill_perimeter_gaps",'nowhere')
        
        elif currMode == "small part" :
            # Profile Mode settings
            modified_count += self._setValue("wall_line_count",4)
            # modified_count += self._setValue("outer_inset_first",True)
            modified_count += self._setValue("infill_sparse_density",20)
            
            modified_count += self._setValue("adhesion_type",'raft')
            modified_count += self._setValue("raft_margin",2)
            modified_count += self._setValue("raft_surface_layers",2)
            modified_count += self._setValue("raft_smoothing",4)
            # "default_value": 0.3 in fdmprinter.def.json ?
            modified_count += self._setValue("raft_airgap",_layer_height*1.3)
            
            modified_count += self._setValue("retraction_hop_enabled",True)
            
            modified_count += self._setValue("small_feature_speed_factor_0",20)
            modified_count += self._setValue("small_hole_max_size",6.0)

            
        elif currMode == "bed adhesion" :
            # Profile Mode settings
            modified_count += self._setValue("adhesion_type",'brim')
            
            modified_count += self._setValue("brim_line_count",15)
            modified_count += self._setValue("speed_layer_0",12)

            modified_count += self._setValue("small_feature_speed_factor_0",30)
            modified_count += self._setValue("small_hole_max_size",6.0)
            
            modified_count += self._setValue("initial_layer_line_width_factor",105)
            modified_count += self._setValue("jerk_layer_0",5)
            modified_count += self._setValue("jerk_print_layer_0",5)            
            modified_count += self._setValue("acceleration_print_layer_0",300)
            modified_count += self._setValue("acceleration_wall_0",300)
        
        elif currMode == "warping" :  
            
            modified_count += self._setValue("adhesion_type",'brim')
            modified_count += self._setValue("retraction_combing",'off')
            modified_count += self._setValue("retraction_combing_max_distance",33)
            modified_count += self._setValue("retraction_hop_enabled",True)
            modified_count += self._setValue("retraction_hop",_layer_height)
            modified_count += self._setValue("retraction_retract_speed",50)
            
            modified_count += self._setValue("speed_travel",100)
        
        elif currMode == "figurine" :
            # for fine details and good cooling ?
            modified_count += self._setValue("infill_sparse_density",8)
            
            modified_count += self._setValue("support_enable",True)
            if self.Major == 4 and self.minor < 7 :
                modified_count += self._setValue("support_tree_enable",True)
            modified_count += self._setValue("support_structure",'tree')   
            modified_count += self._setValue("support_tree_angle",45)
            
            
            modified_count += self._setValue("support_tree_branch_diameter",(_line_width*8))
            modified_count += self._setValue("support_tree_branch_diameter_angle",5)
            modified_count += self._setValue("support_tree_branch_distance",0.5)
            modified_count += self._setValue("support_tree_collision_resolution",0.15)            
            if self.Major < 5 :
                modified_count += self._setValue("fill_perimeter_gaps",'nowhere')
            
            modified_count += self._setValue("skin_outline_count",2)
            
            modified_count += self._setValue("brim_line_count",2)
            modified_count += self._setValue("wall_line_count",3)
            
            # Print Thin Walls
            modified_count += self._setValue("fill_outline_gaps",True)
            
            modified_count += self._setValue("speed_travel",100)
            modified_count += self._setValue("speed_layer_0",18)
            modified_count += self._setValue("support_interface_offset",round((_line_width*0.5),1))
            
            modified_count += self._setValue("z_seam_corner",'z_seam_corner_weighted')
 
            modified_count += self._setValue("retraction_hop_enabled",True)
            modified_count += self._setValue("retraction_hop",_layer_height) 
            
        elif currMode == "prototype" :
        
            modified_count += self._setValue("infill_sparse_density",10)
            
            # Fast and rought
            modified_count += self._setValue("wall_line_count",2)
            if self.Major < 5 :
                modified_count += self._setValue("fill_perimeter_gaps",'nowhere')
            
            modified_count += self._setValue("max_skin_angle_for_expansion",64)
            
            # "Top Surface Skin Layers"
            modified_count += self._setValue("roofing_layer_count",0)
            
            # modified_count += self._setValue("expand_skins_expand_distance",2)
            modified_count += self._setValue("skin_preshrink",_skin_preshrink)
                        
            modified_count += self._setValue("acceleration_enabled",True)
            modified_count += self._setValue("acceleration_infill",1000)
            modified_count += self._setValue("acceleration_ironing",1000)
            modified_count += self._setValue("acceleration_print_layer_0",500)
            modified_count += self._setValue("acceleration_roofing",500)
            modified_count += self._setValue("acceleration_skirt_brim",500)
            modified_count += self._setValue("acceleration_support_infill",1000)
            modified_count += self._setValue("acceleration_topbottom",1000)
            modified_count += self._setValue("acceleration_travel",1500)
            modified_count += self._setValue("acceleration_wall_0",500)
            modified_count += self._setValue("acceleration_wall_x",750)
        
            modified_count += self._setValue("jerk_enabled",True)
            modified_count += self._setValue("jerk_infill",15)
            modified_count += self._setValue("jerk_ironing",17.5)
            modified_count += self._setValue("jerk_layer_0",7.5)
            modified_count += self._setValue("jerk_print_layer_0",10)
            modified_count += self._setValue("jerk_support",15)
            modified_count += self._setValue("jerk_roofing",15)
            modified_count += self._setValue("jerk_skirt_brim",10)
            modified_count += self._setValue("jerk_support_infill",15)
            modified_count += self._setValue("jerk_topbottom",15)
            modified_count += self._setValue("jerk_travel",20)
            modified_count += self._setValue("jerk_wall_0",7.5)
            modified_count += self._setValue("jerk_wall_x",15)            
 
            modified_count += self._setValue("meshfix_maximum_deviation",0.04)
            modified_count += self._setValue("meshfix_maximum_resolution",0.4)

            modified_count += self._setValue("min_infill_area",0)
            modified_count += self._setValue("min_skin_width_for_expansion",0)
 
            modified_count += self._setValue("skirt_gap",2)
            modified_count += self._setValue("skirt_line_count",1)
        
        
        elif currMode == "support" :
            # Support
            modified_count += self._setValue("support_enable",True)
            modified_count += self._setValue("support_structure",'normal')
            modified_count += self._setValue("support_infill_rate",7)
            modified_count += self._setValue("support_material_flow",70)
            
            modified_count += self._setValue("minimum_support_area",8)
            
            modified_count += self._setValue("support_interface_enable",True)
            modified_count += self._setValue("support_roof_enable",True)
            modified_count += self._setValue("support_bottom_enable",False)
            
            modified_count += self._setValue("support_interface_density",30)
            modified_count += self._setValue("support_roof_density",90)
            modified_count += self._setValue("support_bottom_density",8)
            
            modified_count += self._setValue("support_wall_count",0)
            modified_count += self._setValue("support_type",'buildplate')
            modified_count += self._setValue("support_xy_overrides_z",'z_overrides_xy') # or xy_overrides_z
            
            modified_count += self._setValue("support_z_distance",round((_layer_height),1))
            modified_count += self._setValue("support_xy_distance",round((_line_width*2),1))
            
            modified_count += self._setValue("support_pattern",'lines')  # or zigzag

            modified_count += self._setValue("support_roof_height",round((_layer_height*6),1))
            modified_count += self._setValue("support_roof_offset",round((_layer_height*3),1))
            modified_count += self._setValue("support_top_distance",_layer_height)

            modified_count += self._setValue("support_bottom_distance",_layer_height)
            modified_count += self._setValue("support_bottom_height",round((_layer_height*4),1))
            modified_count += self._setValue("support_brim_enable",True)
            modified_count += self._setValue("support_brim_width",3)       
            modified_count += self._setValue("support_join_distance",3)
            modified_count += self._setValue("support_offset",round((_layer_height*3),1))

            modified_count += self._setValue("support_interface_line_width",round((_line_width*1.3),1))

            modified_count += self._setValue("support_interface_pattern",'zigzag')
            modified_count += self._setValue("support_interface_skip_height",_layer_height)
        
            
        elif currMode == "vase" :
            # Spiralize outer contour
            modified_count += self._setValue("magic_spiralize",True)
            
        else:
            modified_count += self._setValue("wall_line_count",3)

        _meshfix_maximum_resolution = float(self._getValue("meshfix_maximum_resolution"))
        _meshfix_maximum_travel_resolution = min(_meshfix_maximum_resolution * _speed_travel / _speed_print, 2 * _line_width)
        # modified_count += self._setValue("meshfix_maximum_travel_resolution",meshfix_maximum_travel_resolution) 

        # Profile Material settings
        modified_count += self._setValue("material_print_temperature",self._defineMaterial_Print_Temperature(machine_nozzle_size))
            
        if currMaterial != "unknow" :
            self.writeToLog("------------------------------")
            self.writeToLog("|  Material preset : " + currMaterial + "  |")
            self.writeToLog("------------------------------")        
            modified_count += self._setValue("material_flow",100)
        
        if currMaterial == "unknow" :
            # no modification
            self.writeToLog("------------------------------")
            self.writeToLog("|  Material preset : unknow  |")
            self.writeToLog("------------------------------")
            
        elif currMaterial == "pla" :
            modified_count += self._setValue("material_bed_temperature",55)
            modified_count += self._setValue("material_bed_temperature_layer_0",60)
            
        elif currMaterial == "abs" :
            modified_count += self._setValue("cool_fan_speed",0)
 
        elif currMaterial == "tpu" :
            modified_count += self._setValue("retraction_enable",False)
            modified_count += self._setValue("cool_fan_enabled",False)
            modified_count += self._setValue("skin_overlap",30)
            
        elif currMaterial == "petg" :
            modified_count += self._setValue("cool_fan_speed",30)
        
        else:
            modified_count += self._setValue("material_bed_temperature",60)
            modified_count += self._setValue("material_bed_temperature_layer_0",60)           
                       
        # Profile Extruder settings
        if currExtruder == "unknow" :
            # no modification
            self.writeToLog("----------------------------")
            self.writeToLog("|  Extruder preset : unknow  |")
            self.writeToLog("----------------------------")
        elif currExtruder == "direct" :
            modified_count += self._setValue("retraction_amount",0.8)
            modified_count += self._setValue("retraction_speed",30)
        else:
            self.writeToLog("----------------------------")
            self.writeToLog("| Extruder preset : " + currExtruder + " |")
            self.writeToLog("----------------------------")
            modified_count += self._setValue("retraction_amount",5)
            modified_count += self._setValue("retraction_speed",50)
 
        _layer_height = float(self._getValue("layer_height"))
        _infill_sparse_density = float(self._getValue("infill_sparse_density"))
        _top_thickness = float(self._getValue("top_thickness"))
        if _infill_sparse_density == 100 :
            _top_layers = 0 
        else:
            _top_layers = math.ceil(round((_top_thickness / _layer_height), 4))
            
        modified_count += self._setValue("top_layers",_top_layers)

        
        # Set name to quality change if modification
        if modified_count > 0 :
            profileName= currMode + " " 
            profileName= profileName + currMaterial 
            profileName= profileName + " "
            profileName= profileName + str(machine_nozzle_size)
            # Need to create a new Profile and not just change the name but not so easy ...
            #
            #if P_Name != "empty" :
            #    stack.qualityChanges.setName(profileName)
            #    for Extrud in extruders:
            #        Extrud.qualityChanges.setName(profileName)

        Message().hide()
        Message("Set values for %s Mode, %d parameters" % (currMode, modified_count) , title = "Universal Cura Settings").show()


