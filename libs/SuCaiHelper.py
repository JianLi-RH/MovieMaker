#!/usr/bin/python3.10
import os

def get_material(material):
    """
    Get sucai file path.

    Params:
        material: material file path, like: "resources/SuCai/JueSe/捕快2.png", "resources\\SuCai\\杂物\\书信1.png"

    Return:
        The path of material.
    """
    if os.path.exists(material):
        return material

    material = material.replace("\\", "/")
    if os.path.exists(material):
        return material

    raise Exception(f"Material is not exists: {material}")


if __name__ == "__main__":
    pass