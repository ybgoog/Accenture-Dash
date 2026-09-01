import json
import zipfile
import xml.etree.ElementTree as ET
import os

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
        
    sheets = {}
    for s in root.findall('.//main:sheet', ns):
        name = s.attrib.get('name')
        r_id = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target = sheet_files.get(r_id, '')
        if not target.startswith('xl/'):
            target = 'xl/' + target.lstrip('/')
        sheets[name] = target

    def parse_sheet(s_file):
        if s_file not in z.namelist():
            return []
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

    # 1. Accounts
    s1_rows = parse_sheet(sheets.get("2026 Key Accounts"))
    accounts = []
    for r in s1_rows[4:]:
        acct_name = r.get('C', '').strip()
        if acct_name and acct_name != '-':
            prio_raw = r.get('G', '').strip()
            try:
                prio = str(int(float(prio_raw))) if prio_raw and prio_raw != '-' else '-'
            except:
                prio = prio_raw

            acct = {
                'id': r.get('AA', '').strip() or f"ACCT-{len(accounts)+1}",
                'gsi': r.get('A', 'Accenture'),
                'is_emea_focus': r.get('B', '0') == '1' or r.get('B', '') == '1.0',
                'name': acct_name,
                'sub_region': r.get('D', '').strip() or 'EMEA',
                'vector_link': r.get('E', '').strip(),
                'strategy': r.get('F', '').strip() or 'Joint Growth',
                'priority': prio,
                'is_market_mover': 'Yes' if ('market mover' in r.get('H', '').lower() or r.get('AD', '') == '1') else ('No' if r.get('H','') == '-' else r.get('H','-')),
                'type': r.get('I', '').strip() or 'SPENDER',
                'industry': r.get('J', '').strip() or 'Cross-Industry',
                'sales_plays': {
                    'mmb': r.get('L', '').strip(),
                    'vmware': r.get('M', '').strip(),
                    'oracle': r.get('N', '').strip(),
                    'sap': r.get('O', '').strip(),
                    'data_analytics': r.get('P', '').strip(),
                    'build_ai': r.get('Q', '').strip(),
                    'gemini_ent': r.get('R', '').strip(),
                    'ai': r.get('S', '').strip(),
                    'ces': r.get('T', '').strip(),
                    'security': r.get('U', '').strip(),
                    'sovereignty': r.get('V', '').strip(),
                    'gdc': r.get('W', '').strip()
                },
                'next_steps': r.get('X', '').strip(),
                'fsr': r.get('Y', '').strip(),
                'comments': r.get('Z', '').strip(),
                'opps_q1': float(r.get('AH', 0) or 0),
                'opps_q2': float(r.get('AI', 0) or 0),
                'opps_q3': float(r.get('AJ', 0) or 0),
                'opps_q4': float(r.get('AK', 0) or 0),
                'val_q1': float(r.get('AL', 0) or 0),
                'val_q2': float(r.get('AM', 0) or 0),
                'val_q3': float(r.get('AN', 0) or 0),
                'val_q4': float(r.get('AO', 0) or 0),
            }
            accounts.append(acct)

    # 2. Opportunities
    s2_rows = parse_sheet(sheets.get("Pipe line Raw Data - Extract"))
    raw_opps = []
    for r in s2_rows[1:]:
        if not r.get('E'):
            continue
        def safe_float(v):
            try:
                return float(v) if v not in (None, '', '-') else 0.0
            except:
                return 0.0
        
        opp = {
            'sfdc_account_id': r.get('A', '').strip(),
            'child_account_name': r.get('B', '').strip(),
            'reporting_account_name': r.get('C', '').strip(),
            'partner': r.get('D', '').strip(),
            'opportunity_id': r.get('E', '').strip(),
            'opportunity_name': r.get('F', '').strip(),
            'stage': r.get('G', '').strip() or '01 - Refine',
            'sub_region': r.get('H', '').strip() or 'EMEA',
            'close_date_raw': r.get('I', '').strip(),
            'create_date_raw': r.get('J', '').strip(),
            'is_commit': r.get('K', '') == '1' or r.get('K', '') == '1.0',
            'sales_play': r.get('L', '').strip() or 'General Cloud',
            'usd_acv': safe_float(r.get('M')),
            'usd_incremental_acv': safe_float(r.get('N')),
            'usd_total_amount': safe_float(r.get('O')),
            'close_quarter': r.get('P', '').strip() or 'Q3',
            'create_quarter': r.get('Q', '').strip() or 'Q1'
        }
        raw_opps.append(opp)

    # 3. Sheet 4: Sales Play Matrix
    s4_rows = parse_sheet(sheets.get("Sales Play By Sub Region"))
    s4_data = []
    if s4_rows:
        for r in s4_rows[1:15]:
            play = r.get('A', '').strip()
            if play:
                s4_data.append({
                    'play': play,
                    'benelux': r.get('B', '').strip(),
                    'cee': r.get('C', '').strip(),
                    'dach': r.get('D', '').strip(),
                    'france': r.get('E', '').strip(),
                    'iberia': r.get('F', '').strip(),
                    'israel': r.get('G', '').strip(),
                    'italy': r.get('H', '').strip(),
                    'menat': r.get('I', '').strip(),
                    'nordics': r.get('J', '').strip()
                })

payload = {
    'accounts': accounts,
    'opportunities': raw_opps,
    'sales_play_matrix': s4_data
}

with open('full_data_payload.json', 'w') as f:
    json.dump(payload, f)

print("Data payload generated successfully.")
