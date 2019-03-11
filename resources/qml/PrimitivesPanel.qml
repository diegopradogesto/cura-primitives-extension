import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.2 as UM
import Cura 1.0 as Cura


UM.Dialog
{
    id: dialog

    title: "3D Primitives"

    Cura.PrimaryButton
    {
        text: "Add cube"
        iconSource: UM.Theme.getIcon("plus")
        onClicked: manager.createMesh("cube")
    }
}