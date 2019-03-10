from .src import PrimitivesExtension


def getMetaData():
    return {}


def register(app):
    return { "extension": PrimitivesExtension.PrimitivesExtension()}
