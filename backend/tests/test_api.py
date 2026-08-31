import struct
import zlib


def _png_1x1() -> bytes:
    # A valid, decodable 1x1 RGB PNG (needed by ReportLab in PDF generation).
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))

    idat = zlib.compress(b"\x00\xff\x00\x00")
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_standards_seeded(client):
    r = client.get("/standards")
    data = r.json()
    slugs = {s["slug"] for s in data}
    assert {
        "owasp-top10-web",
        "owasp-api-top10",
        "owasp-asvs",
        "owasp-wstg",
        "owasp-masvs",
        "owasp-genai-top10",
    } <= slugs


def test_asvs_level_filtering(client):
    counts = {}
    for lvl in (1, 2, 3):
        r = client.post(
            "/projects",
            json={"name": f"L{lvl}", "standard_slugs": ["owasp-asvs"], "asvs_level": lvl},
        )
        counts[lvl] = len(r.json()["items"])
    assert counts[1] < counts[2] < counts[3]


def test_asvs_level_does_not_exclude_other_standards(client):
    # Non-ASVS items have NULL asvs_level and must not be filtered out.
    r = client.post(
        "/projects",
        json={
            "name": "Mixed",
            "standard_slugs": ["owasp-asvs", "owasp-api-top10", "owasp-wstg"],
            "asvs_level": 1,
        },
    )
    assert r.status_code == 200
    codes = [i["code"] for i in r.json()["items"]]
    # All API Top 10 items present
    for code in ["API1:2023", "API2:2023", "API10:2023"]:
        assert code in codes
    # All WSTG items present
    assert any(c.startswith("WSTG-") for c in codes)


def test_create_and_update_project_item(client, project_id):
    r = client.get(f"/projects/{project_id}")
    items = r.json()["items"]
    item = items[0]

    patch = client.patch(
        f"/projects/{project_id}/items/{item['id']}",
        json={"status": "failed", "notes": "vuln found", "reproduce_steps": "1. do x"},
    )
    assert patch.status_code == 200
    body = patch.json()
    assert body["status"] == "failed"
    assert body["notes"] == "vuln found"
    assert body["reproduce_steps"] == "1. do x"


def test_add_custom_item(client, project_id):
    r = client.post(
        f"/projects/{project_id}/items",
        json={"code": "CUSTOM-01", "title": "Custom check", "description": "d", "how_to_test": "h"},
    )
    assert r.status_code == 200
    assert r.json()["code"] == "CUSTOM-01"


def test_screenshot_upload_and_serve(client, project_id):
    r = client.get(f"/projects/{project_id}")
    item = r.json()["items"][0]
    png = _png_1x1()
    up = client.post(
        f"/projects/{project_id}/items/{item['id']}/screenshots",
        files={"file": ("shot.png", png, "image/png")},
        data={"alt_text": "evidence"},
    )
    assert up.status_code == 200, up.text
    shot_id = up.json()["id"]
    serve = client.get(f"/projects/{project_id}/items/{item['id']}/screenshots/{shot_id}/file")
    assert serve.status_code == 200
    assert serve.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_screenshot_rejects_non_image(client, project_id):
    r = client.get(f"/projects/{project_id}")
    item = r.json()["items"][0]
    bad = b"this is definitely not an image"
    up = client.post(
        f"/projects/{project_id}/items/{item['id']}/screenshots",
        files={"file": ("fake.png", bad, "image/png")},
    )
    assert up.status_code == 400


def test_company_logo_upload(client, project_id):
    png = _png_1x1()
    r = client.post(
        f"/projects/{project_id}/report/config/logo",
        files={"file": ("logo.png", png, "image/png")},
    )
    assert r.status_code == 200, r.text
    assert "filename" in r.json()


def test_report_config(client, project_id):
    r = client.put(
        f"/projects/{project_id}/report/config",
        json={"accent_color": "#123456", "company_name": "ACME", "report_title": "My Report"},
    )
    assert r.status_code == 200
    assert r.json()["company_name"] == "ACME"


def test_report_pdf_generated(client, project_id):
    r = client.get(f"/projects/{project_id}/report/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"
    assert r.content.rstrip().endswith(b"%%EOF")
