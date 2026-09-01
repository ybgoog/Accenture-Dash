import zipfile
import xml.etree.ElementTree as ET

xlsx_path = ".shared/uploads/Accenture - Top Accounts - EMEA - FY26 (2).xlsx"

with zipfile.ZipFile(xlsx_path, 'r') as z:
    wb_xml = z.read("xl/workbook.xml")
    root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    shared_strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        sst_xml = z.read("xl/sharedStrings.xml")
        sst_root = ET.fromstring(sst_xml)
        for si in sst_root.findall('.//main:si', ns):
            texts = [t.text for t in si.findall('.//main:t', ns) if t.text]
            shared_strings.append("".join(texts))

    rels_xml = z.read("xl/_rels/workbook.xml.rels")
    rels_root = ET.fromstring(rels_xml)
    rel_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    sheet_files = {}
    for r in rels_root.findall('.//r:Relationship', rel_ns):
        sheet_files[r.attrib.get('Id')] = r.attrib.get('Target')
        
    for s in root.findall('.//main:sheet', ns):
        name = s.attrib.get('name')
        r_id = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target = sheet_files.get(r_id, '')
        if not target.startswith('xl/'):
            target = 'xl/' + target.lstrip('/')
        if 'Won' in name or 'Revenue' in name or 'Commit' in name:
            s_xml = z.read(target)
            s_root = ET.fromstring(s_xml)
            rows = s_root.findall('.//main:row', ns)
            print(f"Sheet '{name}': {len(rows)} rows")
            for r in rows[:4]:
                r_vals = []
                for c in r.findall('.//main:c', ns):
                    t = c.attrib.get('t')
                    v = c.find('main:v', ns)
                    val = v.text if v is not None else ""
                    if t == 's' and val != "":
                        val = shared_strings[int(val)] if int(val) < len(shared_strings) else val
                    r_vals.append(val)
                print("  ", r_vals[:8])
