import re
import os

content = open('dlc.yml').read()
cats = ['anthropic', 'openai', 'google', 'apple', 'microsoft', 'cloudflare', 'google-gemini']

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

    open('lists/' + cat + '.lst', 'w').write('\n'.join(domains))

    stash_lines = ['payload:']
    stash_lines += ['  - DOMAIN-SUFFIX,' + d for d in domains]
    open('Stash/' + cat + '.list', 'w').write('\n'.join(stash_lines))

    print('=== ' + cat + ': ' + str(len(domains)) + ' domains ===')
