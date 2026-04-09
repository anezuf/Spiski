import re
content = open('dlc.yml').read()
cats = ['anthropic','openai','google','apple','microsoft','cloudflare']
for cat in cats:
    domains = []
    in_section = False
    for line in content.splitlines():
        if line == '- name: ' + cat:
            in_section = True
            continue
        if in_section:
            if line.startswith('- name:'):
                break
            m = re.search(r'"domain:([^"]+)"', line)
            if m:
                domains.append(m.group(1).strip())
    open('lists/' + cat + '.lst', 'w').write('\n'.join(domains))
    print('=== ' + cat + ': ' + str(len(domains)) + ' domains ===')
