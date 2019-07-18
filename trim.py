#!/usr/bin/env python

from PIL import Image
import sys
import deftree
import os
import re

def name_from_path(path):
    pathname = path[path.rfind("/") + 1:]
    dotindex = pathname.rfind(".")
    if dotindex == -1:
        return pathname
    return pathname[:dotindex]

def trim_image(in_file, out_file):
    image = Image.open(in_file)
    size = image.size
    bbox = image.convert("RGBa").getbbox()
    offset_x = (float(bbox[2]) + float(bbox[0])) * 0.5 - float(size[0]) * 0.5
    offset_y = -(float(bbox[3]) + float(bbox[1])) * 0.5 + float(size[1]) * 0.5
    image.crop(bbox).save(out_file)
    offset = (offset_x, offset_y)
    print("Trimmed", name_from_path(in_file), "from", size, "to", bbox, "Offset:", offset)
    return offset

def get_image_path(element):
    return element.get_attribute("image").value

def add_hashes(hash_ids, name):
    hash_ids[name] = 'h_' + re.sub(r'[^a-zA-Z0-9]', '_', name)

if __name__ == "__main__":
    project_dir = sys.argv[1]
    atlas_path = sys.argv[2]
    out_dir = sys.argv[3]

    atlas = deftree.parse(atlas_path)
    root = atlas.get_root()

    images = {}
    animations = {}
    offsets = {}
    hash_ids = {}

    for element in root.elements():
        if element.name == "images":
            path = get_image_path(element)
            name = name_from_path(path)
            images[name] = path
        elif element.name == "animations":
            id = element.get_attribute("id").value
            add_hashes(hash_ids, id)
            framelist = []
            for child in element.elements():
                if child.name == "images":
                    path = get_image_path(child)
                    name = name_from_path(path)
                    images[name] = path
                    framelist.append(name)
            animations[id] = {
                "fps": element.get_attribute("fps").value,
                "frames": framelist,
            }


    for name, path in images.items():
        hash_ids[name] = 'h_' + re.sub(r'[^a-zA-Z0-9]', '_', name)
        add_hashes(hash_ids, name)
        path = path.replace("/", os.sep)
        offsets[name] = trim_image(project_dir + path, os.path.join(out_dir, name + ".png"))

    lines = []
    lines.append("local all_animations = require \"main.animations.animations\"")
    lines.append("")
    for name, hash_id in hash_ids.items():
        lines.append("local " + hash_id + " = hash(\"" + name + "\")")
    lines.append("")
    lines.append("local animations = {")
    lines.append("  images = {")
    for name, offset in offsets.items():
        lines.append("    [" + hash_ids[name] + "] = { offset = vmath.vector3(" + str(offset[0]) + ", " + str(offset[1]) + ", 0.0) },")
    lines.append("  },")
    lines.append("  animations = {")
    for animation_id, animation in animations.items():
        lines.append("    [" + hash_ids[animation_id] + "] = {")
        lines.append("      fps = " + str(animation["fps"]) + ",")
        lines.append("      frames = {")
        for frame in animation["frames"]:
            lines.append("        " + hash_ids[frame] + ",")
        lines.append("      }")
        lines.append("    },")
    lines.append("  },")
    lines.append("}")
    lines.append("")
    lines.append("all_animations[hash(\"" + name_from_path(atlas_path) + "\")] = animations")
    lines.append("return animations")
    lines.append("")

    out_file = open(os.path.join(out_dir, "animations.lua"), "w+")
    out_file.write("\n".join(lines))
    out_file.close()
