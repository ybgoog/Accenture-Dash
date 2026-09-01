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
            
    def parse_sheet(s_file):
        s_xml = z.read(s_file)
        s_root = ET.fromstring(s_xml)
        rows = []
        for r in s_root.findall('.//main:row', ns):
            row_dict = {}
            for c in r.findall('.//main:c', ns):
                coord = c.attrib.get('r')
                col_letter = ''.join([ch for ch in coord if ch.isalpha()])
                t = c.attrib.get('t')
                v = c.find('main:v', ns)
                val = v.text if v is not None else ""
                if t == 's' and val != "":
                    val = shared_strings[int(val)] if int(val) < len(shared_strings) else val
                elif t == 'inlineStr':
                    is_elem = c.find('main:is/main:t', ns)
                    if is_elem is not None:
                        val = is_elem.text
                row_dict[col_letter] = val
            rows.append(row_dict)
        return rows

    # Sheet 1: 2026 Key Accounts
    sheet1_rows = parse_sheet("xl/worksheets/sheet1.xml")
    print(f"Sheet 1 total rows: {len(sheet1_rows)}")
    header_row = sheet1_rows[3] # Row 4 has headers
    print("Sheet 1 headers (Row 4):", header_row)
    
    # Sample non-empty accounts
    accounts = []
    for r in sheet1_rows[4:]:
        acct_name = r.get('C', '').strip()
        if acct_name and acct_name != '-':
            accounts.append(r)
    print(f"Valid accounts in Sheet 1: {len(accounts)}")
    for a in accounts[:5]:
        print("Sample Account:", {k: a[k] for k in ['A','B','C','D','F','G','H','I','J','Q','R','U','V','X'] if k in a})

