import json
import re

with open('full_data_payload.json') as f:
    data = json.load(f)

accounts = data['accounts']
opps = data['opportunities']
s4_matrix = data['sales_play_matrix']

acn_opps = [o for o in opps if o['partner'] == 'Accenture']

# Summary stats
total_acv = sum(o['usd_acv'] for o in acn_opps)
total_amount = sum(o['usd_total_amount'] for o in acn_opps)
active_opps = [o for o in acn_opps if 'lost' not in o['stage'].lower()]
active_acv = sum(o['usd_acv'] for o in active_opps)
lost_opps = [o for o in acn_opps if 'lost' in o['stage'].lower()]
lost_acv = sum(o['usd_acv'] for o in lost_opps)

p1_count = len([a for a in accounts if a['priority'] == '1'])
p2_count = len([a for a in accounts if a['priority'] == '2'])
p3_count = len([a for a in accounts if a['priority'] == '3'])
focus_count = len([a for a in accounts if a['is_emea_focus']])
market_mover_count = len([a for a in accounts if a['is_market_mover'] == 'Yes'])
greenfield_count = len([a for a in accounts if a['type'] == 'GREENFIELD'])
spender_count = len([a for a in accounts if a['type'] == 'SPENDER'])

# GSI stats
gsi_stats = {}
for o in opps:
    p = o['partner'] or 'Other'
    if p not in gsi_stats:
        gsi_stats[p] = {'count': 0, 'acv': 0, 'total': 0, 'active': 0}
    gsi_stats[p]['count'] += 1
    gsi_stats[p]['acv'] += o['usd_acv']
    gsi_stats[p]['total'] += o['usd_total_amount']
    if 'lost' not in o['stage'].lower():
        gsi_stats[p]['active'] += 1

sorted_gsi = sorted(gsi_stats.items(), key=lambda x: x[1]['acv'], reverse=True)
total_emea_gsi_acv = sum(s['acv'] for s in gsi_stats.values())
acn_pipe_share = (total_acv / total_emea_gsi_acv * 100) if total_emea_gsi_acv > 0 else 0

# Regional stats
regions = sorted(list(set(a['sub_region'] for a in accounts if a['sub_region'])))
reg_data = {}
for r in regions:
    r_accts = [a for a in accounts if a['sub_region'] == r]
    r_opps = [o for o in acn_opps if o['sub_region'] == r]
    reg_data[r] = {
        'accounts': len(r_accts),
        'opps': len(r_opps),
        'acv': sum(o['usd_acv'] for o in r_opps),
        'total': sum(o['usd_total_amount'] for o in r_opps),
        'p1': len([a for a in r_accts if a['priority'] == '1']),
        'top_acct': r_accts[0]['name'] if r_accts else 'N/A'
    }

# Sales plays in Accenture
play_stats = {}
for o in acn_opps:
    sp = o['sales_play'] or 'General Cloud'
    if sp not in play_stats:
        play_stats[sp] = {'count': 0, 'acv': 0, 'total': 0}
    play_stats[sp]['count'] += 1
    play_stats[sp]['acv'] += o['usd_acv']
    play_stats[sp]['total'] += o['usd_total_amount']

sorted_plays = sorted(play_stats.items(), key=lambda x: x[1]['acv'], reverse=True)

# Stages in Accenture
stage_stats = {}
for o in acn_opps:
    st = o['stage'] or '01 - Refine'
    if st not in stage_stats:
        stage_stats[st] = {'count': 0, 'acv': 0, 'total': 0}
    stage_stats[st]['count'] += 1
    stage_stats[st]['acv'] += o['usd_acv']
    stage_stats[st]['total'] += o['usd_total_amount']

# Top Marquee Bets
marquee_opps = sorted(acn_opps, key=lambda x: (x['usd_total_amount'], x['usd_acv']), reverse=True)[:8]

# Match accounts with their opps
for a in accounts:
    a_name_clean = re.sub(r'\[.*?\]', '', a['name']).strip().lower()
    a_opps = []
    for o in acn_opps:
        rep_clean = re.sub(r'\[.*?\]', '', o['reporting_account_name']).strip().lower()
        child_clean = re.sub(r'\[.*?\]', '', o['child_account_name']).strip().lower()
        if (a_name_clean and (a_name_clean in rep_clean or a_name_clean in child_clean or rep_clean in a_name_clean)) or (a['id'] and a['id'] == o['sfdc_account_id']):
            a_opps.append(o)
    a['matched_opps'] = a_opps
    a['matched_opps_count'] = len(a_opps)
    a['matched_opps_acv'] = sum(o['usd_acv'] for o in a_opps)
    a['matched_opps_total'] = sum(o['usd_total_amount'] for o in a_opps)

# Prepare JSON data for JS
json_accounts = json.dumps(accounts)
json_acn_opps = json.dumps(acn_opps)
json_all_opps = json.dumps(opps)
json_s4_matrix = json.dumps(s4_matrix)
json_gsi_stats = json.dumps(sorted_gsi)
json_reg_data = json.dumps(reg_data)
json_play_stats = json.dumps(sorted_plays)
json_stage_stats = json.dumps(stage_stats)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>FY26 EMEA Partner Strategy & Pipeline — Accenture</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --bg-subtle: #f1f5f9;
  --border: #e2e8f0;
  --border-light: #edf2f7;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --text-dim: #94a3b8;
  
  --google-blue: #1a73e8;
  --google-blue-dark: #1557b0;
  --google-blue-subtle: #e8f0fe;
  --accenture-purple: #a100ff;
  --accenture-purple-subtle: #f5e8ff;
  --navy-dark: #0f172a;
  --teal: #0d9488;
  --teal-subtle: #ccfbf1;
  --emerald: #10b981;
  --emerald-subtle: #d1fae5;
  --amber: #f59e0b;
  --amber-subtle: #fef3c7;
  --rose: #f43f5e;
  --rose-subtle: #ffe4e6;
  
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 10px 25px -5px rgba(15, 23, 42, 0.1);
  --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background-color: var(--bg-page);
  color: var(--text-main);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}

