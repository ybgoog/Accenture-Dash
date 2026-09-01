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

    # Let's inspect 'Pipe line Raw Data - Extract' and '2026 Key Accounts'
    def get_sheet_data(sheet_filename):
        s_xml = z.read(sheet_filename)
        s_root = ET.fromstring(s_xml)
        rows = s_root.findall('.//main:row', ns)
        out = []
        for r in rows:
            row_vals = []
            for c in r.findall('.//main:c', ns):
                t = c.attrib.get('t')
                v = c.find('main:v', ns)
                val = v.text if v is not None else ""
                if t == 's' and val != "":
                    val = shared_strings[int(val)] if int(val) < len(shared_strings) else val
                elif t == 'inlineStr':
                    is_elem = c.find('main:is/main:t', ns)
                    if is_elem is not None:
                        val = is_elem.text
                row_vals.append((c.attrib.get('r'), val))
            out.append(row_vals)
        return out

    # Let's check sheet 2 (Pipe line Raw Data - Extract)
    p_data = get_sheet_data("xl/worksheets/sheet2.xml")
    headers = [val for coord, val in p_data[0]]
    print("Pipe line headers:", headers)
    partners = {}
    for r in p_data[1:]:
        d = dict(r)
        # col D is partner_group_name
        p_name = None
        for k, v in r:
            if k.startswith('D'):
                p_name = v
        if p_name:
            partners[p_name] = partners.get(p_name, 0) + 1
    print("Partners count in Pipe line Raw Data:", partners)
