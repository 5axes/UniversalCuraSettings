#-------------------------------------------------------------------------------------------
# Copyright (c) 2020-2021 5@xes
# 
# JonasUniversalCuraSettings is released under the terms of the AGPLv3 or higher.
#
# Version 0.0.1 : First prototype
#
#-------------------------------------------------------------------------------------------

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import os
import platform
import os.path
import sys
import re

from datetime import datetime
# from typing import cast, Dict, List, Optional, Tuple, Any, Set
from cura.CuraApplication import CuraApplication
from cura.CuraVersion import CuraVersion  # type: ignore


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
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)
        
        self._Section =""

        self._application = Application.getInstance()
        self._preferences = self._application.getPreferences()
        self._preferences.addPreference("JonasUniversalCuraSettings/dialog_path", "")
        
        VersC=1.0

        # Test version for futur release 4.9
        if "master" in CuraVersion or "beta" in CuraVersion or "BETA" in CuraVersion:
            #Logger.log('d', "Info CuraVersion --> " + str(CuraVersion))
            VersC=4.9  # Master is always a developement version.
        else:
            try:
                VersC = int(CuraVersion.split(".")[0])+int(CuraVersion.split(".")[1])/10
            except:
                pass

                
        # thanks to Aldo Hoeben / fieldOfView for this code
        self._dialog_options = QFileDialog.Options()
        if sys.platform == "linux" and "KDE_FULL_SESSION" in os.environ:
            self._dialog_options |= QFileDialog.DontUseNativeDialog

        self.setMenuName(catalog.i18nc("@item:inmenu", "Jonas Universal Settings"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set Jonas Universal Settings"), self.setProfile)
        self.addMenuItem("", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Export current profile"), self.exportData)
        self.addMenuItem(" ", lambda: None)
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Merge a profile"), self.importData)

    def setProfile(self) -> None:

        machine_manager = CuraApplication.getInstance().getMachineManager()        
        stack = CuraApplication.getInstance().getGlobalContainerStack()

        global_stack = machine_manager.activeMachine

        #Get extruder count
        extruder_count=stack.getProperty("machine_extruder_count", "value")
        
        # Profile
        P_Name = global_stack.qualityChanges.getMetaData().get("name", "")
        # Quality
        Q_Name = global_stack.quality.getMetaData().get("name", "")

        # Global stack
        modified_count=2
        stack.setProperty("layer_height","value",0.2)
        
        # Extruder[0]
        container=extruders[0]
        
        container.setProperty("infill_pattern","value",	'zigzag')
  
        Message().hide()
        Message("Changed keys for %d settings" % modified_count , title = "Jonas Universal Cura Settings").show()
        
        
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


