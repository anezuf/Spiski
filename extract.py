import re

content = open('dlc.yml').read()

# Покажем контекст вокруг anthropic
lines = content.splitlines()
for i, line in enumerate(lines):
    if 'anthropic' in line.lower():
        print(f'LINE {i}: {repr(line)}')
        for j in range(i, min(i+10, len(lines))):
            print(f'  {j}: {repr(lines[j])}')
        break
