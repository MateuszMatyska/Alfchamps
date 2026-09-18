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


def test_add_sub_point_and_nested_listing(client, project_id):
    parent = client.get(f"/projects/{project_id}").json()["items"][0]
    r = client.post(
        f"/projects/{project_id}/items",
        json={
            "code": "CUSTOM-SUB",
            "title": "Sub check",
            "description": "d",
            "how_to_test": "h",
            "reproduce_steps": "1. do a\n2. do b",
            "parent_id": parent["id"],
        },
    )
    assert r.status_code == 200, r.text
    sub_id = r.json()["id"]
    assert r.json()["reproduce_steps"] == "1. do a\n2. do b"

    detail = client.get(f"/projects/{project_id}").json()
    top_ids = [i["id"] for i in detail["items"]]
    assert sub_id not in top_ids
    parent_out = next(i for i in detail["items"] if i["id"] == parent["id"])
    assert [c["id"] for c in parent_out["children"]] == [sub_id]


def test_sub_point_parent_validation(client, project_id):
    parent = client.get(f"/projects/{project_id}").json()["items"][0]
    sub = client.post(
        f"/projects/{project_id}/items",
        json={"code": "S1", "title": "sub", "parent_id": parent["id"]},
    ).json()
    # a sub-point cannot be used as a parent
    r = client.post(
        f"/projects/{project_id}/items",
        json={"code": "S2", "title": "bad", "parent_id": sub["id"]},
    )
    assert r.status_code == 400
    # parent must belong to the project
    r = client.post(
        f"/projects/{project_id}/items",
        json={"code": "S3", "title": "bad", "parent_id": 999999},
    )
    assert r.status_code == 404


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


def test_exec_summary_roundtrip(client, project_id):
    r = client.put(
        f"/projects/{project_id}/report/config",
        json={
            "accent_color": "#123456",
            "company_name": "ACME",
            "report_title": "My Report",
            "exec_summary": "We tested things.\nMore details.",
        },
    )
    assert r.status_code == 200
    assert r.json()["exec_summary"] == "We tested things.\nMore details."
    got = client.get(f"/projects/{project_id}/report/config").json()
    assert got["exec_summary"] == "We tested things.\nMore details."


def test_memorial_photo_endpoint(client):
    data = client.get("/memorial").json()
    assert isinstance(data["has_photo"], bool)
    r = client.get("/memorial/photo")
    if data["has_photo"]:
        assert r.status_code == 200
        assert r.content[:8] == b"\x89PNG\r\n\x1a\n"
    else:
        assert r.status_code == 404


def test_report_pdf_generated(client, project_id):
    r = client.get(f"/projects/{project_id}/report/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"
    assert r.content.rstrip().endswith(b"%%EOF")


def test_report_pdf_with_sub_points_and_exec_summary(client, project_id):
    parent = client.get(f"/projects/{project_id}").json()["items"][0]
    sub = client.post(
        f"/projects/{project_id}/items",
        json={"code": "C-SUB", "title": "Sub finding", "reproduce_steps": "steps", "parent_id": parent["id"]},
    )
    assert sub.status_code == 200, sub.text
    client.put(
        f"/projects/{project_id}/report/config",
        json={"accent_color": "#123456", "exec_summary": "Executive narrative here"},
    )
    # header of the sub-point (used in the grouped table) must stay out of charts
    r = client.get(f"/projects/{project_id}/report/pdf")
    assert r.status_code == 200
    assert r.content[:5] == b"%PDF-"
    assert r.content.rstrip().endswith(b"%%EOF")
