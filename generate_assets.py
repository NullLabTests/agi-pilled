import json, colorsys, math, re, os

data = json.load(open('agi_predictions.json'))
entries = data['entries']

def hsl(seed):
    hue = (seed * 0.618033988749895) % 1.0
    sat = 0.72 + (seed % 5) * 0.04
    lit = 0.50 + (seed % 3) * 0.06
    r, g, b = colorsys.hls_to_rgb(hue, lit, sat)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))

for i, e in enumerate(entries):
    e['color'] = hsl(i)

def get_badge(yr):
    if yr >= 2026 and yr <= 2027: return 'IMMINENT', '#00E676'
    if yr <= 2030: return 'NOW', '#FFD740'
    if yr <= 2035: return 'NEAR', '#FF9100'
    if yr <= 2050: return 'MID', '#FF5252'
    if yr <= 2070: return 'LONG', '#E040FB'
    return 'FAR', '#448AFF'

# ===============================================================
#  SVG TIMELINE
# ===============================================================
W, H = 1200, 700
MARGIN = 80

modern = [e for e in entries if e['year'] >= 2020]
historical = [e for e in entries if e['year'] < 2020]
modern.sort(key=lambda e: e['year'])
historical.sort(key=lambda e: e['year'])

YR_MIN, YR_MAX = 1998, 2090
BAR_Y = 330
BAR_H = 12

def xpos(yr):
    return MARGIN + (yr - YR_MIN) / (YR_MAX - YR_MIN) * (W - 2 * MARGIN)

svg = []
svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0B0E1A"/>
      <stop offset="35%" stop-color="#0F1530"/>
      <stop offset="100%" stop-color="#0B0E1A"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#1A237E"/>
      <stop offset="50%" stop-color="#4A6CF7"/>
      <stop offset="100%" stop-color="#1A237E"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <pattern id="dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
    <circle cx="20" cy="20" r="0.8" fill="#FFFFFF" opacity="0.03"/>
  </pattern>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
''')

svg.append(f'''
  <text x="{W/2}" y="48" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-size="28" font-weight="700" fill="#FFFFFF" letter-spacing="3" opacity="0.95">AGI PREDICTIONS TIMELINE</text>
  <text x="{W/2}" y="74" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="#8892B0" letter-spacing="1">33 minds · 33 predictions · one question that defines our era</text>
  <text x="{W/2}" y="95" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="#4A6CF7" opacity="0.6">sourced from public interviews, X, podcasts, essays · as of mid-2026</text>
''')

# Decade markers
for yr in range(2000, 2091, 10):
    x = xpos(yr)
    if x < MARGIN or x > W - MARGIN: continue
    alpha = '0.4' if yr % 50 == 0 else '0.2'
    svg.append(f'<line x1="{x}" y1="{BAR_Y-15}" x2="{x}" y2="{BAR_Y+BAR_H+15}" stroke="#FFFFFF" stroke-opacity="{alpha}" stroke-width="1"/>')
    sz = '12' if yr % 50 == 0 else '10'
    svg.append(f'<text x="{x}" y="{BAR_Y+40}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="{sz}" fill="#8892B0" opacity="0.45">{yr}</text>')

# Bar
svg.append(f'<rect x="{MARGIN}" y="{BAR_Y}" width="{W-2*MARGIN}" height="{BAR_H}" rx="6" fill="url(#bar)" opacity="0.25"/>')
svg.append(f'<line x1="{MARGIN}" y1="{BAR_Y+BAR_H/2}" x2="{W-MARGIN}" y2="{BAR_Y+BAR_H/2}" stroke="#4A6CF7" stroke-width="2" opacity="0.4"/>')

# NOW marker
x_now = xpos(2026)
svg.append(f'<line x1="{x_now}" y1="{BAR_Y-20}" x2="{x_now}" y2="{BAR_Y+BAR_H+20}" stroke="#FFD700" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.7"/>')
svg.append(f'<text x="{x_now}" y="{BAR_Y-28}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="#FFD700" letter-spacing="1" opacity="0.9">NOW</text>')

# Place dots — alternate above/below per person
above = []
below = []
for idx, e in enumerate(modern):
    if idx % 2 == 0: above.append(e)
    else: below.append(e)

for group, is_above in [(above, True), (below, False)]:
    for row_idx, e in enumerate(group):
        x = xpos(e['year'])
        color = e['color']
        name = e['name']
        yr = e['year']

        if is_above:
            ly = BAR_Y - 25 - (row_idx % 5) * 44
        else:
            ly = BAR_Y + BAR_H + 30 + (row_idx % 5) * 44

        # Connection line
        svg.append(f'<line x1="{x}" y1="{BAR_Y+BAR_H/2}" x2="{x}" y2="{ly+12}" stroke="{color}" stroke-width="1" opacity="0.12"/>')
        # Dot
        svg.append(f'<circle cx="{x}" cy="{BAR_Y+BAR_H/2}" r="5" fill="{color}" filter="url(#glow)" opacity="0.95"/>')
        svg.append(f'<circle cx="{x}" cy="{BAR_Y+BAR_H/2}" r="2.5" fill="#FFFFFF" opacity="0.85"/>')
        # Name
        font_sz = 13 if len(name) < 14 else 11
        svg.append(f'<text x="{x}" y="{ly}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="{font_sz}" font-weight="600" fill="{color}" opacity="0.95">{name}</text>')
        svg.append(f'<text x="{x}" y="{ly+15}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" fill="#8892B0" opacity="0.6">~{int(yr)}</text>')

# Historical entries
hist_y = BAR_Y + 100
for e in historical:
    x = xpos(e['year'])
    if x < MARGIN or x > W - MARGIN: continue
    color = e['color']
    name = e['name']
    svg.append(f'<circle cx="{x}" cy="{hist_y}" r="3.5" fill="{color}" filter="url(#glow)" opacity="0.5"/>')
    svg.append(f'<text x="{x}" y="{hist_y+16}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="{color}" opacity="0.5">{name}</text>')
    svg.append(f'<text x="{x}" y="{hist_y-10}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="8" fill="#8892B0" opacity="0.3">historical</text>')

svg.append(f'''
  <text x="{W/2}" y="{H-20}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="#4A6CF7" opacity="0.3">hover or tap any entry below for full details · each person color-coded · mid-2026</text>
