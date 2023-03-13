// Import the standard GUI elements from QTQuick
import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.2
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.2

// Import the Uranium GUI elements, which are themed for Cura
import UM 1.1 as UM
import Cura 1.0 as Cura

// Dialog
UM.Dialog
{
    id: base

    property variant catalog: UM.I18nCatalog { name: "universal" }
	
	title: catalog.i18nc("@title","Universal Cura Settings Version : ") + manager.curaVersion

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
	// flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint

    // Setting the dimensions of the dialog window
    width: 325
    height: 200
    minimumWidth: 325
    minimumHeight: 200

    color: UM.Theme.getColor("main_background") //Background color of cura: "#fafafa"

    function boolCheck(value) //Hack to ensure a good match between python and qml.
    {
        if(value == "True")
        {
            return true
        }else if(value == "False" || value == undefined)
        {
            return false
        }
        else
        {
            return value
        }
    }	
	
    // Position of the window
	// Could be use to open the Dialog always at the center of the cura windows
	// But if active then you cannot switch the Dialog to an other monitor (jellespijker) 
    // x: Screen.width*0.5 - width - 100
    // y: Screen.height*0.5 

	
    // Connecting our variable to the computed property of the manager
	property string modeInput: manager.modeInput
	property string extruderInput: manager.extruderInput
	property string materialInput: manager.materialInput
	property string nozzleInput: manager.nozzleInput
	property string modeCurrent: manager.modeInput
	property string extruderCurrent: manager.extruderInput
	property string materialCurrent: manager.materialInput
	property string nozzleCurrent: manager.nozzleInput

	
    Column
    {
        id: contents
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").height
		anchors.top: standardvalueCheckbox.bottom
		anchors.topMargin: UM.Theme.getSize("default_margin").height
		
        Grid
        {
            columns: 2;
            columnSpacing: UM.Theme.getSize("default_margin").width
            rowSpacing: UM.Theme.getSize("default_lining").height
            verticalItemAlignment: Grid.AlignVCenter


			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Extruder Type:");
				font: UM.Theme.getFont("default");
				color: "#000000" // UM.Theme.getColor("text");
				verticalAlignment: Text.AlignVCenter;
				renderType: Text.NativeRendering
				width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
			}

			//User input of extruder
			ComboBox {
				id: extruder_input
				objectName: "Combo_Extruder"
				model: ListModel {
				   id: cbItems
				   ListElement { text: "unknown"}
				   ListElement { text: "bowden"}
				   ListElement { text: "direct"}
				}
				width: UM.Theme.getSize("setting_control").width
				height: UM.Theme.getSize("setting_control").height

				Component.onCompleted: currentIndex = find(extruderInput)
				
				onCurrentIndexChanged: 
				{ 
				    extruderCurrent = cbItems.get(currentIndex).text;
					manager.extruderEntered(cbItems.get(currentIndex).text)
				}
			}	

			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Nozzle Size:");
				font: UM.Theme.getFont("default");
				color: "#000000" // UM.Theme.getColor("text");
				verticalAlignment: Text.AlignVCenter;
				renderType: Text.NativeRendering
				width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
			}

			//User input of nozzle size
			ComboBox {
				id: nozzle_input
				objectName: "Combo_Nozzle"
				model: ListModel {
				   id: cbnItems
				   ListElement { text: "not specified"}
				   ListElement { text: "0.2"}
				   ListElement { text: "0.3"}
				   ListElement { text: "0.4"}
				   ListElement { text: "0.5"}
				   ListElement { text: "0.6"}
				   ListElement { text: "0.7"}
				   ListElement { text: "0.8"}
				   ListElement { text: "1.0"}
				}
				width: UM.Theme.getSize("setting_control").width
				height: UM.Theme.getSize("setting_control").height

				Component.onCompleted: currentIndex = find(nozzleInput)
				
				onCurrentIndexChanged: 
				{ 
				    nozzleCurrent = cbnItems.get(currentIndex).text;
					manager.nozzleEntered(cbnItems.get(currentIndex).text)
				}
			}	
			
			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Material:");
				font: UM.Theme.getFont("default");
				color: "#000000" // UM.Theme.getColor("text");
				verticalAlignment: Text.AlignVCenter;
				renderType: Text.NativeRendering
				width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
			}
			
			
			//User input of Mode
			ComboBox {
				id: material_input
				objectName: "Combo_Material"
				model: ListModel {
				   id: cbmItems
				   ListElement { text: "unknown"}
				   ListElement { text: "pla"}
				   ListElement { text: "abs"}
				   ListElement { text: "petg"}
				   ListElement { text: "tpu"}
				}
				width: UM.Theme.getSize("setting_control").width
				height: UM.Theme.getSize("setting_control").height

				Component.onCompleted: currentIndex = find(materialInput)
				
				onCurrentIndexChanged: 
				{ 
				    materialCurrent = cbmItems.get(currentIndex).text;
					manager.materialEntered(cbmItems.get(currentIndex).text)
				}
			}
			
			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Settings Mode:");
				font: UM.Theme.getFont("default");
				color: "#000000" // UM.Theme.getColor("text");
				verticalAlignment: Text.AlignVCenter;
				renderType: Text.NativeRendering
				width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
			}
			
			
			//User input of Mode
			ComboBox {
				id: mode_input
				objectName: "Combo_Mode"
				model: ListModel {
				   id: cbeItems
				   ListElement { text: "standard"}
				   ListElement { text: "bed adhesion"}
				   ListElement { text: "extra quality"}
				   ListElement { text: "mechanical"}  
				   ListElement { text: "figurine"}
				   ListElement { text: "prototype"}
				   ListElement { text: "support"}
				   ListElement { text: "save material"}
				   ListElement { text: "small part"}
				   ListElement { text: "small details"}
				   ListElement { text: "top surface"}
				   ListElement { text: "vase"}
				   ListElement { text: "warping"}
				}
				width: UM.Theme.getSize("setting_control").width
				height: UM.Theme.getSize("setting_control").height

				Component.onCompleted: currentIndex = find(modeInput)
				
				onCurrentIndexChanged: 
				{ 
				    modeCurrent = cbeItems.get(currentIndex).text;
					manager.modeEntered(cbeItems.get(currentIndex).text)
				}
			}	

		}
	}

	CheckBox
    {
        id: standardvalueCheckbox
        anchors.top: contents.bottom
        // anchors.topMargin: UM.Theme.getSize("default_margin").height
        anchors.left: parent.left
        text: catalog.i18nc("@option:check","Set standard settings")

        checked: boolCheck(UM.Preferences.getValue("UniversalCuraSettings/setstandardvalue"))
        onClicked: UM.Preferences.setValue("UniversalCuraSettings/setstandardvalue", checked)
		
    }
	
	rightButtons: [
        Button
        {
            id: cancelButton
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.reject()
        },
        Button
        {
            text: catalog.i18nc("@action:button", "Apply")
            onClicked: 
			{
			manager.modeApply(modeCurrent)
			}
            isDefault: true
        }
    ]
}
