import zipfile
import xml.etree.ElementTree as ET
import json
import re

xlsx_path = ".shared/uploads/Accenture - Top Accounts - EMEA - FY26 (2).xlsx"

with zipfile.ZipFile(xlsx_path, 'r') as z:
    # Get sheet names from workbook.xml
    wb_xml = z.read("xl/workbook.xml")
    root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    
    sheets = []
    for s in root.findall('.//main:sheet', ns):
        sheets.append((s.attrib.get('name'), s.attrib.get('sheetId'), s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')))
    
    # Get shared strings
    shared_strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        sst_xml = z.read("xl/sharedStrings.xml")
        sst_root = ET.fromstring(sst_xml)
        for si in sst_root.findall('.//main:si', ns):
            # get all text inside si
            texts = [t.text for t in si.findall('.//main:t', ns) if t.text]
            shared_strings.append("".join(texts))
            
    # Read workbook rels
    rels_xml = z.read("xl/_rels/workbook.xml.rels")
    rels_root = ET.fromstring(rels_xml)
    rel_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    sheet_files = {}
    for r in rels_root.findall('.//r:Relationship', rel_ns):
        sheet_files[r.attrib.get('Id')] = r.attrib.get('Target')
        
    print(f"Total Sheets: {len(sheets)}")
    for name, s_id, r_id in sheets:
        target = sheet_files.get(r_id, "")
        if not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        print(f"\n==========================================")
        print(f"Sheet Name: '{name}' | File: {target}")
        
        if target in z.namelist():
            s_xml = z.read(target)
            s_root = ET.fromstring(s_xml)
            rows = s_root.findall('.//main:row', ns)
            print(f"Row count: {len(rows)}")
            
            parsed_rows = []
            for row in rows[:25]:
                r_idx = row.attrib.get('r')
                cols = {}
                for c in row.findall('.//main:c', ns):
                    r_coord = c.attrib.get('r')
                    t = c.attrib.get('t')
                    v = c.find('main:v', ns)
                    val = v.text if v is not None else None
                    if t == 's' and val is not None:
                        val = shared_strings[int(val)] if int(val) < len(shared_strings) else val
                    elif t == 'inlineStr':
                        is_elem = c.find('main:is/main:t', ns)
                        if is_elem is not None:
                            val = is_elem.text
                    cols[r_coord] = val
                parsed_rows.append(cols)
                
            for idx, r in enumerate(parsed_rows[:15]):
                print(f"Row {idx+1}: {r}")

