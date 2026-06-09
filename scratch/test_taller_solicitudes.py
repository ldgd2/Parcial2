import requests
resp = requests.get('http://62.171.133.23:8000/api/v1/talleres/GERLEXSRYK/solicitudes')
if resp.status_code == 200:
    for e in resp.json():
        tecnicos = [t['id'] for t in e.get('tecnicos_asignados', [])]
        print(f"ID: {e['id']}, Estado Actual: {e.get('estado_actual')}, Tecnicos: {tecnicos}")
else:
    print(resp.status_code)
