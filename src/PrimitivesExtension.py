import os
from typing import cast

from PyQt5.QtCore import QObject

from UM.Extension import Extension
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from UM.i18n import i18nCatalog
from cura.CuraApplication import CuraApplication

i18n_catalog = i18nCatalog("cura")


# This extension allows the user to load some primitive 3D model into the build plate in Cura.
class PrimitivesExtension(QObject, Extension):

    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self.setMenuName("3D Primitives")
        self.addMenuItem("Model list", self.showPopup)

        self._view = None

    def showPopup(self) -> None:
        if self._view is None:
            self._createView()
            if self._view is None:
                Logger.log("e", "Not creating 3D Primitives window since the QML component failed to be created.")
                return
        self._view.show()

    def _createView(self) -> None:
        Logger.log("d", "Creating 3D Primitives plugin view.")

        # Create the plugin dialog component
        path = os.path.join(cast(str, PluginRegistry.getInstance().getPluginPath("cura-primitives-extension")),
                            "resources", "qml", "PrimitivesPanel.qml")
        self._view = CuraApplication.getInstance().createQmlComponent(path, {"manager": self})
