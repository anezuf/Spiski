import re
import os
import json
import base64
import struct
import socket
import urllib.request

content = open('dlc.yml').read()
cats = ['category-porn', 'category-speedtest', 'anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram', 'instagram', 'youtube', 'supercell', 'ookla-speedtest', 'discord', 'pinterest', 'spotify', 'soundcloud']
os.makedirs('lists', exist_ok=True)
os.makedirs('Stash', exist_ok=True)
os.makedirs('geo-data', exist_ok=True)
os.makedirs('happ', exist_ok=True)

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

# --- geo-data/mylist для geosite.dat ---
happ_cats = ['anthropic', 'openai', 'google-gemini', 'tiktok', 'telegram',
             'instagram', 'youtube', 'supercell', 'ookla-speedtest',
             'discord', 'pinterest', 'spotify', 'soundcloud']

mylist_lines = []
for cat in happ_cats:
    for d in all_domains[cat]:
        mylist_lines.append('domain:' + d)

open('geo-data/mylist', 'w').write('\n'.join(mylist_lines))
print('=== geo-data/mylist: ' + str(len(mylist_lines)) + ' domains ===')

# --- geoip.dat через Python (protobuf вручную) ---
# Структура: GeoIPList -> GeoIP -> CIDR
# GeoIPList { repeated GeoIP entry = 1; }
# GeoIP { string country_code = 1; repeated CIDR cidr = 2; }
# CIDR { bytes ip = 1; uint32 prefix = 2; }

def encode_varint(value):
    bits = value & 0x7f
    value >>= 7
    result = b''
    while value:
        result += bytes([0x80 | bits])
        bits = value & 0x7f
        value >>= 7
    result += bytes([bits])
    return result

def encode_field(field_number, wire_type, data):
    tag = (field_number << 3) | wire_type
    return encode_varint(tag) + data

def encode_bytes(data):
    return encode_varint(len(data)) + data

def encode_string(s):
    return encode_bytes(s.encode('utf-8'))

def encode_cidr(ip_str, prefix):
    ip_bytes = socket.inet_aton(ip_str)
    cidr_msg = b''
    cidr_msg += encode_field(1, 2, encode_bytes(ip_bytes))   # ip
    cidr_msg += encode_field(2, 0, encode_varint(prefix))    # prefix
    return encode_bytes(cidr_msg)

def encode_geoip(country_code, cidrs):
    geoip_msg = b''
    geoip_msg += encode_field(1, 2, encode_string(country_code))  # country_code
    for ip_str, prefix in cidrs:
        geoip_msg += encode_field(2, 2, encode_cidr(ip_str, prefix))  # cidr
    return encode_bytes(geoip_msg)

# Парсим CIDR список Telegram
telegram_cidrs = []
for cidr in tg_ips:
    cidr = cidr.strip()
    if '/' in cidr:
        ip_part, prefix_part = cidr.split('/')
        telegram_cidrs.append((ip_part, int(prefix_part)))

# Собираем GeoIPList
geoip_list = b''
geoip_list += encode_field(1, 2, encode_geoip('TELEGRAM', telegram_cidrs))

open('geoip.dat', 'wb').write(geoip_list)
print('=== geoip.dat: ' + str(len(geoip_list)) + ' bytes ===')

REPO = "anezuf/Spiski"

happ_profile = {
    "Name": "My Rules",
    "GlobalProxy": "false",
    "RemoteDNSType": "DoH",
    "RemoteDNSDomain": "https://cloudflare-dns.com/dns-query",
    "RemoteDNSIP": "1.1.1.1",
    "DomesticDNSType": "DoH",
    "DomesticDNSDomain": "https://dns.google/dns-query",
    "DomesticDNSIP": "8.8.8.8",
    "Geoipurl": f"https://raw.githubusercontent.com/{REPO}/main/geoip.dat",
    "Geositeurl": f"https://raw.githubusercontent.com/{REPO}/main/geosite.dat",
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
    "ProxyIp": ["geoip:TELEGRAM"],
    "BlockSites": [],
    "BlockIp": [],
    "DomainStrategy": "IPIfNonMatch",
    "FakeDNS": "false"
}

profile_json = json.dumps(happ_profile, ensure_ascii=False, indent=2)
profile_b64 = base64.b64encode(profile_json.encode()).decode()
deeplink = "happ://routing/onadd/" + profile_b64

open('happ/geoip.dat', 'wb').write(geoip_list)
open('happ/happ-routing.json', 'w').write(profile_json)
open('happ/happ-routing-deeplink.txt', 'w').write(deeplink)

print('=== happ deeplink length: ' + str(len(deeplink)) + ' chars ===')
print('ВАЖНО: замени USERNAME/REPONAME в скрипте на реальный путь!')
