import os
from typing import cast

import numpy
import trimesh
from PyQt5.QtCore import QObject, pyqtSlot

from UM.Extension import Extension
from UM.Logger import Logger
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.PluginRegistry import PluginRegistry
from UM.i18n import i18nCatalog
from cura.CuraApplication import CuraApplication
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Scene.CuraSceneNode import CuraSceneNode
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator

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

    @pyqtSlot(str)
    def createMesh(self, model_name: str) -> None:
        node = CuraSceneNode()

        node.setName(model_name)
        node.setSelectable(True)
        mesh = self._createCube(10)
        node.setMeshData(mesh.build())

        active_build_plate = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))
        node.addDecorator(SliceableObjectDecorator())

        scene = CuraApplication.getInstance().getController().getScene()

        op = AddSceneNodeOperation(node, scene.getRoot())
        op.push()

        scene.sceneChanged.emit(node)

    def _createCube(self, size):
        mesh = MeshBuilder()

        # Can't use MeshBuilder.addCube() because that does not get per-vertex normals
        # Per-vertex normals require duplication of vertices
        s = size / 2
        verts = [ # 6 faces with 4 corners each
            [-s, -s,  s], [-s,  s,  s], [ s,  s,  s], [ s, -s,  s],
            [-s,  s, -s], [-s, -s, -s], [ s, -s, -s], [ s,  s, -s],
            [ s, -s, -s], [-s, -s, -s], [-s, -s,  s], [ s, -s,  s],
            [-s,  s, -s], [ s,  s, -s], [ s,  s,  s], [-s,  s,  s],
            [-s, -s,  s], [-s, -s, -s], [-s,  s, -s], [-s,  s,  s],
            [ s, -s, -s], [ s, -s,  s], [ s,  s,  s], [ s,  s, -s]
        ]
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        for i in range(0, 24, 4): # All 6 quads (12 triangles)
            indices.append([i, i+2, i+1])
            indices.append([i, i+3, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
