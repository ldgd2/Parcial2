import os

models_dir = "backend/app/packages"
for root, dirs, files in os.walk(models_dir):
    for file in files:
        if file.endswith(".py") and "models" in root:
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                content = f.read()
                if "__tablename__" in content and "__table_args__" not in content:
                    print(f"Missing schema in: {os.path.join(root, file)}")
