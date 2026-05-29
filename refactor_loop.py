import os
import glob
import re

files = glob.glob('cli/**/*.py', recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "def interactive_menu():" not in content:
        continue
        
    lines = content.split('\n')
    out_lines = []
    in_menu = False
    imports_done = False
    
    for line in lines:
        if line.startswith('def interactive_menu():'):
            in_menu = True
            out_lines.append(line)
            continue
            
        if in_menu:
            if line.startswith('def ') or line.startswith('class '):
                in_menu = False
                out_lines.append(line)
                continue
                
            if not line.strip():
                out_lines.append(line)
                continue
                
            if not imports_done and ('import ' in line or '"""' in line) and line.startswith('    '):
                out_lines.append(line)
            else:
                if not imports_done:
                    imports_done = True
                    out_lines.append('    while True:')
                    # Fix break conditions
                
                # Check for return on Volver
                if 'return' in line and ('Volver' in content or 'Salir' in content) and not line.strip().startswith('def '):
                    # Replace return with break to escape the loop
                    line = line.replace('return', 'break')
                
                if line.strip():
                    out_lines.append('    ' + line)
                else:
                    out_lines.append(line)
        else:
            out_lines.append(line)
            
    with open(file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
    print(f'Processed {file}')
