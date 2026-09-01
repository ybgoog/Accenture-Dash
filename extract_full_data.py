import zipfile
import xml.etree.ElementTree as ET
import json
import datetime

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

    # 1. Sheet 1: 2026 Key Accounts
    s1_rows = parse_sheet(sheets.get("2026 Key Accounts"))
    # Row 4 is header
    accounts = []
    for r in s1_rows[4:]:
        acct_name = r.get('C', '').strip()
        if acct_name and acct_name != '-':
            # clean priority
            prio_raw = r.get('G', '').strip()
            try:
                prio = str(int(float(prio_raw))) if prio_raw and prio_raw != '-' else '-'
            except:
                prio = prio_raw

            acct = {
                'gsi': r.get('A', 'Accenture'),
                'is_emea_focus': r.get('B', '0') == '1' or r.get('B', '') == '1.0',
                'name': acct_name,
                'sub_region': r.get('D', '').strip(),
                'vector_link': r.get('E', '').strip(),
                'strategy': r.get('F', '').strip(),
                'priority': prio,
                'is_market_mover': 'Yes' if ('market mover' in r.get('H', '').lower() or r.get('AD', '') == '1') else ('No' if r.get('H','') == '-' else r.get('H','-')),
                'type': r.get('I', '').strip(),
                'industry': r.get('J', '').strip(),
                'sales_plays': {
                    'mmb': r.get('L', ''),
                    'vmware': r.get('M', ''),
                    'oracle': r.get('N', ''),
                    'sap': r.get('O', ''),
                    'data_analytics': r.get('P', ''),
                    'build_ai': r.get('Q', ''),
                    'gemini_ent': r.get('R', ''),
                    'ai': r.get('S', ''),
                    'ces': r.get('T', ''),
                    'security': r.get('U', ''),
                    'sovereignty': r.get('V', ''),
                    'gdc': r.get('W', '')
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

    # 2. Sheet 2: Pipe line Raw Data - Extract
    s2_rows = parse_sheet(sheets.get("Pipe line Raw Data - Extract"))
    # Header row is index 0: sfdc_account_id, child_account_name, reporting_account_name, partner_group_name, opportunity_id, opportunity_name, stage_name, sub_region, close_date, create_date, is_commit, sales_play, usd_acv, usd_incremental_acv, usd_total_amount, Close Quarter, Create Quarter
    raw_opps = []
    col_map = {
        'A': 'sfdc_account_id', 'B': 'child_account_name', 'C': 'reporting_account_name',
        'D': 'partner_group_name', 'E': 'opportunity_id', 'F': 'opportunity_name',
        'G': 'stage_name', 'H': 'sub_region', 'I': 'close_date', 'J': 'create_date',
        'K': 'is_commit', 'L': 'sales_play', 'M': 'usd_acv', 'N': 'usd_incremental_acv',
        'O': 'usd_total_amount', 'P': 'close_quarter', 'Q': 'create_quarter'
    }
    for r in s2_rows[1:]:
        if not r.get('E'):
            continue
        def safe_float(v):
            try:
                return float(v) if v not in (None, '', '-') else 0.0
            except:
                return 0.0
        
        opp = {
            'sfdc_account_id': r.get('A', ''),
            'child_account_name': r.get('B', ''),
            'reporting_account_name': r.get('C', ''),
            'partner': r.get('D', ''),
            'opportunity_id': r.get('E', ''),
            'opportunity_name': r.get('F', ''),
            'stage': r.get('G', ''),
            'sub_region': r.get('H', ''),
            'close_date_raw': r.get('I', ''),
            'create_date_raw': r.get('J', ''),
            'is_commit': r.get('K', '') == '1' or r.get('K', '') == '1.0',
            'sales_play': r.get('L', '') or 'General Cloud',
            'usd_acv': safe_float(r.get('M')),
            'usd_incremental_acv': safe_float(r.get('N')),
            'usd_total_amount': safe_float(r.get('O')),
            'close_quarter': r.get('P', ''),
            'create_quarter': r.get('Q', '')
        }
        raw_opps.append(opp)

    # 3. Sheet 4: Sales Play By Sub Region
    s4_rows = parse_sheet(sheets.get("Sales Play By Sub Region"))
    s4_data = []
    if s4_rows:
        s4_headers = [s4_rows[0].get(k, '') for k in ['A','B','C','D','E','F','G','H','I','J'] if k in s4_rows[0]]
        for r in s4_rows[1:15]:
            play = r.get('A', '')
            if play:
                s4_data.append({
                    'play': play,
                    'benelux': r.get('B', ''),
                    'cee': r.get('C', ''),
                    'dach': r.get('D', ''),
                    'france': r.get('E', ''),
                    'iberia': r.get('F', ''),
                    'israel': r.get('G', ''),
                    'italy': r.get('H', ''),
                    'menat': r.get('I', ''),
                    'nordics': r.get('J', '')
                })

    # Summary analysis
    print(f"Parsed {len(accounts)} Accounts from Sheet 1")
    print(f"Parsed {len(raw_opps)} Opportunities from Sheet 2")
    
    accenture_opps = [o for o in raw_opps if o['partner'] == 'Accenture']
    print(f"Accenture Opportunities count: {len(accenture_opps)}")
    
    total_acn_acv = sum(o['usd_acv'] for o in accenture_opps)
    total_acn_total = sum(o['usd_total_amount'] for o in accenture_opps)
    print(f"Total Accenture ACV: ${total_acn_acv:,.2f} | Total Amount: ${total_acn_total:,.2f}")
    
    # Save full json dump
    data_dump = {
        'accounts': accounts,
        'opportunities': raw_opps,
        'sales_play_matrix': s4_data
    }
    with open('extracted_data.json', 'w') as out:
        json.dump(data_dump, out, indent=2)

