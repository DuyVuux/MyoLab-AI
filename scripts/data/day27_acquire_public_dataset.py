from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import argparse
import json
import os
import tempfile
import urllib.request
from datetime import datetime, timezone

from data.day27.contracts import canonical_sha256
from data.day27.hashing import sha256_file
from data.day27.source_record import validate_source_record

parser = argparse.ArgumentParser(description="Controlled public dataset downloader; dry-run by default.")
parser.add_argument("--record", type=Path, required=True)
parser.add_argument("--destination", type=Path, required=True)
mode = parser.add_mutually_exclusive_group()
mode.add_argument("--dry-run", action="store_true")
mode.add_argument("--execute", action="store_true")
parser.add_argument("--accept-license", action="store_true")
args = parser.parse_args()
record = json.loads(args.record.read_text(encoding="utf-8"))
validation = validate_source_record(record)
if validation["status"] != "VERIFIED":
    raise SystemExit("SOURCE_RECORD_INVALID: " + ";".join(validation["errors"]))
url = record["download"]["url"]
file_name = record["download"]["expectedFileName"]
print(json.dumps({"mode":"execute" if args.execute else "dry-run","url":url,"destination":str(args.destination/file_name)}, ensure_ascii=False, indent=2))
if not args.execute:
    raise SystemExit(0)
if not args.accept_license:
    raise SystemExit("--accept-license is required for execute mode")
args.destination.mkdir(parents=True, exist_ok=True)
final_path = args.destination / file_name
part_path = final_path.with_suffix(final_path.suffix + ".part")
max_bytes = record["download"].get("maxBytes")
request = urllib.request.Request(url, headers={"User-Agent":"MyoLab-AI-Day27/1.0"})
with urllib.request.urlopen(request, timeout=60) as response, part_path.open("wb") as out:
    total = 0
    while chunk := response.read(1024 * 1024):
        total += len(chunk)
        if max_bytes is not None and total > int(max_bytes):
            part_path.unlink(missing_ok=True)
            raise SystemExit("DOWNLOAD_EXCEEDS_MAX_BYTES")
        out.write(chunk)
os.replace(part_path, final_path)
receipt = {
    "schemaVersion":"retrieval-receipt.v1",
    "datasetId":record["datasetId"],
    "sourceRecordSha256":canonical_sha256(record),
    "downloadUrl":url,
    "finalUrl":response.geturl(),
    "retrievedAt":datetime.now(timezone.utc).isoformat(),
    "fileName":final_path.name,
    "sizeBytes":final_path.stat().st_size,
    "sha256":sha256_file(final_path),
    "httpMetadata":{},
    "licenseAccepted":True,
}
receipt_path = args.destination / "retrieval-receipt.json"
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(receipt_path)
