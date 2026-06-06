import os
import glob
import re

search_dir = r'c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend\app\packages'
files = glob.glob(os.path.join(search_dir, '**', '*.py'), recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False

    # 1. Add public. to ForeignKeys
    # Finds ForeignKey("something.something") and if it doesn't start with public., adds it.
    # Exception: if it's already "public." we skip.
    def replacer(match):
        fk_str = match.group(1)
        if not fk_str.startswith("public."):
            return f'ForeignKey("public.{fk_str}"'
        return match.group(0)

    new_content = re.sub(r'ForeignKey\(\"([^"]+)\"', replacer, content)
    if new_content != content:
        content = new_content
        changed = True

    # 2. Add __table_args__ = {"schema": "public"} to all models
    # Find `__tablename__ = "something"`
    # Check if next line is `__table_args__`
    # If not, inject it.
    
    def table_args_replacer(match):
        full_match = match.group(0)
        table_name_line = match.group(1)
        if '__table_args__' not in full_match:
            return f'{table_name_line}\n    __table_args__ = {{"schema": "public"}}'
        return full_match

    new_content = re.sub(r'(__tablename__\s*=\s*"[^"]+")(?!\s*__table_args__)', table_args_replacer, content)
    if new_content != content:
        content = new_content
        changed = True

    if changed:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed ForeignKeys and schemas in {file}')
