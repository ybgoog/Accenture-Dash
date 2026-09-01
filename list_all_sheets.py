import zipfile
import xml.etree.ElementTree as ET

xlsx_path = ".shared/uploads/Accenture - Top Accounts - EMEA - FY26 (2).xlsx"

with zipfile.ZipFile(xlsx_path, 'r') as z:
    wb_xml = z.read("xl/workbook.xml")
    root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheets = [s.attrib.get('name') for s in root.findall('.//main:sheet', ns)]
    
print("All Sheets in Workbook:")
for idx, s in enumerate(sheets):
    print(f"{idx+1}. {s}")
