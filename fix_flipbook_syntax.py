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
    
    # We need to remove { and } around comments in the array
    # because {/* Comment */} is invalid inside a JavaScript array.
    
    new_children = children.replace('{/*', '/*').replace('*/}', '*/')
    
    # But wait, wait! 
    # What about `{!isMobile && ...}`? The `{` and `}` are around the conditional.
    # In an array, we can't have `{!isMobile && ...}`. It should just be `!isMobile && ...`!
    # Wait, `{!isMobile && ...}` is invalid in an array. It must be `!isMobile ? ... : null` or just `!isMobile && ...` without braces!
    # Let's replace `{ !isMobile` and `{!isMobile` with `!isMobile`
    new_children = new_children.replace('{!isMobile &&', '!isMobile &&')
    new_children = new_children.replace('{ !isMobile &&', '!isMobile &&')
    
    # And we replaced `/>}` with `/>},` previously.
    # But wait, the script ran before. So it currently has `/>},`
    # Let's fix that too. If there's any stray `},` from that, we should remove the `}`.
    new_children = new_children.replace('/>},', '/>,')
    
    # We must also be careful that we don't break anything else.
    # What about the very end of the children?
    
    new_content = before + flipbook_open + children[:0] + new_children + after
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Fixed flipbook syntax errors!")
