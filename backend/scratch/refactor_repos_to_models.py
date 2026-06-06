import os
import glob
import re

search_dir = r'c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend\app\packages'
repo_files = glob.glob(os.path.join(search_dir, '**', 'repositories', '*_repo.py'), recursive=True)

for repo_file in repo_files:
    if '__init__' in repo_file: continue
    
    with open(repo_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract model name
    model_match = re.search(r'class \w+Repository\(BaseRepository\[(\w+),', content)
    if not model_match: continue
    model_name = model_match.group(1)
    
    # Find the corresponding model file
    # we know repo_file is in .../repositories/name_repo.py
    # model is in .../models/name.py
    # a simpler way is to just find where `class ModelName(GenericModel):` is defined.
    model_file_paths = glob.glob(os.path.join(search_dir, '**', 'models', '*.py'), recursive=True)
    target_model_file = None
    for mf in model_file_paths:
        with open(mf, 'r', encoding='utf-8') as f:
            if f'class {model_name}(GenericModel):' in f.read():
                target_model_file = mf
                break
                
    if not target_model_file: continue
    
    # Extract custom methods from repository class
    # Find all `async def ...` inside the repository class
    # Regex to capture methods inside the class
    class_def_pattern = re.compile(r'class \w+Repository\(.*?\):(.*)', re.DOTALL)
    class_match = class_def_pattern.search(content)
    if not class_match: continue
    
    class_body = class_match.group(1)
    
    # We want to skip __init__
    methods = re.findall(r'(    async def \w+\(self.*?)(?=\n    async def|\Z)', class_body, re.DOTALL)
    
    if not methods: continue
    
    with open(target_model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
        
    # Import select, joinedload, delete etc if they don\'t exist in the model file
    if 'from sqlalchemy import' not in model_content:
        model_content = 'from sqlalchemy import select, delete\n' + model_content
    elif 'select' not in model_content:
        model_content = model_content.replace('from sqlalchemy import ', 'from sqlalchemy import select, delete, ')
        
    if 'from sqlalchemy.ext.asyncio import AsyncSession' not in model_content:
        model_content = 'from sqlalchemy.ext.asyncio import AsyncSession\n' + model_content
        
    # Append methods to model class
    methods_str = "\n"
    for method in methods:
        # replace `def func(self, ...)` with `@classmethod\n    async def func(cls, db: AsyncSession, ...)`
        # also replace `self.db` with `db`, and `ModelName` with `cls`
        m = method
        m = re.sub(r'async def (\w+)\(self,\s*', r'@classmethod\n    async def \1(cls, db: AsyncSession, ', m)
        m = re.sub(r'async def (\w+)\(self\s*\)', r'@classmethod\n    async def \1(cls, db: AsyncSession)', m)
        
        m = m.replace('self.db', 'db')
        m = m.replace(f'{model_name}', 'cls')
        
        methods_str += m + "\n"
        
    model_content += methods_str
    
    with open(target_model_file, 'w', encoding='utf-8') as f:
        f.write(model_content)

print('Repos to models refactor done!')
