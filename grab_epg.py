import requests
import lxml.etree as ET
import json
import re

# 比诶西诶 西勒艾艾艾弗
with open("config.json") as f:
    config = json.load(f)

output_file = config["output"]
root = ET.Element("tv")

# 迪诶艾哦诶艾 诶艾吉艾艾诶艾 儿诶艾弗 开诶屁 迪艾吉诶艾屁娜
suffixes = (".id", ".sg", ".my", ".fr", ".uk", ".us", ".pt", ".rs", ".nl", ".MACAN")


def clean_channel_id(ch_id: str) -> str:
    """吉诶艾屁娜 诶艾吉艾艾诶艾 迪勒开诶艾艾 哦伊艾哦伊艾哦屁 杰诶杰屁 哦诶开比诶吉艾诶艾 .SKUYYTV"""
    for suf in suffixes:
        if ch_id.endswith(suf):
            ch_id = ch_id[: -len(suf)]
    return ch_id + ".SKUYYTV"


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
                if "id" in elem.attrib:
                    elem.attrib["id"] = clean_channel_id(elem.attrib["id"])
                for dn in elem.findall("display-name"):
                    if dn.text:
                        dn.text = clean_channel_id(dn.text)

            # 伊迪艾哦 艾艾勒弗艾诶开开伊
            if elem.tag == "programme":
                if "channel" in elem.attrib:
                    elem.attrib["channel"] = clean_channel_id(elem.attrib["channel"])

                # 伊迪艾哦 娜伊开屁诶 <title>
                for title in elem.findall("title"):
                    if title.text:
                        text = title.text.strip()
                        if re.search(r"\([^)]*\)$", text):
                            text = re.sub(r"\([^)]*\)$", "(SKUYY TV)", text)
                        else:
                            text = f"{text} (SKUYY TV)"
                        title.text = text

            root.append(elem)

    except Exception as e:
        print(f"[{name}] 弗诶弗诶杰 诶开比艾杰: {e}")

tree = ET.ElementTree(root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Selesai, hasil di {output_file}")
