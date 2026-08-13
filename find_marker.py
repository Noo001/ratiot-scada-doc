import sys
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    text = f.read()
marker = sys.argv[2]
idx = text.lower().find(marker.lower())
if idx == -1:
    print(f'"{marker}" not found')
    sys.exit(1)
print(f'Found at position {idx}, total length {len(text)}')
print(text[idx:idx+1000])
