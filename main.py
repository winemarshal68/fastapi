from fastapi import FastAPI, Request
import requests, os, base64, datetime

app = FastAPI()

GITHUB_REPO = "winemarshal68/orca-presets"   # the repo where files will be uploaded
GITHUB_BRANCH = "main"

def push_to_github(path, message, content):
    """Commit a file to your GitHub repo."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {os.environ['GH_TOKEN']}"}
    b64content = base64.b64encode(content.encode()).decode()
    payload = {"message": message, "content": b64content, "branch": GITHUB_BRANCH}
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code not in (200, 201):
        return {"error": r.json(), "status": r.status_code}
    return {"success": True, "status": r.status_code, "commit": r.json()}

@app.get("/")
def home():
    return {"status": "ok", "message": "Orca/Bambu Preset Uploader active."}

@app.post("/upload-filament")
async def upload_filament(request: Request):
    data = await request.json()
    if "filament_name" not in data:
        return {"error": "Missing filament_name"}
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"filaments/{data['filament_name'].replace(' ', '_')}_{timestamp}.json"
    message = f"Add filament preset: {data['filament_name']}"
    return push_to_github(filename, message, await request.body())

@app.post("/upload-preset")
async def upload_preset(request: Request):
    data = await request.json()
    if "printer_model" not in data:
        return {"error": "Missing printer_model"}
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    name = data.get("project_name", "unnamed")
    slicer = data.get("slicer", "orca")
    filename = f"presets/{slicer}/{data['printer_model'].replace(' ', '_')}_{name}_{timestamp}.json"
    message = f"Add preset: {data['printer_model']} – {name}"
    return push_to_github(filename, message, await request.body())
