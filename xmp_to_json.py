import sys
import os
import json
import xml.etree.ElementTree as ET

def parse_value(value):
    value = value.strip()
    if value.lower() == 'true': return True
    if value.lower() == 'false': return False
    try:
        if '.' in value: return float(value)
        return int(value)
    except ValueError:
        return value

def convert_xmp_to_json(input_xmp, output_json):
    if not os.path.exists(input_xmp) or not input_xmp.lower().endswith(".xmp"):
        print("❌ Invalid or missing .xmp file.")
        sys.exit(1)

    try:
        tree = ET.parse(input_xmp)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ Error parsing XMP: {e}")
        sys.exit(2)

    NS_CRS = "{http://ns.adobe.com/camera-raw-settings/1.0/}"
    NS_RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    develop_settings = {}
    nested_masks = []

    for elem in root.iter():
        tag = elem.tag
        # Handle flat crs:* tags
        if tag.startswith(NS_CRS):
            key = tag.replace(NS_CRS, "")
            value = (elem.text or "").strip()
            if (
                value != "" and
                "mask" not in key.lower() and
                "correction" not in key.lower() and
                key.lower() not in ["name", "shortname", "sortname", "group", "description", "look"]
            ):
                develop_settings[key] = parse_value(value)

        # Handle nested correction/mask values
        if tag == f"{NS_RDF}Description":
            attributes = elem.attrib
            nested = {}
            for attr_key, attr_val in attributes.items():
                if attr_key.startswith(NS_CRS):
                    clean_key = attr_key.replace(NS_CRS, "")
                    nested[clean_key] = parse_value(attr_val)
            if nested:
                nested_masks.append(nested)

    if not develop_settings and not nested_masks:
        print("⚠️ No develop settings or nested corrections found.")
        sys.exit(3)

    output = {
        "filename": os.path.basename(input_xmp),
        "presetName": "Recovered from XMP",
        "description": "Auto-converted from .xmp",
        "settings": develop_settings
    }

    if nested_masks:
        output["maskingCorrections"] = nested_masks

    try:
        with open(output_json, 'w') as f:
            json.dump(output, f, indent=4)
        print(f"✅ Converted successfully to: {output_json}")
    except Exception as e:
        print(f"❌ Error writing JSON: {e}")
        sys.exit(4)

# --- Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python xmp_to_json.py <input.xmp> <output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_xmp_to_json(input_file, output_file)
