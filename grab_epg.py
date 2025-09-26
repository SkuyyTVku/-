import requests
import lxml.etree as ET
import json
import re

# Load config
with open("config.json") as f:
    config = json.load(f)

output_file = config["output"]
root = ET.Element("tv")

# Hanya domain ini yang dibersihkan
suffixes = (".id", ".sg", ".my", ".th")


def clean_channel_id(ch_id: str) -> str:
    """Bersihkan hanya suffix tertentu (.id, .sg, .my, .th)"""
    if not ch_id:
        return ch_id

    original = ch_id.strip()  # hilangkan spasi
    lowered = original.lower()

    for suf in suffixes:
        if lowered.endswith(suf):
            cleaned = original[: -len(suf)] + ".SKUYYTV"
            print(f"[CLEAN] {original} -> {cleaned}")
            return cleaned

    # kalau tidak masuk suffix di atas, tetap normal
    return original


for source in config["sources"]:
    url = source["url"]
    name = source["name"]
    try:
        print(f"[{name}] Fetching {url} ...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        xml_data = ET.fromstring(r.content)

        for elem in xml_data:
            # Edit channel
            if elem.tag == "channel":
                if "id" in elem.attrib and elem.attrib["id"].strip():
                    elem.attrib["id"] = clean_channel_id(elem.attrib["id"])
                for dn in elem.findall("display-name"):
                    if dn.text and dn.text.strip():
                        dn.text = clean_channel_id(dn.text)

            # Edit programme
            if elem.tag == "programme":
                if "channel" in elem.attrib and elem.attrib["channel"].strip():
                    elem.attrib["channel"] = clean_channel_id(elem.attrib["channel"])

            root.append(elem)

    except Exception as e:
        print(f"[{name}] Error ambil data: {e}")

tree = ET.ElementTree(root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"✅ Generate EPG selesai -> {output_file}")
