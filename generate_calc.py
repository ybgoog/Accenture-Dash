import json
import os

with open('full_data_payload.json') as f:
    data = json.load(f)

accounts = data['accounts']
opps = data['opportunities']
s4_matrix = data['sales_play_matrix']

# Filter Accenture opps
acn_opps = [o for o in opps if o['partner'] == 'Accenture']

# Generate HTML
html_builder_script = """
import json
import re

with open('full_data_payload.json') as f:
    data = json.load(f)

accounts = data['accounts']
opps = data['opportunities']
s4_matrix = data['sales_play_matrix']

acn_opps = [o for o in opps if o['partner'] == 'Accenture']

# Compute summary stats
total_acv = sum(o['usd_acv'] for o in acn_opps)
total_amount = sum(o['usd_total_amount'] for o in acn_opps)
active_opps = [o for o in acn_opps if 'lost' not in o['stage'].lower()]
active_acv = sum(o['usd_acv'] for o in active_opps)

# Count priority
p1_count = len([a for a in accounts if a['priority'] == '1'])
p2_count = len([a for a in accounts if a['priority'] == '2'])
p3_count = len([a for a in accounts if a['priority'] == '3'])
focus_count = len([a for a in accounts if a['is_emea_focus']])
market_mover_count = len([a for a in accounts if a['is_market_mover'] == 'Yes'])
greenfield_count = len([a for a in accounts if a['type'] == 'GREENFIELD'])
spender_count = len([a for a in accounts if a['type'] == 'SPENDER'])

# GSI Benchmark stats
gsi_stats = {}
for o in opps:
    p = o['partner'] or 'Other'
    if p not in gsi_stats:
        gsi_stats[p] = {'count': 0, 'acv': 0, 'total': 0}
    gsi_stats[p]['count'] += 1
    gsi_stats[p]['acv'] += o['usd_acv']
    gsi_stats[p]['total'] += o['usd_total_amount']

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
        'total': sum(o['usd_total_amount'] for o in r_opps)
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

# Stages in Accenture
stage_stats = {}
for o in acn_opps:
    st = o['stage'] or '01 - Refine'
    if st not in stage_stats:
        stage_stats[st] = {'count': 0, 'acv': 0, 'total': 0}
    stage_stats[st]['count'] += 1
    stage_stats[st]['acv'] += o['usd_acv']
    stage_stats[st]['total'] += o['usd_total_amount']

# Marquee Opps (sorted by total amount or acv)
marquee_opps = sorted(acn_opps, key=lambda x: (x['usd_total_amount'], x['usd_acv']), reverse=True)[:10]

print("Ready to construct HTML.")
"""

with open('test_calc.py', 'w') as f:
    f.write(html_builder_script)

