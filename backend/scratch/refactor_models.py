import os
import glob
import re

search_dir = r'c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend\app\packages'
files = glob.glob(os.path.join(search_dir, '**', 'models', '*.py'), recursive=True)

for file in files:
    if '__init__' in file: continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace import
    content = re.sub(r'from app\.db\.session import Base\s*', 'from app.db.generic_model import GenericModel\n', content)
    
    # Replace class declaration
    content = re.sub(r'class (\w+)\(Base\):', r'class \1(GenericModel):', content)

    # If Taller or Usuario, add schema
    if file.endswith('taller.py') or file.endswith('usuario.py'):
        # Check if it already has __table_args__
        if '__table_args__' not in content:
            content = re.sub(r'__tablename__ = \"(\w+)\"', r'__tablename__ = "\1"\n    __table_args__ = {"schema": "public"}', content)

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print('Done!')
