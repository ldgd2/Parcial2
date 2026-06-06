import os
import glob
import re

search_dir = r'c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend\app\packages'
files = glob.glob(os.path.join(search_dir, '**', '*.py'), recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '[cls]' in content:
        # Find the class name in the file
        match = re.search(r'class\s+([A-Za-z0-9_]+)\(GenericModel\):', content)
        if not match:
            match = re.search(r'class\s+([A-Za-z0-9_]+)\(', content)
            
        if match:
            class_name = match.group(1)
            content = content.replace('[cls]', f'["{class_name}"]')
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed {file} with ["{class_name}"]')
        else:
            print(f'Could not find class name in {file}')