</svg>''')

os.makedirs('assets', exist_ok=True)
with open('assets/agi_timeline.svg', 'w') as f:
    f.write('\n'.join(svg))
print("✓ SVG: assets/agi_timeline.svg")

# ===============================================================
#  CARDS HTML
# ===============================================================
ordered = sorted(modern, key=lambda e: e['year']) + historical

cards = []
for e in ordered:
    color = e['color']
    name = e['name']
    role = e['role']
    prediction = e['prediction']
    viewpoint = e['viewpoint']
    links = e['links']
    yr = e['year']

    badge_text, badge_color = get_badge(yr)

    link_html = ''
    if links.get('website'):
        link_html += f'<a href="{links["website"]}" style="display:inline-block;padding:4px 10px;margin:2px;border-radius:4px;font-size:11px;font-weight:500;text-decoration:none;background:{color}22;color:{color};border:1px solid {color}44;">🌐 Site</a>'
    if links.get('twitter'):
        link_html += f'<a href="{links["twitter"]}" style="display:inline-block;padding:4px 10px;margin:2px;border-radius:4px;font-size:11px;font-weight:500;text-decoration:none;background:{color}22;color:{color};border:1px solid {color}44;">𝕏 X</a>'
    if links.get('arxiv'):
        link_html += f'<a href="{links["arxiv"]}" style="display:inline-block;padding:4px 10px;margin:2px;border-radius:4px;font-size:11px;font-weight:500;text-decoration:none;background:{color}22;color:{color};border:1px solid {color}44;">📄 arXiv</a>'
    if links.get('github'):
        link_html += f'<a href="{links["github"]}" style="display:inline-block;padding:4px 10px;margin:2px;border-radius:4px;font-size:11px;font-weight:500;text-decoration:none;background:{color}22;color:{color};border:1px solid {color}44;">💻 GitHub</a>'
    if links.get('books'):
        link_html += f'<span style="display:inline-block;padding:4px 10px;margin:2px;border-radius:4px;font-size:11px;font-weight:500;background:{color}22;color:{color};border:1px solid {color}44;">📚 {links["books"]}</span>'

    preview = viewpoint[:220] + ('...' if len(viewpoint) > 220 else '')

    cards.append(f'''
<tr style="border-bottom:1px solid #1E2240;">
  <td style="width:5px;background:{color};padding:0;border-radius:6px 0 0 6px;"></td>
  <td style="padding:20px 24px;vertical-align:top;">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;flex-wrap:wrap;">
      <span style="font-size:20px;font-weight:700;color:#E6F1FF;">{name}</span>
      <span style="display:inline-block;padding:2px 12px;border-radius:12px;font-size:10px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;background:{badge_color}22;color:{badge_color};">{badge_text}</span>
    </div>
    <div style="font-size:13px;color:#8892B0;margin-bottom:12px;line-height:1.5;font-weight:400;">{role}</div>
    <div style="font-size:14px;font-weight:600;color:{color};margin-bottom:8px;">▸ {prediction}</div>
    <div style="font-size:13px;color:#A8B2D1;line-height:1.7;margin-bottom:14px;max-width:800px;">{preview}</div>
    <div style="display:flex;flex-wrap:wrap;gap:4px;">{link_html}</div>
  </td>
</tr>''')

full = f'''<div style="overflow-x:auto;margin:30px 0;">
<table style="width:100%;border-collapse:separate;border-spacing:0 10px;background:transparent;">
{''.join(cards)}
</table>
</div>'''

with open('assets/cards.html', 'w') as f:
    f.write(full)
print(f"✓ Cards: assets/cards.html ({len(ordered)} people)")
