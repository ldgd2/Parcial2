import os
import glob
import re

search_dir = r'c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend\app\packages'
service_files = glob.glob(os.path.join(search_dir, '**', 'services', '*.py'), recursive=True)

# Map repo variable names to model names
# e.g., repo = TecnicoRepository(db) -> repo points to Tecnico

for file in service_files:
    if '__init__' in file: continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find repo assignments
    repo_assignments = re.findall(r'(\w+)\s*=\s*(\w+)Repository\s*\([^)]*\)', content)
    
    # We will replace all occurrences of repo.method() with Model.method() or object.update()
    for var_name, model_name in repo_assignments:
        # replace `await var_name.create(obj_in=...)` with `await ModelName.create(db, obj_in=...)`
        # Need to be careful: sometimes it's repo.create(...)
        # let's do a simple regex replacement
        content = re.sub(rf'await {var_name}\.create\(', f'await {model_name}.create(db, ', content)
        content = re.sub(rf'await {var_name}\.get\(', f'await {model_name}.get(db, ', content)
        content = re.sub(rf'await {var_name}\.get_all\(', f'await {model_name}.get_all(db, ', content)
        content = re.sub(rf'await {var_name}\.remove\(', f'await {model_name}.remove(db, ', content)
        
        # for update: await repo.update(db_obj=obj, obj_in=data) -> await obj.update(db, obj_in=data)
        # we can't easily regex this if it's not exactly that string, but usually it is:
        content = re.sub(rf'await {var_name}\.update\(db_obj=(\w+),\s*obj_in=', r'await \1.update(db, obj_in=', content)
        
        # custom methods: await repo.get_by_placa(placa) -> await Vehiculo.get_by_placa(db, placa)
        # regex for any other method: await repo.method_name(args)
        # we skip create, get, get_all, remove, update since we handled them.
        content = re.sub(rf'await {var_name}\.([a-zA-Z0-9_]+)\(', f'await {model_name}.\\1(db, ', content)

        # Remove the repo instantiation line
        content = re.sub(rf'\s*{var_name}\s*=\s*{model_name}Repository\s*\([^)]*\)\n', '\n', content)

    # Remove repository imports
    content = re.sub(r'from .*repositories.* import .*\n', '', content)

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Service refactor done!')
