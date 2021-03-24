#-------------------------------------------------------------------------------------------
# Copyright (c) 2020-2021 5@xes
# 
# JonasUniversalCuraSettings is released under the terms of the AGPLv3 or higher.
#
# Version 0.0.1 : First prototype
# Version 0.0.2 : Add the choice of the Nozzle Size
#
#-------------------------------------------------------------------------------------------
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from UM.Extension import Extension
from UM.PluginRegistry import PluginRegistry
from UM.Application import Application
from cura.CuraApplication import CuraApplication
from cura.CuraVersion import CuraVersion  # type: ignore

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

class JonasUniversalCuraSettings(Extension, QObject,):
  
    # The QT signal, which signals an update for user information text
    userInfoTextChanged = pyqtSignal()
    userModeChanged = pyqtSignal()
    
    
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)
        
        self._Section =""

        #Initialize variables
        self._continueDialog = None
        self._mode = "mechanical"
        self._extruder = "bowden"
        self._material = "pla"
        self._nozzle = "0.4"
        
        # set the preferences to store the default value
        self._application = Application.getInstance()
        self._preferences = self._application.getPreferences()
        self._preferences.addPreference("JonasUniversalCuraSettings/dialog_path", "")
        self._preferences.addPreference("JonasUniversalCuraSettings/mode", "mechanical")
        self._preferences.addPreference("JonasUniversalCuraSettings/extruder", "bowden")
        self._preferences.addPreference("JonasUniversalCuraSettings/material", "pla")
        self._preferences.addPreference("JonasUniversalCuraSettings/nozzle", "0.4")

        
        # Mode
        self._mode = self._preferences.getValue("JonasUniversalCuraSettings/mode")
        # Extruder type
        self._extruder= self._preferences.getValue("JonasUniversalCuraSettings/extruder") 
        # Material type
        self._material= self._preferences.getValue("JonasUniversalCuraSettings/material")
        # Nozzle size
        self._nozzle= self._preferences.getValue("JonasUniversalCuraSettings/nozzle")
        
        # Test version for futur release 4.9 or Arachne
        VersC=1.0
        if "master" in CuraVersion or "beta" in CuraVersion or "BETA" in CuraVersion:
            #Logger.log('d', "Info CuraVersion --> " + str(CuraVersion))
            VersC=4.9  # Master is always a developement version.
        else:
            try:
                VersC = int(CuraVersion.split(".")[0])+int(CuraVersion.split(".")[1])/10
            except:
                pass
                
        # Thanks to Aldo Hoeben / fieldOfView for this code
        self._dialog_options = QFileDialog.Options()
        if sys.platform == "linux" and "KDE_FULL_SESSION" in os.environ:
            self._dialog_options |= QFileDialog.DontUseNativeDialog

        self.setMenuName(catalog.i18nc("@item:inmenu", "Jonas Universal Settings"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set Jonas Universal Settings"), self.setDefProfile)
        self.addMenuItem("", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Export current profile"), self.exportData)
        self.addMenuItem(" ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Merge a profile"), self.importData)

        #Initialize variables
        self._continueDialog = None
 
    #===== Text Output ===================================================================================================
    # Writes the message to the log, includes timestamp, length is fixed
    def writeToLog(self, str):
        Logger.log("d", "Jonas Cura Settings = %s", str)
        
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
        qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "JonasCuraSettings.qml")
        component_with_context = Application.getInstance().createQmlComponent(qml_file_path, {"manager": self})
        return component_with_context
 
    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def nozzleEntered(self, text) -> None:
        self._nozzle = text

        self.writeToLog("Set JonasUniversalCuraSettings/Nozzle set to : " + text)
        self._preferences.setValue("JonasUniversalCuraSettings/nozzle", self._nozzle)
        
    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def modeEntered(self, text) -> None:
        self._mode = text

        self.writeToLog("Set JonasUniversalCuraSettings/Mode set to : " + text)
        self._preferences.setValue("JonasUniversalCuraSettings/mode", self._mode)

    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def materialEntered(self, text) -> None:
        self._material = text

        self.writeToLog("Set JonasUniversalCuraSettings/Material set to : " + text)
        self._preferences.setValue("JonasUniversalCuraSettings/material", self._material)

    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def extruderEntered(self, text) -> None:
        self._extruder = text

        self.writeToLog("Set JonasUniversalCuraSettings/Extruder set to : " + text)
        self._preferences.setValue("JonasUniversalCuraSettings/extruder", self._extruder) 

    # is called when a key gets released in the mode inputField (twice for some reason)
    @pyqtSlot(str)
    def modeApply(self, text) -> None:
        self._mode = text
        self.setProfile() 
        #self.writeToLog("Mode Apply to : " + text)
        
    #==== Previous code for Export/Import CSV =====================================================================================================    
    def exportData(self) -> None:
        # thanks to Aldo Hoeben / fieldOfView for this part of the code
        file_name = QFileDialog.getSaveFileName(
            parent = None,
            caption = catalog.i18nc("@title:window", "Save as"),
            directory = self._preferences.getValue("JonasUniversalCuraSettings/dialog_path"),
            filter = "CSV files (*.csv)",
            options = self._dialog_options
        )[0]

        if not file_name:
            Logger.log("d", "No file to export selected")
            return

        self._preferences.setValue("JonasUniversalCuraSettings/dialog_path", os.path.dirname(file_name))
        # -----
        
        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        #Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        
        exported_count = 0
        try:
            with open(file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
                    if VersC > 4.8:
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
        file_name = QFileDialog.getOpenFileName(
            parent = None,
            caption = catalog.i18nc("@title:window", "Open File"),
            directory = self._preferences.getValue("import_export_tools/dialog_path"),
            filter = "CSV files (*.csv)",
            options = self._dialog_options
        )[0]

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
                csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        self.writeToLog("setValue key : " + key)
        machine_manager = CuraApplication.getInstance().getMachineManager()  
        stack = CuraApplication.getInstance().getGlobalContainerStack()
        
        # settable_per_extruder
        # type 
        GetType=stack.getProperty(key,"type")
        GetVal=stack.getProperty(key,"value")
        GetExtruder=stack.getProperty(key,"settable_per_extruder")

                   
        if GetExtruder == True:
            global_stack = machine_manager.activeMachine
            extruders = list(global_stack.extruders.values())      
            for Extrud in extruders:
                PosE = int(Extrud.getMetaDataEntry("position"))
                PosE += 1
                GetVal= Extrud.getProperty(key,"value")
                if GetVal != c_val :
                    Extrud.setProperty(key,"value",c_val)
                    text_message = "setValue Extruder " + str(PosE)
                    text_message = text_message + " : "
                    self.writeToLog(text_message + str(c_val))
                    modified_c = 1
                else:
                    modified_c = 0                
        else:
            if GetVal != c_val : 
                stack.setProperty(key,"value",c_val)
                self.writeToLog("setValue Global : " + str(c_val)) 
                modified_c = 1            
            else:
                modified_c = 0
        
        return modified_c
    
    # Layer_Height according to machine_nozzle_size & self._mode
    def _defineLayer_Height(self,c_val) -> float:
        layer_height = 0.5 * c_val
         # Profile Mode settings
        if self._mode == "mechanical" :
            layer_height = 0.5 * c_val    
        
        elif self._mode == "figurine" :
            layer_height = 0.25 * c_val
            
        elif self._mode == "prototype" :
            layer_height = 0.6 * c_val
            
        elif self._mode == "vases" :
            layer_height = 0.5 * c_val
            
        else:
            layer_height = 0.5 * c_val   
        
        return layer_height

    # Line_Width according to machine_nozzle_size & self._mode
    def _defineLine_Width(self,c_val) -> float:
        line_width = c_val
         # Profile Mode settings
        if self._mode == "mechanical" :
            layer_height = c_val
            
        elif self._mode == "figurine" :
            layer_height = c_val
            
        elif self._mode == "prototype" :
            line_width = 1.075 * c_val
            
        elif self._mode == "vases" :
            line_width = 1.075 * c_val
            
        else:
            line_width = c_val   
        
        return line_width

    # Material_Print_Temperature according to machine_nozzle_size & self._material
    def _defineMaterial_Print_Temperature(self,c_val) -> float:
        material_print_temperature = 200
         # Profile Mode settings
        if self._material == "pla" :
            material_print_temperature = 205 + round(c_val*12.5,0)
            
        elif self._mode == "abs" :
            material_print_temperature = 225 + round(c_val*12.5,0)
            
        elif self._mode == "petg" :
            material_print_temperature = 220 + round(c_val*12.5,0)
                        
        else:
            material_print_temperature = c_val   
        
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
        self.writeToLog("With Profile Mode : " + self._mode)
        self.writeToLog("With Extruder Mode : " + self._extruder)
        self.writeToLog("With Material : " + self._material)
        self.writeToLog("With Nozzle Size : " + self._nozzle)
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
        if float(currNozzle) != machine_nozzle_size:
            machine_nozzle_size=float(currNozzle)
            modified_count += self._setValue("machine_nozzle_size",machine_nozzle_size)
            
        #------------------------------------------------------
        # Extruder get Meterial (Useless for the moment )
        #------------------------------------------------------
        extruders = list(global_stack.extruders.values())             
        for Extrud in extruders:
            # Material
            M_Name = Extrud.material.getMetaData().get("material", "")
              
        #------------------
        # Global stack
        #------------------
        # Reinit
        modified_count += self._setValue("magic_spiralize",False)
        
        # General settings
        modified_count += self._setValue("adaptive_layer_height_threshold",250)
        modified_count += self._setValue("adaptive_layer_height_variation",0.03)
        modified_count += self._setValue("adhesion_type",'skirt')
        
        modified_count += self._setValue("retraction_combing",'infill')
        modified_count += self._setValue("speed_slowdown_layers",1)
        modified_count += self._setValue("support_enable",False)
        modified_count += self._setValue("support_type",'buildplate')
        modified_count += self._setValue("travel_retract_before_outer_wall",True)

        modified_count += self._setValue("skin_no_small_gaps_heuristic",False)
        
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
        
        modified_count += self._setValue("bottom_layers",6)
        modified_count += self._setValue("bottom_skin_preshrink",1.2)
        modified_count += self._setValue("brim_line_count",10)
        
        modified_count += self._setValue("conical_overhang_angle",70)
        
        modified_count += self._setValue("coasting_enable",True)
        modified_count += self._setValue("coasting_speed",100)
        modified_count += self._setValue("coasting_volume",0.02)
        modified_count += self._setValue("cool_fan_full_at_height",1)
        modified_count += self._setValue("cool_fan_full_layer",5)
        modified_count += self._setValue("cool_fan_speed",100)
        modified_count += self._setValue("cool_min_layer_time",5)
        modified_count += self._setValue("cool_min_speed",15)
        
        modified_count += self._setValue("gradual_support_infill_step_height",1.5)
        modified_count += self._setValue("gradual_support_infill_steps",1)
        
        modified_count += self._setValue("infill_before_walls",False)
        modified_count += self._setValue("infill_enable_travel_optimization",True)
        modified_count += self._setValue("infill_line_width",0.5)
        modified_count += self._setValue("infill_pattern",'zigzag')
        modified_count += self._setValue("infill_sparse_density",8)
        modified_count += self._setValue("infill_wall_line_count",1)
        modified_count += self._setValue("infill_wipe_dist",0.2)
        modified_count += self._setValue("ironing_enabled",False)
        
        modified_count += self._setValue("ironing_flow",8.0)
        modified_count += self._setValue("ironing_inset",0.15)
        modified_count += self._setValue("ironing_line_spacing",0.15)
        
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
        
        modified_count += self._setValue("limit_support_retractions",False)
        modified_count += self._setValue("magic_fuzzy_skin_point_density",1.75)
        modified_count += self._setValue("magic_fuzzy_skin_thickness",0.2)
        modified_count += self._setValue("material_flow",99)
        modified_count += self._setValue("material_print_temperature",210)
        modified_count += self._setValue("max_skin_angle_for_expansion",64)
        modified_count += self._setValue("meshfix_maximum_deviation",0.04)
        modified_count += self._setValue("meshfix_maximum_resolution",0.4)
        
        modified_count += self._setValue("min_infill_area",10)
        modified_count += self._setValue("min_skin_width_for_expansion",0.1)

        modified_count += self._setValue("optimize_wall_printing_order",True)
        modified_count += self._setValue("retraction_combing",'off')
        modified_count += self._setValue("retraction_combing_max_distance",33)
        modified_count += self._setValue("retraction_hop",0.16)
        modified_count += self._setValue("retraction_hop_enabled",True)
        modified_count += self._setValue("retraction_retract_speed",50)
        modified_count += self._setValue("roofing_layer_count",1)
        modified_count += self._setValue("roofing_line_width",0.35)
        
        modified_count += self._setValue("skirt_gap",8)
        modified_count += self._setValue("skirt_line_count",2)
        modified_count += self._setValue("small_feature_max_length",5)
        modified_count += self._setValue("small_feature_speed_factor",100)
        modified_count += self._setValue("small_feature_speed_factor_0",50)
        modified_count += self._setValue("small_hole_max_size",3.25)
        modified_count += self._setValue("speed_infill",60)
        modified_count += self._setValue("speed_ironing",55)
        modified_count += self._setValue("speed_layer_0",20)
        modified_count += self._setValue("speed_roofing",40)
        modified_count += self._setValue("speed_topbottom",60)
        modified_count += self._setValue("speed_travel",150)
        modified_count += self._setValue("speed_wall_0",25)
        modified_count += self._setValue("speed_wall_x",40)
        
        modified_count += self._setValue("support_enable",False)
        modified_count += self._setValue("support_structure",'normal')
        modified_count += self._setValue("support_type",'buildplate')
        modified_count += self._setValue("support_angle",67)
        modified_count += self._setValue("support_bottom_density",97)
        modified_count += self._setValue("support_bottom_distance",0.2)
        modified_count += self._setValue("support_bottom_enable",True)
        modified_count += self._setValue("support_bottom_height",0.8)
        modified_count += self._setValue("support_brim_enable",True)
        modified_count += self._setValue("support_brim_width",3)       
        modified_count += self._setValue("support_infill_rate",7)
        modified_count += self._setValue("support_join_distance",3)
        modified_count += self._setValue("support_offset",0.6)
        modified_count += self._setValue("support_interface_enable",True)
        modified_count += self._setValue("support_interface_line_width",0.55)

        modified_count += self._setValue("support_interface_offset",0.6)
        modified_count += self._setValue("support_interface_pattern",'zigzag')
        modified_count += self._setValue("support_interface_skip_height",0.2)

        modified_count += self._setValue("support_roof_density",97)
        modified_count += self._setValue("support_roof_enable",True)
        modified_count += self._setValue("support_roof_height",1.2)
        modified_count += self._setValue("support_roof_offset",0.6)
        modified_count += self._setValue("support_top_distance",0.2)
        modified_count += self._setValue("support_tower_diameter",6)
        modified_count += self._setValue("support_tower_roof_angle",60)
        modified_count += self._setValue("support_use_towers",False)
        modified_count += self._setValue("support_wall_count",1)
        modified_count += self._setValue("support_xy_distance",0.4)
        modified_count += self._setValue("support_z_distance",0.2)
        modified_count += self._setValue("support_xy_overrides_z",'xy_overrides_z')
        
        modified_count += self._setValue("support_tree_angle",45)
        modified_count += self._setValue("support_tree_branch_diameter_angle",2.5)
        modified_count += self._setValue("support_tree_branch_distance",0.5)
        modified_count += self._setValue("support_tree_collision_resolution",0.15)
        
        # modified_count += self._setValue("top_layers",7)
        modified_count += self._setValue("top_thickness",1)
        
        modified_count += self._setValue("travel_avoid_distance",1)
        modified_count += self._setValue("travel_avoid_other_parts",False)
        modified_count += self._setValue("travel_avoid_supports",True)
        modified_count += self._setValue("travel_compensate_overlapping_walls_0_enabled",False)
        modified_count += self._setValue("travel_retract_before_outer_wall",True)
        modified_count += self._setValue("wall_0_inset",0.02)
        modified_count += self._setValue("wall_line_count",3)
        modified_count += self._setValue("wall_min_flow",15)
        # modified_count += self._setValue("wall_transition_angle",25)
        modified_count += self._setValue("wall_min_flow_retract",True)
        modified_count += self._setValue("xy_offset_layer_0",-0.025)
        modified_count += self._setValue("z_seam_relative",True)
        modified_count += self._setValue("z_seam_type",'back')

        
        # Settings according to value calculation
        top_bottom_pattern = self._getValue("top_bottom_pattern")
        if top_bottom_pattern != 'concentric':
            modified_count += self._setValue("skin_overlap",5)           
        else:
            modified_count += self._setValue("skin_overlap",5)

        line_width = float(self._getValue("line_width"))
        modified_count += self._setValue("skin_line_width",line_width)

        material_flow = float(self._getValue("material_flow"))
        modified_count += self._setValue("infill_material_flow",material_flow)
        
        meshfix_maximum_resolution = float(self._getValue("meshfix_maximum_resolution"))
        speed_travel = float(self._getValue("speed_travel"))
        speed_print = float(self._getValue("speed_print"))
        meshfix_maximum_travel_resolution = min(meshfix_maximum_resolution * speed_travel / speed_print, 2 * line_width)
        modified_count += self._setValue("meshfix_maximum_travel_resolution",meshfix_maximum_travel_resolution)
        
        support_brim_width = float(self._getValue("support_brim_width"))
        skirt_brim_line_width = float(self._getValue("skirt_brim_line_width"))
        initial_layer_line_width_factor = float(self._getValue("initial_layer_line_width_factor"))
        
        support_brim_line_count = math.ceil(support_brim_width / (skirt_brim_line_width * initial_layer_line_width_factor / 100.0))
        modified_count += self._setValue("support_brim_line_count",support_brim_line_count)

        support_interface_pattern=self._getValue("support_interface_pattern")
        modified_count += self._setValue("support_roof_pattern",support_interface_pattern)

        modified_count += self._setValue("support_xy_distance_overhang",(machine_nozzle_size / 2))
        
        
        # layer_height 
        modified_count += self._setValue("layer_height",self._defineLayer_Height(machine_nozzle_size))
        modified_count += self._setValue("layer_height_0",0.2)
        
        # Profile Mode settings
        if currMode == "mechanical" :         
            modified_count += self._setValue("brim_line_count",10)
 
        elif currMode == "bed adhesion" :
            # Profile Mode settings
            modified_count += self._setValue("brim_line_count",10)
            
        elif currMode == "figurine" :
            # dimensionally accurate, stiff and durable
            modified_count += self._setValue("brim_line_count",2)
            
        elif currMode == "prototype" :
            # Fast and rought
            modified_count += self._setValue("wall_line_count",2)
            
        elif currMode == "vases" :
            # Spiralize outer contour
            modified_count += self._setValue("magic_spiralize",True)
            
        else:
            modified_count += self._setValue("wall_line_count",3)
            
        # Profile Extruder settings   

        # Profile Material settings
        if currMaterial == "pla" :
            modified_count += self._setValue("material_bed_temperature",55)
            modified_count += self._setValue("material_bed_temperature_layer_0",55)
            modified_count += self._setValue("material_print_temperature",210)
        else:
            modified_count += self._setValue("material_print_temperature",230)
            modified_count += self._setValue("material_bed_temperature",60)
            modified_count += self._setValue("material_bed_temperature_layer_0",60)           
                       
        # Profile Extruder settings
        if currExtruder == "bowden" :
            modified_count += self._setValue("retraction_amount",5)
            modified_count += self._setValue("retraction_hop",0.16)
            modified_count += self._setValue("retraction_hop_enabled",True)
            modified_count += self._setValue("retraction_retract_speed",50)
        else:
            modified_count += self._setValue("retraction_amount",0.8)
            modified_count += self._setValue("retraction_hop",0.16)
            modified_count += self._setValue("retraction_hop_enabled",True)
            modified_count += self._setValue("retraction_retract_speed",50)
 
        layer_height = float(self._getValue("layer_height"))
        infill_sparse_density = float(self._getValue("infill_sparse_density"))
        top_thickness = float(self._getValue("top_thickness"))
        if infill_sparse_density == 100 :
            top_layers = 0 
        else:
            top_layers = math.ceil(round((top_thickness / layer_height), 4))
        modified_count += self._setValue("top_layers",top_layers)

        
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
        Message("Set values for %s Mode, %d parameters" % (currMode, modified_count) , title = "Jonas Universal Cura Settings").show()


