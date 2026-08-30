import os

for file_path in ['frontend/src/pages/Home.jsx', 'frontend/src/pages/HomeFeed.jsx']:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parts = content.split('<HTMLFlipBook')
    if len(parts) < 2:
        continue
        
    before = parts[0]
    rest = '<HTMLFlipBook' + parts[1]
    
    idx = rest.find('>')
    if idx == -1: continue
    
    flipbook_open = rest[:idx+1]
    inside = rest[idx+1:]
    
    end_idx = inside.rfind('</HTMLFlipBook>')
    if end_idx == -1: continue
    
    children = inside[:end_idx]
    after = inside[end_idx:]
    
    # We want to add a comma after every top-level child in `children`.
    # A simple hack: replace </Page> with </Page>, 
    # and replace />} (which closes {!isMobile && <Page />}) with />},
    
    # First, let's replace </Page> with </Page>,
    new_children = children.replace('</Page>', '</Page>,')
    
    # Second, for the image pages, we have: {!isMobile && <Page ... />}
    # We replace />} with />},
    new_children = new_children.replace('/>}', '/>},')
    
    wrapped = f"\n          {{[\n{new_children}\n          ].filter(Boolean)}}\n        "
    
    new_content = before + flipbook_open + wrapped + after
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Fixed flipbooks!")
