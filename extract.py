import re
import os
import urllib.request

content = open('dlc.yml').read()
cats = ['category-porn', 'category-speedtest', 'anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram', 'instagram', 'youtube', 'supercell', 'ookla-speedtest', 'discord', 'pinterest', 'spotify', 'soundcloud']

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
    for d in clean_domains:
        stash_lines.append('  - DOMAIN-SUFFIX,' + d)
    open('Stash/' + cat + '.list', 'w').write('\n'.join(stash_lines))

    print('=== ' + cat + ': ' + str(len(clean_domains)) + ' domains ===')

url = 'https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Subnets/IPv4/telegram.lst'
tg_ips = urllib.request.urlopen(url).read().decode().splitlines()
tg_ips = [ip for ip in tg_ips if ip.strip()]

stash_ip_lines = ['payload:']
for ip in tg_ips:
    stash_ip_lines.append('  - IP-CIDR,' + ip.strip())
open('Stash/telegram-ip.list', 'w').write('\n'.join(stash_ip_lines))

lists_ip_lines = []
for ip in tg_ips:
    lists_ip_lines.append(ip.strip())
open('lists/telegram-ip.lst', 'w').write('\n'.join(lists_ip_lines))

print('=== telegram-ip: ' + str(len(tg_ips)) + ' subnets ===')
