import os
import glob
import re

search_dir = r'c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend\app\packages'
files = glob.glob(os.path.join(search_dir, '**', '*.py'), recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # Replace 'List[' with 'list['
    if 'List[' in content:
        content = content.replace('List[', 'list[')
        changed = True
        
    if changed:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed List[] to list[] in {file}')
