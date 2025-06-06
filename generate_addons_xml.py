import os
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_addons_xml():
    """Create addons.xml file from all addon directories."""
    addons = ET.Element("addons")
    
    # Walk through all directories
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            addon_xml = os.path.join(root, dir_name, "addon.xml")
            if os.path.exists(addon_xml):
                try:
                    tree = ET.parse(addon_xml)
                    addon = tree.getroot()
                    addons.append(addon)
                except Exception as e:
                    print(f"Error parsing {addon_xml}: {e}")

    # Write addons.xml
    with open("addons.xml", "w", encoding="utf-8") as f:
        f.write(prettify(addons))

    # Create addons.xml.md5
    with open("addons.xml", "r", encoding="utf-8") as f:
        content = f.read()
        md5 = hashlib.md5(content.encode("utf-8")).hexdigest()
    
    with open("addons.xml.md5", "w", encoding="utf-8") as f:
        f.write(md5)

if __name__ == "__main__":
    create_addons_xml() 