import re
import os

content = open('dlc.yml').read()
cats = ['anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram', 'instagram', 'youtube', 'supercell', 'ookla-speedtest', 'discord']

os.makedirs('lists', exist_ok=True)
os.makedirs('Stash', exist_ok=True)

for cat in cats:
    domains = []
    in_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == '- name: ' + cat:
            in_section = True
            continue
        if in_section:
            if stripped.startswith('- name:'):
                break
            m = re.search(r'"domain:([^"]+)"', stripped)
            if m:
                domains.append(m.group(1).strip())

    clean_domains = [d.split(':')[0] for d in domains]
    open('lists/' + cat + '.lst', 'w').write('\n'.join(clean_domains))

    stash_lines = ['payload:']
    for d in domains:
        clean = d.split(':')[0]  # убирает :@!cn и подобное
        stash_lines.append('  - DOMAIN-SUFFIX,' + clean)
    open('Stash/' + cat + '.list', 'w').write('\n'.join(stash_lines))

    print('=== ' + cat + ': ' + str(len(domains)) + ' domains ===')
