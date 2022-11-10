// Import the standard GUI elements from QTQuick
import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import QtQuick.Dialogs 6.0
import QtQuick.Window 6.0

// Import the Uranium GUI elements, which are themed for Cura
import UM 1.6 as UM
import Cura 1.7 as Cura

// Dialog
UM.Dialog
{
    id: base

    title: "Universal Cura Settings V0.1.10 (5.X)"

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
	// flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint

    // Setting the dimensions of the dialog window
    width: 325
    height: 180
    minimumWidth: 325
    minimumHeight: 180

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

    property variant catalog: UM.I18nCatalog { name: "cura" }
    // property variant palette: SystemPalette {}
	
    // Connecting our variable to the computed property of the manager
	property string modeInput: manager.modeInput
	property string extruderInput: manager.extruderInput
	property string materialInput: manager.materialInput
	property string nozzleInput: manager.nozzleInput
	property string modeCurrent: manager.modeInput
	property string extruderCurrent: manager.extruderInput
	property string materialCurrent: manager.materialInput
	property string nozzleCurrent: manager.nozzleInput
	property string getmodeCurrent: "standard"
	property string getlinkCurrent: "https://github.com/5axes/UniversalCuraSettings/wiki"

	
    Column
    {
        id: contents
        anchors.fill: parent
		// anchors.topMargin: UM.Theme.getSize("default_margin").height
        spacing: UM.Theme.getSize("default_margin").height
		height: childrenRect.height	
		
        Grid
        {
            columns: 2
            columnSpacing: UM.Theme.getSize("default_margin").width
            rowSpacing: UM.Theme.getSize("default_lining").height
            verticalItemAlignment: Grid.AlignVCenter

			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Extruder Type:");
				font: UM.Theme.getFont("default");
				color: UM.Theme.getColor("text");
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
				   ListElement { text: "unknow"}
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
				color: UM.Theme.getColor("text");
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
				   ListElement { text: "0.4"}
				   ListElement { text: "0.6"}
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
			
		}

        Grid
        {
            columns: 3
			columnSpacing: UM.Theme.getSize("default_margin").width

			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Material:");
				font: UM.Theme.getFont("default");
				color: UM.Theme.getColor("text");
				verticalAlignment: Text.AlignVCenter;
				renderType: Text.NativeRendering
				width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
			}
			
			//User input for Material
			ComboBox {
				id: material_input
				objectName: "Combo_Material"
				model: ListModel {
				   id: cbmItems
				   ListElement { text: "unknow"}
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

			UM.SimpleButton
			{
				id: helpmaterialButton
				width: UM.Theme.getSize("save_button_specs_icons").width
				height: UM.Theme.getSize("save_button_specs_icons").height
				iconSource: UM.Theme.getIcon("Help")
				hoverColor: UM.Theme.getColor("small_button_text_hover")
				color:  UM.Theme.getColor("small_button_text")

				onClicked:
				{
				getmodeCurrent = material_input.currentText;
				getlinkCurrent = "https://github.com/5axes/UniversalCuraSettings/wiki/Material-" + getmodeCurrent.replace(" ","-");
				Qt.openUrlExternally(getlinkCurrent)
				}
			}		
			
			Label
			{
				height: UM.Theme.getSize("setting_control").height;
				text: catalog.i18nc("@label","Settings Mode:");
				font: UM.Theme.getFont("default");
				color: UM.Theme.getColor("text");
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
				   ListElement { text: "top surface"}
				   ListElement { text: "extra quality"}
				   ListElement { text: "warping"}
				   ListElement { text: "mechanical"}
				   ListElement { text: "small part"}
				   ListElement { text: "figurine"}
				   ListElement { text: "prototype"}
				   ListElement { text: "support"}
				   ListElement { text: "vase"}
				   ListElement { text: "save material"}
				   ListElement { text: "small details"}			   
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
			
			UM.SimpleButton
			{
				id: helpButton
				width: UM.Theme.getSize("save_button_specs_icons").width
				height: UM.Theme.getSize("save_button_specs_icons").height
				iconSource: UM.Theme.getIcon("Help")
				hoverColor: UM.Theme.getColor("small_button_text_hover")
				color:  UM.Theme.getColor("small_button_text")

				onClicked:
				{
				getmodeCurrent = mode_input.currentText;
				getlinkCurrent = "https://github.com/5axes/UniversalCuraSettings/wiki/Mode-" + getmodeCurrent.replace(" ","-");
				Qt.openUrlExternally(getlinkCurrent)
				}
			}
		}			
	}

			
	UM.CheckBox
	{
		id: standardvalueCheckbox
		anchors.left: parent.left
		// anchors.top: parent.top
		anchors.top: contents.bottom
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
			id: applyButton
            text: catalog.i18nc("@action:button", "Apply")
            onClicked: 
			{
			manager.modeApply(modeCurrent)
			}

        }
    ]
}