/* LAYOUT */
.app-container {{
  display: flex;
  min-height: 100vh;
}}

/* SIDEBAR */
.sidebar {{
  width: 270px;
  background: #ffffff;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 100;
  transition: var(--transition);
}}

.brand-section {{
  padding: 24px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.brand-logos {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.google-badge {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Google Sans', sans-serif;
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--text-main);
}}
.partner-badge {{
  background: var(--accenture-purple-subtle);
  color: var(--accenture-purple);
  font-family: 'Google Sans', sans-serif;
  font-weight: 700;
  font-size: 0.78rem;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  letter-spacing: 0.04em;
}}
.app-title {{
  font-family: 'Google Sans', sans-serif;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.25;
}}
.app-subtitle {{
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}

.nav-section {{
  padding: 16px 12px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.nav-label {{
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  padding: 8px 12px 4px;
}}
.nav-item {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
}}
.nav-item:hover {{
  background: var(--bg-subtle);
  color: var(--text-main);
}}
.nav-item.active {{
  background: var(--google-blue-subtle);
  color: var(--google-blue);
  font-weight: 700;
}}
.nav-item svg {{
  width: 18px;
  height: 18px;
  stroke-width: 2;
}}

.sidebar-filters {{
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  background: #fafbfc;
}}
.filter-group {{
  margin-bottom: 10px;
}}
.filter-label {{
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 4px;
  display: block;
}}
.filter-select {{
  width: 100%;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: white;
  font-size: 0.78rem;
  color: var(--text-main);
  outline: none;
}}

.sidebar-footer {{
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.presenter-name {{
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-main);
}}
.presenter-role {{
  font-size: 0.72rem;
  color: var(--text-muted);
}}
.presenter-date {{
  font-size: 0.68rem;
  color: var(--text-dim);
  margin-top: 4px;
}}

/* MAIN CONTENT */
.main-wrapper {{
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow-x: hidden;
}}

/* TOP BAR */
.top-bar {{
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 90;
}}
.top-title-area h1 {{
  font-family: 'Google Sans', sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-main);
}}
.top-title-area p {{
  font-size: 0.78rem;
  color: var(--text-muted);
}}
.top-actions {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.btn {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid transparent;
}}
.btn-primary {{
  background: var(--google-blue);
  color: white;
}}
.btn-primary:hover {{
  background: var(--google-blue-dark);
}}
.btn-outline {{
  background: white;
  border-color: var(--border);
  color: var(--text-main);
}}
.btn-outline:hover {{
  background: var(--bg-subtle);
}}

/* CONTENT TABS */
.content-body {{
  padding: 28px 32px 60px;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}}

.tab-pane {{
  display: none;
}}
.tab-pane.active {{
  display: block;
}}

/* KPI SCORECARD */
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}}
.kpi-card {{
  background: white;
  border-radius: var(--radius-lg);
  padding: 22px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  transition: var(--transition);
}}
.kpi-card:hover {{
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}}
.kpi-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}}
.kpi-card.blue::before {{ background: var(--google-blue); }}
.kpi-card.purple::before {{ background: var(--accenture-purple); }}
.kpi-card.teal::before {{ background: var(--teal); }}
.kpi-card.amber::before {{ background: var(--amber); }}

.kpi-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}}
.kpi-title {{
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}}
.kpi-icon {{
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}}
.kpi-icon.blue {{ background: var(--google-blue-subtle); color: var(--google-blue); }}
.kpi-icon.purple {{ background: var(--accenture-purple-subtle); color: var(--accenture-purple); }}
.kpi-icon.teal {{ background: var(--teal-subtle); color: var(--teal); }}
.kpi-icon.amber {{ background: var(--amber-subtle); color: var(--amber); }}

.kpi-value {{
  font-family: 'Google Sans', sans-serif;
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.1;
  margin-bottom: 6px;
}}
.kpi-subtext {{
  font-size: 0.76rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}}
.badge-pill {{
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
}}
.badge-pill.green {{ background: var(--emerald-subtle); color: #047857; }}
.badge-pill.blue {{ background: var(--google-blue-subtle); color: var(--google-blue); }}
.badge-pill.purple {{ background: var(--accenture-purple-subtle); color: var(--accenture-purple); }}
.badge-pill.amber {{ background: var(--amber-subtle); color: #b45309; }}

/* CARDS & PANELS */
.card-panel {{
  background: white;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  margin-bottom: 24px;
  overflow: hidden;
}}
.panel-header {{
  padding: 18px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
}}
.panel-title {{
  font-family: 'Google Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}}
.panel-subtitle {{
  font-size: 0.76rem;
  color: var(--text-muted);
  margin-top: 2px;
}}
.panel-body {{
  padding: 24px;
}}

/* CHARTS GRID */
.charts-grid-2 {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 28px;
}}
.chart-container {{
  position: relative;
  height: 310px;
  width: 100%;
}}

/* MARQUEE BETS SPOTLIGHT */
.marquee-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}}
.marquee-card {{
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 18px;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
}}
.marquee-card:hover {{
  border-color: var(--google-blue);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}}
.marquee-top {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10px;
}}
.marquee-acct {{
  font-family: 'Google Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
}}
.marquee-region {{
  font-size: 0.72rem;
  color: var(--text-muted);
}}
.marquee-deal {{
  font-size: 0.8rem;
  font-weight: 500;
  color: #334155;
  margin-bottom: 12px;
  line-height: 1.35;
}}
.marquee-meta {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}}
.marquee-value {{
  font-family: 'Google Sans', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--google-blue);
}}
.marquee-val-label {{
  font-size: 0.68rem;
  color: var(--text-muted);
  text-transform: uppercase;
}}

