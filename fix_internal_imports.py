import os
import re

def update_relative_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.dart'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace import '../ with import '../../
                # But only if it's actually an import
                new_content = re.sub(r"(import|part)\s+['\"](\.\./)", r"\1 '\2../", content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f'Updated internal imports in {filepath}')

update_relative_imports('tallermovil/lib/features/home/ui/client')
update_relative_imports('tallermovil/lib/features/home/ui/tech')
update_relative_imports('tallermovil/lib/features/emergencies/views/detail/client')
update_relative_imports('tallermovil/lib/features/emergencies/views/detail/tech')

