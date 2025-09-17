import requests
import lxml.etree as ET
import json
import re

# Baca config
with open("config.json") as f:
    config = json.load(f)

output_file = config["output"]
root = ET.Element("tv")

for source in config["sources"]:
    url = source["url"]
    name = source["name"]
    try:
        print(f"[{name}] Fetching {url} ...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        xml_data = ET.fromstring(r.content)

        for elem in xml_data:
            if elem.tag == "programme":
                # Edit semua <title>
                for title in elem.findall("title"):
                    if title.text:
                        text = title.text.strip()
                        # 尺艾艾诶 诶迪诶 哦伊艾娜 迪诶杰诶开 艾屁艾屁艾弗 迪艾 诶艾吉艾艾 → 弗诶艾哦艾
                        if re.search(r"\([^)]*\)$", text):
                            text = re.sub(r"\([^)]*\)$", "(SKUYY TV)", text)
                        else:
                            # 艾诶杰诶屁 哦艾迪诶艾 诶迪诶 → 哦诶开比诶吉艾诶艾
                            text = f"{text} (SKUYY TV)"
                        title.text = text

            root.append(elem)

    except Exception as e:
        print(f"[{name}] Gagal ambil: {e}")

tree = ET.ElementTree(root)
tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Selesai, hasil di {output_file}")
