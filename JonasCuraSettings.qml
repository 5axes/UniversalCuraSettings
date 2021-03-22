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

    title: "Jonas Cura Settings"

    color: "#fafafa" //Background color of cura: #fafafa

    // NonModal like that the dialog to block input in the main window
    modality: Qt.NonModal

    // WindowStaysOnTopHint to stay on top
	// flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint

    // Setting the dimensions of the dialog window
    width: 350
    height: 100
    minimumWidth: 350
    minimumHeight: 100

    // Position of the window
    x: Screen.width*0.5 - width - 100
    y: Screen.height*0.5 

    property variant catalog: UM.I18nCatalog { name: "cura" }
    property variant palette: SystemPalette {}
	
    // Connecting our variable to the computed property of the manager
	property string modeInput: manager.modeInput
	property string extruderInput: manager.extruderInput
	property string modeCurrent: manager.modeInput
	property string extruderCurrent: manager.extruderInput

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
				text: catalog.i18nc("@label","Extruder type:");
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
				   ListElement { text: "mechanical"}
				   ListElement { text: "figurine"}
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
