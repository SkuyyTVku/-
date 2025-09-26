import requests
import lxml.etree as ET
import json
import re

# Load config
with open("config.json") as f:
    config = json.load(f)

output_file = config["output"]
root = ET.Element("tv")

# hanya domain ini yang diubah → jadi .SKUYYTV
suffixes = (".id", ".sg", ".my", ".th")


def clean_channel_id(ch_id: str) -> str:
    """Bersihkan hanya domain tertentu lalu tambah .SKUYYTV"""
    if not ch_id:
        return ch_id

    original = ch_id
    for suf in suffixes:
        if ch_id.lower().endswith(suf.lower()):
            ch_id = ch_id[: -len(suf)]
            cleaned = ch_id + ".SKUYYTV"
            if original != cleaned:
                print(f"[CLEAN] {original} -> {cleaned}")
            return cleaned

    # selain suffix di atas → biarkan
    return ch_id


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
        print(f"[{name}] ERROR ambil data: {e}")

tree = ET.ElementTree(root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"✅ Berhasil generate file EPG ke {output_file}")
