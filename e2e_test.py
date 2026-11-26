import requests, json, time
from pathlib import Path

BASE = "http://127.0.0.1:8000"

# 1. Health
r = requests.get(f"{BASE}/api/health")
h = r.json()
print("=== HEALTH ===")
print(f"  status:      {h['status']}")
print(f"  YOLO custom: {h['models']['yolo']['is_custom']}")
print(f"  VLM ready:   {h['models']['vlm']['available']}")
print(f"  OCR ready:   {h['models']['ocr']['available']}")

# 2. Upload a test image
test_imgs = list(Path("archive (3)/traffic_dataset/test").glob("*.jpg"))[:1]
img_path = test_imgs[0]
print(f"\n=== UPLOAD: {img_path.name[:55]} ===")
with open(img_path, "rb") as f:
    r = requests.post(f"{BASE}/api/upload", files={"file": (img_path.name, f, "image/jpeg")})
up = r.json()
upload_id = up["upload_id"]
print(f"  upload_id={upload_id}  file_type={up['file_type']}  status={up['status']}")

# 3. Analyze
print(f"\n=== ANALYZE (upload_id={upload_id}) ===")
r = requests.post(f"{BASE}/api/image/analyze", json={"upload_id": upload_id, "mode": "explain"})
ana = r.json()
task_id = ana.get("task_id")
print(f"  task_id={task_id}  initial_status={ana.get('status')}")

# 4. Poll until done
for i in range(40):
    r = requests.get(f"{BASE}/api/image/result/{task_id}")
    res = r.json()
    prog = res.get("progress", 0)
    status = res.get("status", "?")
    print(f"  t={i*2}s  progress={prog}%  status={status}")
    if status in ("completed", "failed"):
        break
    time.sleep(2)

print(f"\n=== RESULT ===")
print(f"  Final status: {status}")
if status == "completed":
    exp = res.get("explanation", "")
    print(f"  Explanation ({len(exp)} chars): {exp[:150]}")
    signs = res.get("detected_signs", [])
    ocr   = res.get("ocr_results", [])
    audio = res.get("audio_id", "")
    print(f"  Signs detected: {signs}")
    print(f"  OCR results:    {ocr[:3]}")
    print(f"  Audio ID:       {audio}")
elif status == "failed":
    print(f"  Error: {res.get('error', 'unknown')}")

# 5. Test audio generation via SAPI
print(f"\n=== AUDIO GENERATION (Windows SAPI) ===")
r = requests.post(f"{BASE}/api/audio/generate", json={
    "upload_id": upload_id,
    "text": "This is a test of the audio narration system. Traffic sign detected: narrow road ahead.",
    "speed": 1.0
})
if r.status_code == 200:
    aud = r.json()
    print(f"  audio_id:  {aud['audio_id']}")
    print(f"  audio_url: {aud['audio_url']}")
    # Verify file is streamable
    r2 = requests.get(f"{BASE}{aud['audio_url']}", stream=True)
    print(f"  stream status: {r2.status_code}  content-type: {r2.headers.get('content-type')}")
    print(f"  file size:     {int(r2.headers.get('content-length', 0)) // 1024} KB")
else:
    print(f"  FAILED: {r.status_code}  {r.json()}")

print("\n=== END-TO-END CHECK COMPLETE ===")
