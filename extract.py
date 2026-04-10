import re
import os
import json
import base64
import urllib.request

content = open('dlc.yml').read()
cats = ['category-porn', 'category-speedtest', 'anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram', 'instagram', 'youtube', 'supercell', 'ookla-speedtest', 'discord', 'pinterest', 'spotify', 'soundcloud']
os.makedirs('lists', exist_ok=True)
os.makedirs('Stash', exist_ok=True)

all_domains = {}

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
    all_domains[cat] = clean_domains
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
open('lists/telegram-ip.lst', 'w').write('\n'.join(ip.strip() for ip in tg_ips))
print('=== telegram-ip: ' + str(len(tg_ips)) + ' subnets ===')

# --- Генерация happ routing профиля ---
# Все категории КРОМЕ category-porn и category-speedtest
happ_cats = ['anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram',
             'instagram', 'youtube', 'supercell', 'ookla-speedtest',
             'discord', 'pinterest', 'spotify', 'soundcloud']

happ_domains = []
for cat in happ_cats:
    happ_domains.extend(all_domains[cat])

happ_profile = {
    "Name": "My Rules",
    "GlobalProxy": "false",
    "RemoteDNSType": "DoH",
    "RemoteDNSDomain": "https://cloudflare-dns.com/dns-query",
    "RemoteDNSIP": "1.1.1.1",
    "DomesticDNSType": "DoH",
    "DomesticDNSDomain": "https://dns.google/dns-query",
    "DomesticDNSIP": "8.8.8.8",
    "DnsHosts": {},
    "DirectSites": [],
    "DirectIp": [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
        "224.0.0.0/4",
        "255.255.255.255"
    ],
    "ProxySites": ["domain:" + d for d in happ_domains],
    "ProxyIp": [ip.strip() for ip in tg_ips],
    "BlockSites": [],
    "BlockIp": [],
    "DomainStrategy": "IPIfNonMatch",
    "FakeDNS": "false"
}

profile_json = json.dumps(happ_profile, ensure_ascii=False, indent=2)
profile_b64 = base64.b64encode(profile_json.encode()).decode()
deeplink = "happ://routing/onadd/" + profile_b64

open('happ-routing.json', 'w').write(profile_json)
open('happ-routing-deeplink.txt', 'w').write(deeplink)
open('happ-subscription.txt', 'w').write(deeplink + "\n")

print('=== happ: ' + str(len(happ_domains)) + ' domains, ' + str(len(tg_ips)) + ' IPs ===')
