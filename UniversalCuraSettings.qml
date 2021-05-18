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

    title: "Universal Cura Settings V0.0.11"

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
	// flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint

    // Setting the dimensions of the dialog window
    width: 325
    height: 175
    minimumWidth: 325
    minimumHeight: 175

    color: UM.Theme.getColor("main_background") //Background color of cura: "#fafafa"
	
	
    // Position of the window
    x: Screen.width*0.5 - width - 100
    y: Screen.height*0.5 

    property variant catalog: UM.I18nCatalog { name: "cura" }
    // property variant palette: SystemPalette {}
	
    // Connecting our variable to the computed property of the manager
	property string modeInput: manager.modeInput
	property string extruderInput: manager.extruderInput
	property string materialInput: manager.materialInput
	property string nozzleInput: manager.nozzleInput
	property string modeCurrent: manager.modeInput
	property string extruderCurrent: manager.extruderInput
	property string matrialCurrent: manager.materialInput
	property string nozzleCurrent: manager.nozzleInput

    Column
    {
        id: contents
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").height
		
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
				   ListElement { text: "0.2"}
				   ListElement { text: "0.4"}
				   ListElement { text: "0.6"}
				   ListElement { text: "0.8"}
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
				   ListElement { text: "top surface"}
				   ListElement { text: "warping"}
				   ListElement { text: "mechanical"}
				   ListElement { text: "small part"}
				   ListElement { text: "figurine"}
				   ListElement { text: "prototype"}
				   ListElement { text: "vase"}
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
