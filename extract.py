import re
import os
import json
import base64
import urllib.request

content = open('dlc.yml').read()
cats = ['category-porn', 'category-speedtest', 'anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram', 'instagram', 'youtube', 'supercell', 'ookla-speedtest', 'discord', 'pinterest', 'spotify', 'soundcloud']
os.makedirs('lists', exist_ok=True)
os.makedirs('Stash', exist_ok=True)
os.makedirs('geo-data', exist_ok=True)

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

# --- Telegram IPs ---
url = 'https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Subnets/IPv4/telegram.lst'
tg_ips = urllib.request.urlopen(url).read().decode().splitlines()
tg_ips = [ip for ip in tg_ips if ip.strip()]
stash_ip_lines = ['payload:']
for ip in tg_ips:
    stash_ip_lines.append('  - IP-CIDR,' + ip.strip())
open('Stash/telegram-ip.list', 'w').write('\n'.join(stash_ip_lines))
open('lists/telegram-ip.lst', 'w').write('\n'.join(ip.strip() for ip in tg_ips))
print('=== telegram-ip: ' + str(len(tg_ips)) + ' subnets ===')

# --- Генерация geo-data файлов для geosite.dat и geoip.dat ---

# Категории для geosite (все кроме category-porn и category-speedtest)
happ_cats = ['anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram',
             'instagram', 'youtube', 'supercell', 'ookla-speedtest',
             'discord', 'pinterest', 'spotify', 'soundcloud']

# Файл данных для domain-list-community генератора
# Формат: одна запись на строку, тип:значение
mylist_lines = []
for cat in happ_cats:
    for d in all_domains[cat]:
        mylist_lines.append('domain:' + d)

open('geo-data/mylist', 'w').write('\n'.join(mylist_lines))
print('=== geo-data/mylist: ' + str(len(mylist_lines)) + ' domains ===')

# Файл IP для geoip генератора (просто список CIDR)
open('geo-data/telegram-ips.txt', 'w').write('\n'.join(ip.strip() for ip in tg_ips))
print('=== geo-data/telegram-ips.txt: ' + str(len(tg_ips)) + ' IPs ===')

# Конфиг для v2fly/geoip
geoip_config = {
    "input": [
        {
            "type": "text",
            "action": "add",
            "args": {
                "name": "telegram",
                "uri": "geo-data/telegram-ips.txt"
            }
        }
    ],
    "output": [
        {
            "type": "v2rayGeoIPDat",
            "action": "output",
            "args": {
                "outputName": "geoip.dat",
                "outputDir": "./"
            }
        }
    ]
}
open('geo-data/geoip-config.json', 'w').write(json.dumps(geoip_config, indent=2))

# --- Маленький happ routing профиль ---
happ_profile = {
    "Name": "My Rules",
    "GlobalProxy": "false",
    "RemoteDNSType": "DoH",
    "RemoteDNSDomain": "https://cloudflare-dns.com/dns-query",
    "RemoteDNSIP": "1.1.1.1",
    "DomesticDNSType": "DoH",
    "DomesticDNSDomain": "https://dns.google/dns-query",
    "DomesticDNSIP": "8.8.8.8",
    "Geoipurl": "https://raw.githubusercontent.com/ТВОЙ_РЕПО/main/geoip.dat",
    "Geositeurl": "https://raw.githubusercontent.com/ТВОЙ_РЕПО/main/geosite.dat",
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
    "ProxySites": ["geosite:mylist"],
    "ProxyIp": ["geoip:telegram"],
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

print('=== happ deeplink length: ' + str(len(deeplink)) + ' chars ===')
print('ВАЖНО: замени ТВОЙ_РЕПО в happ-routing.json на реальный путь к репозиторию!')
