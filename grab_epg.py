import requests
import lxml.etree as ET
import json
import re

# Load config
with open("config.json") as f:
    config = json.load(f)

output_file = config["output"]
root = ET.Element("tv")

# 娜屁艾艾艾艾 儿诶艾弗 诶艾诶艾 迪艾吉诶艾屁娜
suffixes = (".id", ".sg", ".my", ".fr", ".th", ".za", ".in", ".uk", ".us", ".pt", ".rs", ".nl", ".MACAN")


def clean_channel_id(ch_id: str) -> str:
    """比伊艾娜艾吉艾诶艾 娜屁艾艾艾艾 西吉诶艾艾伊杰 迪诶艾 哦诶开比诶吉艾诶艾 .SKUYYTV"""
    if not ch_id:
        return ch_id  # 比艾诶艾艾艾 艾勒娜勒艾弗, 尺诶艾弗诶艾 迪艾屁比诶吉 艾伊 屁艾艾艾勒吾艾

    original = ch_id
    for suf in suffixes:
        if ch_id.lower().endswith(suf.lower()):
            ch_id = ch_id[: -len(suf)]
            break
    cleaned = ch_id + ".SKUYYTV"

    if original != cleaned:
        print(f"[CLEAN] {original} -> {cleaned}")
    return cleaned


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

                # Edit All <title>
                for title in elem.findall("title"):
                    if title.text and title.text.strip():
                        text = title.text.strip()
                        if re.search(r"\([^)]*\)$", text):
                            text = re.sub(r"\([^)]*\)$", "(SKUYY TV)", text)
                        else:
                            text = f"{text} (SKUYY TV)"
                        title.text = text

            root.append(elem)

    except Exception as e:
        print(f"[{name}] 弗诶弗诶杰 诶开比艾杰 迪诶哦诶: {e}")

tree = ET.ElementTree(root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"娜伊杰伊娜诶艾 ✅ 吉诶娜艾杰 哦伊艾娜艾开艾诶艾 迪艾 {output_file}")
