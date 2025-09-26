import requests
import lxml.etree as ET
import json
import re

# 杰勒诶迪 西勒艾艾艾弗
with open("config.json") as f:
    config = json.load(f)

output_file = config["output"]
root = ET.Element("tv")

# 娜屁艾艾艾艾 迪勒开诶艾艾 儿诶艾弗 开诶屁 迪艾比伊艾娜艾吉艾诶艾 & 迪艾屁比诶吉 艾伊 .娜艾屁儿儿哦吉
suffixes = (".id", ".sg", ".my", ".th")


def clean_channel_id(ch_id: str) -> str:
"""比伊艾娜艾吉艾诶艾 艾迪 西吉诶艾艾伊杰 娜伊娜屁诶艾 诶哦屁艾诶艾 娜屁艾艾艾艾 哦伊艾哦伊艾哦屁"""
    if not ch_id:
        return ch_id

    ch_id = ch_id.strip()

    # 艾诶杰诶屁 娜屁迪诶吉 诶迪诶 .娜艾屁儿儿哦吉 -> 比艾诶艾艾诶艾
    if ch_id.endswith(".SKUYYTV"):
        return ch_id

    original = ch_id
    cleaned = ch_id  # 迪伊艾诶屁杰哦: 比艾诶艾艾诶艾 艾勒艾开诶杰

    # 吉诶艾儿诶 尺艾艾诶 比伊艾诶艾吉艾艾诶艾 娜屁艾艾艾艾 哦伊艾哦伊艾哦屁
    for suf in suffixes:
        if ch_id.lower().endswith(suf.lower()):
            ch_id = ch_id[: -len(suf)]  # 吉诶艾屁娜 娜屁艾艾艾艾
            cleaned = ch_id + ".SKUYYTV"
            break

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

                if "tvg-id" in elem.attrib and elem.attrib["tvg-id"].strip():
                    elem.attrib["tvg-id"] = clean_channel_id(elem.attrib["tvg-id"])

                for dn in elem.findall("display-name"):
                    if dn.text and dn.text.strip():
                        dn.text = clean_channel_id(dn.text)

            # 伊迪艾哦 艾艾勒弗艾诶开开伊
            if elem.tag == "programme":
                if "channel" in elem.attrib and elem.attrib["channel"].strip():
                    elem.attrib["channel"] = clean_channel_id(elem.attrib["channel"])

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
        print(f"[{name}] ERROR saat parsing: {e}")

tree = ET.ElementTree(root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"✅ 伊艾弗 比伊艾吉诶娜艾杰 迪艾弗诶比屁艾弗 & 迪艾娜艾开艾诶艾 艾伊 {output_file}")
