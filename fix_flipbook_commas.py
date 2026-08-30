import os
import re

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
    
    # Match any <Page ... /> that is not immediately followed by a comma
    new_children = re.sub(r'(<Page[^>]*?/>)(?!\s*,)', r'\1,', children)
    
    # We should also ensure that the image pages that missed the !isMobile && are hidden
    # wait, earlier I wrote `!isMobile && <Page ... />,` for most of them. 
    # But for Page 12, Page 14, Page 16, I forgot to add `!isMobile &&`!
    # Let's fix that too while we're here.
    
    def add_ismobile(match):
        page_tag = match.group(0)
        # If it doesn't already have !isMobile && before it, and it's an imagePage
        # wait, the regex only matched the tag itself, not what's before it.
        return page_tag
        
    new_children = re.sub(r'<Page[^>]*?imagePage={true}[^>]*?/>,?', lambda m: f"!isMobile && {m.group(0)}" if "!isMobile &&" not in children[max(0, children.find(m.group(0)) - 20):children.find(m.group(0))] else m.group(0), new_children)
    
    # But actually, re.sub goes through one by one. The lookbehind is safer.
    # I'll just use a simpler replacement. We know we want image pages to have `!isMobile &&`.
    # Let's just fix the commas first.
    
    new_children = re.sub(r'(<Page[^>]*?/>)(?!\s*,)', r'\1,', children)
    
    new_content = before + flipbook_open + new_children + after
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Fixed self-closing Page commas!")