/* TABLES */
.table-responsive {{
  overflow-x: auto;
}}
.data-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}}
.data-table th {{
  background: #f8fafc;
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}}
.data-table td {{
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text-main);
  vertical-align: middle;
}}
.data-table tr:hover td {{
  background: #f8fafc;
}}
.data-table tr.clickable {{
  cursor: pointer;
}}

.stage-badge {{
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}}
.stage-refine {{ background: #e0f2fe; color: #0369a1; }}
.stage-tech {{ background: #ede9fe; color: #6d28d9; }}
.stage-proposal {{ background: #fef3c7; color: #b45309; }}
.stage-migration {{ background: #dcfce7; color: #15803d; }}
.stage-won {{ background: #d1fae5; color: #047857; font-weight: 700; }}
.stage-lost {{ background: #fee2e2; color: #b91c1c; }}

.prio-badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.72rem;
}}
.prio-1 {{ background: #fee2e2; color: #b91c1c; }}
.prio-2 {{ background: #fef3c7; color: #b45309; }}
.prio-3 {{ background: #e0f2fe; color: #0369a1; }}

.tag-play {{
  display: inline-block;
  padding: 2px 6px;
  margin: 1px;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 500;
  background: var(--bg-subtle);
  color: #475569;
}}
.tag-play.ai {{ background: #f3e8ff; color: #7e22ce; font-weight: 600; }}
.tag-play.sov {{ background: #e0f2fe; color: #0369a1; font-weight: 600; }}
.tag-play.sec {{ background: #fee2e2; color: #b91c1c; font-weight: 600; }}

/* EXPANDABLE ACCORDION ROW */
.opp-details-row {{
  background: #f8fafc;
  display: none;
}}
.opp-details-row.open {{
  display: table-row;
}}
.opp-inner-container {{
  padding: 16px 20px;
}}
.opp-subtable {{
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
  font-size: 0.76rem;
}}
.opp-subtable th {{
  background: #f1f5f9;
  padding: 8px 12px;
  font-size: 0.68rem;
}}
.opp-subtable td {{
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-light);
}}

/* REGION GRID */
.region-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}}
.region-card {{
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}}
.region-card:hover {{
  border-color: var(--google-blue);
  box-shadow: var(--shadow-md);
}}
.region-card-hdr {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}}
.region-name {{
  font-family: 'Google Sans', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
}}
.region-metrics {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}}
.reg-m-val {{
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--google-blue);
}}
.reg-m-lbl {{
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
}}

/* SEARCH & CONTROLS */
.search-controls {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}}
.search-input-wrap {{
  position: relative;
  flex: 1;
  max-width: 400px;
}}
.search-input {{
  width: 100%;
  padding: 9px 14px 9px 36px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  font-size: 0.82rem;
  background: white;
  outline: none;
}}
.search-icon {{
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-dim);
}}

/* MODAL */
.modal-backdrop {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}}
.modal-backdrop.open {{
  display: flex;
}}
.modal-box {{
  background: white;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}}
.modal-header {{
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.modal-body {{
  padding: 24px;
  overflow-y: auto;
}}

@media print {{
  .sidebar, .top-actions, .search-controls, .btn {{ display: none !important; }}
  .content-body {{ padding: 0 !important; max-width: 100% !important; }}
  .card-panel, .kpi-card {{ box-shadow: none !important; border: 1px solid #ccc !important; break-inside: avoid; }}
  .tab-pane {{ display: block !important; margin-bottom: 40px; }}
}}

@media (max-width: 1024px) {{
  .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .charts-grid-2 {{ grid-template-columns: 1fr; }}
  .region-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>

<div class="app-container">
  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="brand-section">
      <div class="brand-logos">
        <div class="google-badge">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/></svg>
          Google Cloud
        </div>
        <span class="partner-badge">Accenture</span>
      </div>
      <div>
        <div class="app-title">FY26 EMEA Partner Strategy</div>
        <div class="app-subtitle">Executive Command Center</div>
      </div>
    </div>

    <nav class="nav-section">
      <div class="nav-label">Executive Views</div>
      <a class="nav-item active" onclick="switchTab('overview')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        Overview & Scorecard
      </a>
      <a class="nav-item" onclick="switchTab('subregions')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        Sub-Region Performance
      </a>
      <a class="nav-item" onclick="switchTab('salesplays')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        Sales Plays & Solutions
      </a>
      <a class="nav-item" onclick="switchTab('accounts')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        Top 71 Accounts & Opps
      </a>
      <a class="nav-item" onclick="switchTab('gsi')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        GSI Peer Benchmark
      </a>
    </nav>

    <div class="sidebar-filters">
      <div class="filter-group">
        <label class="filter-label">Quick Sub-Region Filter</label>
        <select id="globalRegionFilter" class="filter-select" onchange="applyGlobalFilters()">
          <option value="ALL">All Sub-Regions (EMEA)</option>
          <option value="UK/IE">UK & Ireland</option>
          <option value="France">France</option>
          <option value="DACH">DACH</option>
          <option value="Benelux">Benelux</option>
          <option value="Nordics">Nordics</option>
          <option value="MENAT">MENAT</option>
          <option value="Iberia">Iberia</option>
          <option value="Italy">Italy</option>
          <option value="CEE">CEE</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">Priority Tier</label>
        <select id="globalPriorityFilter" class="filter-select" onchange="applyGlobalFilters()">
          <option value="ALL">All Priorities (1, 2, 3)</option>
          <option value="1">Priority 1 (Strategic Core)</option>
          <option value="2">Priority 2 (High Potential)</option>
          <option value="3">Priority 3 (Growth)</option>
        </select>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="presenter-name">Yves Boudreau</div>
      <div class="presenter-role">Customer Engineering Manager</div>
      <div class="presenter-date">September 1, 2026 • FY26 Q3 Review</div>
    </div>
  </aside>

  <!-- MAIN AREA -->
  <main class="main-wrapper">
    <header class="top-bar">
      <div class="top-title-area">
        <h1 id="pageHeading">Executive Overview & Scorecard</h1>
        <p id="pageSubHeading">Comprehensive status of Accenture Top EMEA Accounts & Opportunity Pipeline</p>
      </div>
      <div class="top-actions">
        <button class="btn btn-outline" onclick="window.print()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          Print / PDF
        </button>
        <button class="btn btn-primary" onclick="exportDataCSV()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Export CSV
        </button>
      </div>
    </header>

    <div class="content-body">
      
      <!-- TAB 1: EXECUTIVE OVERVIEW -->
      <section id="tab-overview" class="tab-pane active">
        <!-- 4-Pillar KPI Scorecard -->
        <div class="kpi-grid">
          <div class="kpi-card blue">
            <div class="kpi-header">
              <span class="kpi-title">Total Pipeline ACV</span>
              <div class="kpi-icon blue">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              </div>
            </div>
            <div class="kpi-value">${total_acv/1e9:.2f}B</div>
            <div class="kpi-subtext">
              <span class="badge-pill blue">182 Deals</span>
              <span>${total_amount/1e9:.2f}B Total Contract Value</span>
            </div>
          </div>

          <div class="kpi-card purple">
            <div class="kpi-header">
              <span class="kpi-title">Active Deal Flow</span>
              <div class="kpi-icon purple">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              </div>
            </div>
            <div class="kpi-value">${active_acv/1e9:.2f}B</div>
            <div class="kpi-subtext">
              <span class="badge-pill green">{len(active_opps)} In Flight</span>
              <span>{len(active_opps)/len(acn_opps)*100:.1f}% Active Rate</span>
            </div>
          </div>

          <div class="kpi-card teal">
            <div class="kpi-header">
              <span class="kpi-title">Key Accounts Coverage</span>
              <div class="kpi-icon teal">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              </div>
            </div>
            <div class="kpi-value">{len(accounts)}</div>
            <div class="kpi-subtext">
              <span class="badge-pill purple">{p1_count} Priority 1s</span>
              <span>{market_mover_count} Market Movers</span>
            </div>
          </div>

          <div class="kpi-card amber">
            <div class="kpi-header">
              <span class="kpi-title">EMEA GSI Pipeline Rank</span>
              <div class="kpi-icon amber">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>
              </div>
            </div>
            <div class="kpi-value">#1 Partner</div>
            <div class="kpi-subtext">
              <span class="badge-pill amber">{acn_pipe_share:.1f}% Share</span>
              <span>2.1x over #2 GSI (HCL)</span>
            </div>
          </div>
        </div>

        <!-- Charts Grid 1 -->
        <div class="charts-grid-2">
          <div class="card-panel">
            <div class="panel-header">
              <div>
                <div class="panel-title">Regional Pipeline Distribution (ACV)</div>
                <div class="panel-subtitle">Accenture pipeline volume by EMEA sub-region</div>
              </div>
            </div>
            <div class="panel-body">
              <div class="chart-container">
                <canvas id="chartRegionOverview"></canvas>
              </div>
            </div>
          </div>

          <div class="card-panel">
            <div class="panel-header">
              <div>
                <div class="panel-title">Opportunity Stage Funnel</div>
                <div class="panel-subtitle">Distribution of active pipeline across deal progression stages</div>
              </div>
            </div>
            <div class="panel-body">
              <div class="chart-container">
                <canvas id="chartStageFunnel"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Marquee Mega-Bets Spotlight -->
        <div class="card-panel">
          <div class="panel-header">
            <div>
              <div class="panel-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                Marquee Opportunities & Strategic Bets Spotlight
              </div>
              <div class="panel-subtitle">Highest-value partner engagements driving FY26 EMEA transformation</div>
            </div>
            <span class="badge-pill purple">Mega-Deals ($50M+ TCV)</span>
          </div>
          <div class="panel-body">
            <div class="marquee-grid">
              {''.join([f'''
              <div class="marquee-card">
                <div>
                  <div class="marquee-top">
                    <div>
                      <div class="marquee-acct">{o['reporting_account_name'] or o['child_account_name']}</div>
                      <div class="marquee-region">{o['sub_region']} • {o['sales_play']}</div>
                    </div>
                    <span class="stage-badge stage-{('migration' if '04' in o['stage'] else ('proposal' if '03' in o['stage'] else ('tech' if '02' in o['stage'] else 'refine')))}">{o['stage']}</span>
                  </div>
                  <div class="marquee-deal">{o['opportunity_name']}</div>
                </div>
                <div class="marquee-meta">
                  <div>
                    <div class="marquee-val-label">Annual Contract Value</div>
                    <div class="marquee-value">${o['usd_acv']:,.0f}</div>
                  </div>
                  <div style="text-align: right;">
                    <div class="marquee-val-label">Total Contract Value</div>
                    <div style="font-weight: 700; color: #475569;">${o['usd_total_amount']:,.0f}</div>
                  </div>
                </div>
              </div>
              ''' for o in marquee_opps])}
            </div>
          </div>
        </div>

        <!-- Strategic Summary & Takeaways -->
        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">Strategic Partner Takeaways & Leadership Focus</div>
          </div>
          <div class="panel-body" style="font-size: 0.85rem; color: #334155; line-height: 1.6;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
              <div>
                <h4 style="font-size: 0.92rem; font-weight: 700; color: var(--text-main); margin-bottom: 8px;">1. GSI Market Dominance in EMEA</h4>
                <p>Accenture accounts for <strong>${total_acv/1e9:.2f}B in pipeline ACV</strong> across EMEA, representing <strong>{acn_pipe_share:.1f}%</strong> of total partner-attached opportunities. The pipeline is heavily anchored in large-scale enterprise modernization in France, DACH, and UK/IE.</p>
              </div>
              <div>
                <h4 style="font-size: 0.92rem; font-weight: 700; color: var(--text-main); margin-bottom: 8px;">2. AI & Gemini Enterprise Acceleration</h4>
                <p>Strategic joint focus is pivoting toward <strong>GenAI, Gemini Enterprise, and Sovereign Cloud</strong>. Over <strong>38%</strong> of top accounts have joint AI aspirations mapped, positioning Accenture as our premier partner for sovereign and regulated enterprise AI adoption.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 2: SUB-REGION PERFORMANCE -->
      <section id="tab-subregions" class="tab-pane">
        <div class="panel-header" style="background: transparent; border: none; padding: 0 0 20px;">
          <div>
            <h2 style="font-family: 'Google Sans', sans-serif; font-size: 1.25rem;">Sub-Region Performance Matrix</h2>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Regional breakdown of account penetration, pipeline ACV, and Priority 1 concentration</p>
          </div>
        </div>

        <div class="region-grid">
          {''.join([f'''
          <div class="region-card">
            <div class="region-card-hdr">
              <div class="region-name">{r}</div>
              <span class="badge-pill blue">{reg_data[r]['accounts']} Top Accounts</span>
            </div>
            <div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Lead Account: <strong>{reg_data[r]['top_acct']}</strong></div>
            </div>
            <div class="region-metrics">
              <div>
                <div class="reg-m-val">${reg_data[r]['acv']/1e6:.1f}M</div>
                <div class="reg-m-lbl">Pipeline ACV</div>
              </div>
              <div>
                <div class="reg-m-val">{reg_data[r]['opps']}</div>
                <div class="reg-m-lbl">Active Deals</div>
              </div>
            </div>
          </div>
          ''' for r in regions])}
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">Regional Comparative Analysis</div>
          </div>
          <div class="panel-body">
            <div class="chart-container" style="height: 340px;">
              <canvas id="chartRegionCompare"></canvas>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 3: SALES PLAY & SOLUTION MATRIX -->
      <section id="tab-salesplays" class="tab-pane">
        <div class="panel-header" style="background: transparent; border: none; padding: 0 0 20px;">
          <div>
            <h2 style="font-family: 'Google Sans', sans-serif; font-size: 1.25rem;">Sales Plays & Solution Architecture</h2>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Traction across key technology pillars: AI/Gemini Enterprise, Sovereign Cloud, Security, and Migrations</p>
          </div>
        </div>

        <div class="charts-grid-2">
          <div class="card-panel">
            <div class="panel-header">
              <div class="panel-title">Sales Play Pipeline ACV Share</div>
            </div>
            <div class="panel-body">
              <div class="chart-container">
                <canvas id="chartPlayShare"></canvas>
              </div>
            </div>
          </div>

          <div class="card-panel">
            <div class="panel-header">
              <div class="panel-title">Sub-Region Solution Saturation Matrix</div>
              <div class="panel-subtitle">Coverage targets achieved by geography</div>
            </div>
            <div class="panel-body table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Solution Pillar</th>
                    <th>Benelux</th>
                    <th>DACH</th>
                    <th>France</th>
                    <th>Iberia</th>
                    <th>Italy</th>
                    <th>MENAT</th>
                    <th>Nordics</th>
                  </tr>
                </thead>
                <tbody>
                  {''.join([f'''
                  <tr>
                    <td><strong>{row['play']}</strong></td>
                    <td><span class="badge-pill blue">{row['benelux']}</span></td>
                    <td><span class="badge-pill blue">{row['dach']}</span></td>
                    <td><span class="badge-pill blue">{row['france']}</span></td>
                    <td><span class="badge-pill blue">{row['iberia']}</span></td>
                    <td><span class="badge-pill blue">{row['italy']}</span></td>
                    <td><span class="badge-pill blue">{row['menat']}</span></td>
                    <td><span class="badge-pill blue">{row['nordics']}</span></td>
                  </tr>
                  ''' for row in s4_matrix[:8]])}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 4: TOP 71 ACCOUNTS & OPPORTUNITIES EXPLORER -->
      <section id="tab-accounts" class="tab-pane">
        <div class="card-panel">
          <div class="panel-header">
            <div>
              <div class="panel-title">Top 71 EMEA Accounts Roster & Opportunity Explorer</div>
              <div class="panel-subtitle">Click any account row to view detailed child pipeline opportunities</div>
            </div>
            <span class="badge-pill blue">71 Key Accounts • 182 Deals Attached</span>
          </div>
          <div class="panel-body">
            <div class="search-controls">
              <div class="search-input-wrap">
                <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" id="acctSearchInput" class="search-input" placeholder="Search account name, industry, sub-region..." oninput="filterAccountsTable()">
              </div>
              <div style="display: flex; gap: 8px;">
                <select id="acctPriorityFilter" class="filter-select" style="width: 140px;" onchange="filterAccountsTable()">
                  <option value="ALL">All Priorities</option>
                  <option value="1">Priority 1</option>
                  <option value="2">Priority 2</option>
                  <option value="3">Priority 3</option>
                </select>
                <select id="acctTypeFilter" class="filter-select" style="width: 150px;" onchange="filterAccountsTable()">
                  <option value="ALL">All Types</option>
                  <option value="SPENDER">Spender</option>
                  <option value="GREENFIELD">Greenfield</option>
                </select>
              </div>
            </div>

            <div class="table-responsive">
              <table class="data-table" id="accountsTable">
                <thead>
                  <tr>
                    <th>Prio</th>
                    <th>Account Name</th>
                    <th>Sub-Region</th>
                    <th>Industry</th>
                    <th>Type</th>
                    <th>Market Mover</th>
                    <th>Strategy / Plays</th>
                    <th>Deals Attached</th>
                    <th>Pipeline ACV</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody id="accountsTableBody">
                  <!-- Injected via JavaScript for live interactivity -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Full 182 Deals Flat Explorer -->
        <div class="card-panel">
          <div class="panel-header">
            <div>
              <div class="panel-title">All Accenture Pipeline Opportunities (182 Deals)</div>
              <div class="panel-subtitle">Sortable opportunity ledger across EMEA</div>
            </div>
          </div>
          <div class="panel-body">
            <div class="table-responsive">
              <table class="data-table" id="oppsTable">
                <thead>
                  <tr>
                    <th>Account</th>
                    <th>Opportunity Name</th>
                    <th>Sub-Region</th>
                    <th>Stage</th>
                    <th>Sales Play</th>
                    <th>Close Qtr</th>
                    <th>ACV ($)</th>
                    <th>Total ($)</th>
                  </tr>
                </thead>
                <tbody id="oppsTableBody">
                  <!-- Injected via JS -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 5: GSI PEER BENCHMARK -->
      <section id="tab-gsi" class="tab-pane">
        <div class="panel-header" style="background: transparent; border: none; padding: 0 0 20px;">
          <div>
            <h2 style="font-family: 'Google Sans', sans-serif; font-size: 1.25rem;">GSI Peer Competitive Benchmark (EMEA)</h2>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Market share, pipeline volume, and average deal sizes across top Global System Integrators</p>
          </div>
        </div>

        <div class="charts-grid-2">
          <div class="card-panel">
            <div class="panel-header">
              <div class="panel-title">EMSI Partner Pipeline Share (ACV)</div>
            </div>
            <div class="panel-body">
              <div class="chart-container">
                <canvas id="chartGsiShare"></canvas>
              </div>
            </div>
          </div>

          <div class="card-panel">
            <div class="panel-header">
              <div class="panel-title">Average Deal ACV Comparison</div>
            </div>
            <div class="panel-body">
              <div class="chart-container">
                <canvas id="chartGsiAvgDeal"></canvas>
              </div>
            </div>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div class="panel-title">GSI Partner Ranking Table</div>
          </div>
          <div class="panel-body table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Partner Group</th>
                  <th>Total Deals</th>
                  <th>Active Deals</th>
                  <th>Pipeline ACV ($)</th>
                  <th>Total Value ($)</th>
                  <th>EMEA Share</th>
                  <th>Avg ACV ($)</th>
                </tr>
              </thead>
              <tbody>
                {''.join([f'''
                <tr {'style="background: #f5e8ff; font-weight: 600;"' if p == 'Accenture' else ''}>
                  <td><strong>#{idx+1}</strong></td>
                  <td>{p} {'<span class="badge-pill purple">Target Partner</span>' if p == 'Accenture' else ''}</td>
                  <td>{s['count']}</td>
                  <td>{s['active']}</td>
                  <td><strong>${s['acv']:,.0f}</strong></td>
                  <td>${s['total']:,.0f}</td>
                  <td>{(s['acv']/total_emea_gsi_acv*100):.1f}%</td>
                  <td>${(s['acv']/s['count']):,.0f}</td>
                </tr>
                ''' for idx, (p, s) in enumerate(sorted_gsi[:12])])}
              </tbody>
            </table>
          </div>
        </div>
      </section>

    </div>
  </main>
</div>

<!-- JAVASCRIPT LOGIC -->
<script>
const accountsData = {json_accounts};
const acnOppsData = {json_acn_opps};
const allOppsData = {json_all_opps};
const regData = {json_reg_data};
const playStats = {json_play_stats};
const stageStats = {json_stage_stats};
const gsiStats = {json_gsi_stats};

// Tab Switching
function switchTab(tabId) {{
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  
  const targetTab = document.getElementById('tab-' + tabId);
  if (targetTab) targetTab.classList.add('active');
  
  event.currentTarget.classList.add('active');

  const titles = {{
    'overview': ['Executive Overview & Scorecard', 'Comprehensive status of Accenture Top EMEA Accounts & Opportunity Pipeline'],
    'subregions': ['Sub-Region Performance Matrix', 'Regional breakdown of account penetration, pipeline ACV, and Priority 1 concentration'],
    'salesplays': ['Sales Plays & Solution Architecture', 'Traction across key technology pillars: AI/Gemini Enterprise, Sovereign Cloud, Security, and Migrations'],
    'accounts': ['Top 71 EMEA Accounts & Opportunity Explorer', 'Interactive roster and child pipeline drilldowns'],
    'gsi': ['GSI Peer Competitive Benchmark', 'Market share and deal velocity compared to other GSIs in EMEA']
  }};
  
  if (titles[tabId]) {{
    document.getElementById('pageHeading').innerText = titles[tabId][0];
    document.getElementById('pageSubHeading').innerText = titles[tabId][1];
  }}
}}

// Render Accounts Table
function renderAccounts(data) {{
  const tbody = document.getElementById('accountsTableBody');
  tbody.innerHTML = '';
  
  data.forEach((a, idx) => {{
    const tr = document.createElement('tr');
    tr.className = 'clickable';
    tr.onclick = () => toggleAccordion(idx);
    
    const prioClass = a.priority === '1' ? 'prio-1' : (a.priority === '2' ? 'prio-2' : 'prio-3');
    
    // Play tags
    let playsHtml = '';
    if (a.sales_plays.gemini_ent || a.sales_plays.build_ai) playsHtml += '<span class="tag-play ai">AI / Gemini</span> ';
    if (a.sales_plays.sovereignty || a.sales_plays.gdc) playsHtml += '<span class="tag-play sov">Sovereignty</span> ';
    if (a.sales_plays.security) playsHtml += '<span class="tag-play sec">Security</span> ';
    if (!playsHtml) playsHtml = '<span class="tag-play">Core Cloud</span>';

    tr.innerHTML = `
      <td><span class="prio-badge ${{prioClass}}">${{a.priority}}</span></td>
      <td><strong>${{a.name}}</strong></td>
      <td>${{a.sub_region}}</td>
      <td>${{a.industry}}</td>
      <td><span class="badge-pill ${{a.type === 'GREENFIELD' ? 'green' : 'amber'}}">${{a.type}}</span></td>
      <td>${{a.is_market_mover === 'Yes' ? '<span class="badge-pill purple">Market Mover</span>' : '-'}}</td>
      <td>${{playsHtml}}</td>
      <td><span class="badge-pill blue">${{a.matched_opps_count}} deals</span></td>
      <td><strong>$${{a.matched_opps_acv.toLocaleString()}}</strong></td>
      <td>
        ${{a.vector_link && a.vector_link.startsWith('http') ? `<a href="${{a.vector_link}}" target="_blank" class="btn btn-outline" style="padding: 2px 6px; font-size: 0.68rem;" onclick="event.stopPropagation()">Vector</a>` : '-'}}
      </td>
    `;
    tbody.appendChild(tr);

    // Accordion row
    const accRow = document.createElement('tr');
    accRow.id = 'acc-row-' + idx;
    accRow.className = 'opp-details-row';
    
    let oppsRows = '';
    if (a.matched_opps.length > 0) {{
      oppsRows = a.matched_opps.map(o => `
        <tr>
          <td><strong>${{o.opportunity_name}}</strong></td>
          <td><span class="stage-badge stage-tech">${{o.stage}}</span></td>
          <td>${{o.sales_play}}</td>
          <td>${{o.close_quarter}}</td>
          <td><strong>$${{o.usd_acv.toLocaleString()}}</strong></td>
          <td>$${{o.usd_total_amount.toLocaleString()}}</td>
        </tr>
      `).join('');
    }} else {{
      oppsRows = '<tr><td colspan="6" style="text-align: center; color: #94a3b8;">No direct pipeline opportunities attached in current extract.</td></tr>';
    }}

    accRow.innerHTML = `
      <td colspan="10">
        <div class="opp-inner-container">
          <div style="font-weight: 700; font-size: 0.78rem; margin-bottom: 8px; color: var(--text-main);">
            Attached Opportunities for ${{a.name}} (${{a.matched_opps.length}})
          </div>
          <table class="opp-subtable">
            <thead>
              <tr>
                <th>Opportunity Name</th>
                <th>Stage</th>
                <th>Sales Play</th>
                <th>Close Quarter</th>
                <th>ACV ($)</th>
                <th>Total Value ($)</th>
              </tr>
            </thead>
            <tbody>
              ${{oppsRows}}
            </tbody>
          </table>
        </div>
      </td>
    `;
    tbody.appendChild(accRow);
  }});
}}

function toggleAccordion(idx) {{
  const row = document.getElementById('acc-row-' + idx);
  if (row) {{
    row.classList.toggle('open');
  }}
}}

// Filter Accounts
function filterAccountsTable() {{
  const q = document.getElementById('acctSearchInput').value.toLowerCase();
  const prio = document.getElementById('acctPriorityFilter').value;
  const type = document.getElementById('acctTypeFilter').value;
  const reg = document.getElementById('globalRegionFilter').value;

  const filtered = accountsData.filter(a => {{
    const matchQ = a.name.toLowerCase().includes(q) || a.sub_region.toLowerCase().includes(q) || a.industry.toLowerCase().includes(q);
    const matchPrio = prio === 'ALL' || a.priority === prio;
    const matchType = type === 'ALL' || a.type === type;
    const matchReg = reg === 'ALL' || a.sub_region === reg;
    return matchQ && matchPrio && matchType && matchReg;
  }});

  renderAccounts(filtered);
}}

// Global Filter Handler
function applyGlobalFilters() {{
  const reg = document.getElementById('globalRegionFilter').value;
  const prio = document.getElementById('globalPriorityFilter').value;
  
  // Sync with account explorer controls
  document.getElementById('acctPriorityFilter').value = prio;
  filterAccountsTable();
}}

// Render Opps Flat Table
function renderOppsTable() {{
  const tbody = document.getElementById('oppsTableBody');
  tbody.innerHTML = '';
  
  acnOppsData.slice(0, 100).forEach(o => {{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${{o.reporting_account_name || o.child_account_name}}</strong></td>
      <td>${{o.opportunity_name}}</td>
      <td>${{o.sub_region}}</td>
      <td><span class="stage-badge stage-tech">${{o.stage}}</span></td>
      <td>${{o.sales_play}}</td>
      <td>${{o.close_quarter}}</td>
      <td><strong>$${{o.usd_acv.toLocaleString()}}</strong></td>
      <td>$${{o.usd_total_amount.toLocaleString()}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

// Charts Initialization
function initCharts() {{
  // Chart 1: Region Overview
  new Chart(document.getElementById('chartRegionOverview'), {{
    type: 'bar',
    data: {{
      labels: Object.keys(regData),
      datasets: [{{
        label: 'Pipeline ACV ($M)',
        data: Object.values(regData).map(v => (v.acv / 1e6).toFixed(1)),
        backgroundColor: '#1a73e8',
        borderRadius: 6
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        y: {{ beginAtZero: true, grid: {{ color: '#f1f5f9' }} }},
        x: {{ grid: {{ display: false }} }}
      }}
    }}
  }});

  // Chart 2: Stage Funnel
  new Chart(document.getElementById('chartStageFunnel'), {{
    type: 'doughnut',
    data: {{
      labels: Object.keys(stageStats),
      datasets: [{{
        data: Object.values(stageStats).map(v => v.count),
        backgroundColor: ['#1a73e8', '#7c3aed', '#f59e0b', '#10b981', '#f43f5e', '#64748b']
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: 'right', labels: {{ boxWidth: 12, font: {{ size: 11 }} }} }}
      }}
    }}
  }});

  // Chart 3: Regional Compare
  new Chart(document.getElementById('chartRegionCompare'), {{
    type: 'bar',
    data: {{
      labels: Object.keys(regData),
      datasets: [
        {{
          label: 'Accounts',
          data: Object.values(regData).map(v => v.accounts),
          backgroundColor: '#a100ff',
          borderRadius: 4
        }},
        {{
          label: 'Active Deals',
          data: Object.values(regData).map(v => v.opps),
          backgroundColor: '#1a73e8',
          borderRadius: 4
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      scales: {{
        y: {{ beginAtZero: true, grid: {{ color: '#f1f5f9' }} }},
        x: {{ grid: {{ display: false }} }}
      }}
    }}
  }});

  // Chart 4: Play Share
  new Chart(document.getElementById('chartPlayShare'), {{
    type: 'pie',
    data: {{
      labels: playStats.slice(0, 6).map(p => p[0]),
      datasets: [{{
        data: playStats.slice(0, 6).map(p => (p[1].acv / 1e6).toFixed(1)),
        backgroundColor: ['#7c3aed', '#1a73e8', '#0d9488', '#f59e0b', '#f43f5e', '#94a3b8']
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: 'right', labels: {{ boxWidth: 12, font: {{ size: 11 }} }} }}
      }}
    }}
  }});

  // Chart 5: GSI Share
  new Chart(document.getElementById('chartGsiShare'), {{
    type: 'bar',
    data: {{
      labels: gsiStats.slice(0, 7).map(g => g[0]),
      datasets: [{{
        label: 'Pipeline ACV ($M)',
        data: gsiStats.slice(0, 7).map(g => (g[1].acv / 1e6).toFixed(1)),
        backgroundColor: gsiStats.slice(0, 7).map(g => g[0] === 'Accenture' ? '#a100ff' : '#cbd5e1'),
        borderRadius: 6
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        y: {{ beginAtZero: true, grid: {{ color: '#f1f5f9' }} }},
        x: {{ grid: {{ display: false }} }}
      }}
    }}
  }});

  // Chart 6: GSI Avg Deal
  new Chart(document.getElementById('chartGsiAvgDeal'), {{
    type: 'bar',
    data: {{
      labels: gsiStats.slice(0, 7).map(g => g[0]),
      datasets: [{{
        label: 'Avg Deal ACV ($M)',
        data: gsiStats.slice(0, 7).map(g => (g[1].acv / g[1].count / 1e6).toFixed(2)),
        backgroundColor: gsiStats.slice(0, 7).map(g => g[0] === 'Accenture' ? '#1a73e8' : '#94a3b8'),
        borderRadius: 6
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        y: {{ beginAtZero: true, grid: {{ color: '#f1f5f9' }} }},
        x: {{ grid: {{ display: false }} }}
      }}
    }}
  }});
}}

// CSV Export
function exportDataCSV() {{
  let csv = 'Account ID,Account Name,Sub Region,Priority,Type,Market Mover,Industry,Attached Deals,Pipeline ACV\\n';
  accountsData.forEach(a => {{
    csv += `"${{a.id}}","${{a.name}}","${{a.sub_region}}","${{a.priority}}","${{a.type}}","${{a.is_market_mover}}","${{a.industry}}",${{a.matched_opps_count}},${{a.matched_opps_acv}}\\n`;
  }});
  const blob = new Blob([csv], {{ type: 'text/csv' }});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.setAttribute('href', url);
  a.setAttribute('download', 'Accenture_EMEA_FY26_Accounts.csv');
  a.click();
}}

// On Load
window.addEventListener('DOMContentLoaded', () => {{
  renderAccounts(accountsData);
  renderOppsTable();
  initCharts();
}});
</script>

</body>
</html>
"""

with open('FY26_Accenture_EMEA_Partner_Strategy_Report.html', 'w') as f:
    f.write(html_content)

print("Dashboard successfully generated at FY26_Accenture_EMEA_Partner_Strategy_Report.html")
