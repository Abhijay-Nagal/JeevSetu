import os
import re

for file_path in ['frontend/src/pages/Home.jsx', 'frontend/src/pages/HomeFeed.jsx']:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace all <Page imagePage... /> that do NOT have !isMobile && in front of them
    # Because they are in an array, they might be preceded by whitespace or a comment.
    
    # Since we know exactly which ones they are:
    # <Page imagePage={true} imageSrc="/book/action.jpg" bookRef={bookRef} />,
    # <Page imagePage={true} imageSrc="/book/final.jpg" bookRef={bookRef} />,
    
    new_content = content.replace(
        '<Page imagePage={true} imageSrc="/book/action.jpg" bookRef={bookRef} />',
        '!isMobile && <Page imagePage={true} imageSrc="/book/action.jpg" bookRef={bookRef} />'
    ).replace(
        '<Page imagePage={true} imageSrc="/book/final.jpg" bookRef={bookRef} />',
        '!isMobile && <Page imagePage={true} imageSrc="/book/final.jpg" bookRef={bookRef} />'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Fixed missing !isMobile && on final image pages!")
