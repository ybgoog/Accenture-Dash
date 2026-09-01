import json
import os

with open('extracted_data.json') as f:
    data = json.load(f)

accounts = data['accounts']
opps = data['opportunities']
s4_matrix = data['sales_play_matrix']

# Accenture specific opps
acn_opps = [o for o in opps if o['partner'] == 'Accenture']

# Stats calculation
total_acv = sum(o['usd_acv'] for o in acn_opps)
total_amount = sum(o['usd_total_amount'] for o in acn_opps)
won_opps = [o for o in acn_opps if 'won' in o['stage'].lower()]
lost_opps = [o for o in acn_opps if 'lost' in o['stage'].lower()]
active_opps = [o for o in acn_opps if 'won' not in o['stage'].lower() and 'lost' not in o['stage'].lower()]

won_acv = sum(o['usd_acv'] for o in won_opps)
active_acv = sum(o['usd_acv'] for o in active_opps)
win_rate = (len(won_opps) / (len(won_opps) + len(lost_opps)) * 100) if (len(won_opps) + len(lost_opps)) > 0 else 0

# Regional breakdown for Accenture
regions = sorted(list(set(o['sub_region'] for o in acn_opps if o['sub_region'])))
region_stats = {}
for r in regions:
    r_opps = [o for o in acn_opps if o['sub_region'] == r]
    r_accts = [a for a in accounts if a['sub_region'] == r]
    region_stats[r] = {
        'opp_count': len(r_opps),
        'acct_count': len(r_accts),
        'total_acv': sum(o['usd_acv'] for o in r_opps),
        'total_amount': sum(o['usd_total_amount'] for o in r_opps),
        'won_acv': sum(o['usd_acv'] for o in r_opps if 'won' in o['stage'].lower()),
        'active_acv': sum(o['usd_acv'] for o in r_opps if 'won' not in o['stage'].lower() and 'lost' not in o['stage'].lower()),
    }

# Stage breakdown
stages = {}
for o in acn_opps:
    st = o['stage'] or 'Unknown'
    if st not in stages:
        stages[st] = {'count': 0, 'acv': 0, 'total': 0}
    stages[st]['count'] += 1
    stages[st]['acv'] += o['usd_acv']
    stages[st]['total'] += o['usd_total_amount']

# Sales play breakdown
sales_plays = {}
for o in acn_opps:
    sp = o['sales_play'] or 'General Cloud'
    if sp not in sales_plays:
        sales_plays[sp] = {'count': 0, 'acv': 0, 'total': 0}
    sales_plays[sp]['count'] += 1
    sales_plays[sp]['acv'] += o['usd_acv']
    sales_plays[sp]['total'] += o['usd_total_amount']

# GSI Peer comparison
gsi_stats = {}
for o in opps:
    p = o['partner'] or 'Other'
    if p not in gsi_stats:
        gsi_stats[p] = {'count': 0, 'acv': 0, 'total': 0, 'won_count': 0, 'won_acv': 0, 'lost_count': 0}
    gsi_stats[p]['count'] += 1
    gsi_stats[p]['acv'] += o['usd_acv']
    gsi_stats[p]['total'] += o['usd_total_amount']
    if 'won' in o['stage'].lower():
        gsi_stats[p]['won_count'] += 1
        gsi_stats[p]['won_acv'] += o['usd_acv']
    elif 'lost' in o['stage'].lower():
        gsi_stats[p]['lost_count'] += 1

for p in gsi_stats:
    dec = gsi_stats[p]['won_count'] + gsi_stats[p]['lost_count']
    gsi_stats[p]['win_rate'] = (gsi_stats[p]['won_count'] / dec * 100) if dec > 0 else 0
    gsi_stats[p]['avg_acv'] = gsi_stats[p]['acv'] / gsi_stats[p]['count'] if gsi_stats[p]['count'] > 0 else 0

print("Accenture Summary:")
print(f"Total Opps: {len(acn_opps)}, ACV: ${total_acv:,.0f}, Won Opps: {len(won_opps)} (${won_acv:,.0f}), Win Rate: {win_rate:.1f}%")
print(f"Active Opps: {len(active_opps)}, Active ACV: ${active_acv:,.0f}")
print("\nTop 5 GSI Partners by Pipeline ACV:")
sorted_gsi = sorted(gsi_stats.items(), key=lambda x: x[1]['acv'], reverse=True)
for p, s in sorted_gsi[:8]:
    print(f"{p}: {s['count']} opps, ACV: ${s['acv']:,.0f}, Win Rate: {s['win_rate']:.1f}%, Avg ACV: ${s['avg_acv']:,.0f}")
