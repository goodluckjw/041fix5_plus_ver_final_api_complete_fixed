import re

import requests
from utils.xml_parser import parse_law_xml

OC = "chetera"
BASE = "http://www.law.go.kr"

def fetch_law_list_and_detail(query, unit):
    from urllib.parse import quote
    encoded_query = quote(f'"{query}"')
    url = f"{BASE}/DRF/lawSearch.do?OC={OC}&target=law&type=XML&display=10&search=2&knd=A0002&query={encoded_query}"
    res = requests.get(url)
    res.encoding = "utf-8"
    if res.status_code != 200:
        return []

    import xml.etree.ElementTree as ET
    root = ET.fromstring(res.content)
    terms = [t.strip() for t in re.split(r"[,&\-()]", query or "") if t.strip()]
    results = []

    for law in root.findall("law"):
        name = law.findtext("법령명한글", "").strip()
        mst = law.findtext("법령일련번호", "")
        detail = law.findtext("법령상세링크", "")
        full_link = BASE + detail
        xml_data = fetch_law_xml_by_mst(mst)
        if xml_data:
            articles = parse_law_xml(xml_data, terms, unit)
            if articles:
                results.append({
                    "법령명한글": name,
                    "원문링크": full_link,
                    "조문": articles
                })
    return results

def fetch_law_xml_by_mst(mst):
    url = f"{BASE}/DRF/lawService.do?OC={OC}&target=law&MST={mst}&type=XML"
    try:
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"
        if res.status_code == 200:
            return res.content
    except Exception:
        return None
