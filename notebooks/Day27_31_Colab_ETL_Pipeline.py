# %% [markdown]
# # 🧪 MyoLab-AI — Colab ETL Pipeline (Day 27→31)
#
# **Mục tiêu:** Tải dữ liệu thô Mendeley 4-Channel Hand Gesture v2 từ API,
# trích xuất đặc trưng (14 features × 3 channels × N windows), và xuất ra
# file `.npz` nhỏ gọn (~50-100 MB) để chạy Day 32 Baseline Modeling trên máy local.
#
# **Kiến trúc 2-Zone:**
# - Zone 1 (Code): Repo GitHub `MyoLab-AI` → clone về Colab
# - Zone 2 (Data): Tải tạm vào `/content/data/` trên Colab, KHÔNG lưu vào Drive
#
# **Quy trình:**
# 1. Clone repo & cài dependencies
# 2. Tải raw MAT files từ Mendeley API
# 3. Parse MAT → numpy, sinh metadata-index.csv
# 4. Build window index (Day 30)
# 5. Extract Feature Set 14 (Day 31)
# 6. Pivot to wide matrix `.npz` (Day 32 input)
# 7. Download `.npz` về máy local
#
# > ⚠️ **Governance:** `training_allowed=False` trong notebook này.
# > Notebook chỉ thực hiện ETL (Extract-Transform-Load), KHÔNG train model.

# %% [markdown]
# ## 0. Setup, Clone Repo & Mount vs Drive

# %%
# === CELL 0: Environment Setup ===
import subprocess
import sys
import os
from google.colab import userdata

# Detect Colab
IN_COLAB = 'google.colab' in sys.modules if 'google.colab' in dir() else False
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

print(f"Running in Colab: {IN_COLAB}")

try:
    GH_TOKEN = userdata.get('GH_TOKEN')
    GITHUB_REPO = f"https://{GH_TOKEN}@github.com/DuyVuux/MyoLab-AI.git"
except Exception:
    print("Warning: GH_TOKEN not found in Secrets. Private repo clone might fail.")
    GITHUB_REPO = "https://github.com/DuyVuux/MyoLab-AI.git"

BRANCH = "main"
DATA_DIR = "/content/data" if IN_COLAB else "./data_temp"
REPO_DIR = "/content/MyoLab-AI" if IN_COLAB else "."
MAX_SUBJECTS = 36

# %%
# === CELL 1: Clone repo (Colab only) ===
if IN_COLAB:
    if not os.path.exists(REPO_DIR):
        print(f"Cloning private repository...")
        subprocess.run(
            ["git", "clone", "--depth", "1", GITHUB_REPO, REPO_DIR],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Cloned successfully to {REPO_DIR}")
    else:
        print(f"ℹRepo already exists at {REPO_DIR}")

    # Install dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q",
         "numpy", "scipy", "scikit-learn", "requests", "pyyaml"],
        check=True,
    )
    print("Dependencies installed")

# %%
# === CELL 2: Initialize Day 27-31 storage architecture ===

from pathlib import Path

TRAINING_ALLOWED = False

assert TRAINING_ALLOWED is False, (
    "Notebook Day 27-31 chỉ thực hiện ETL. "
    "Không được phép train model."
)

DATASET_ID = "ckwc76xr2z"
DATASET_VERSION = 2
DATASET_ARCHIVE_NAME = "ckwc76xr2z-2.zip"

# ============================================================
# Persistent zone: Google Drive
# ============================================================

DRIVE_DATASET_ROOT = Path(
    "/content/drive/MyDrive/"
    "MyoLab-AI-data/"
    "mendeley-4channel-hand-gesture-v2"
)

DRIVE_DOWNLOAD_DIR = DRIVE_DATASET_ROOT / "downloads"
DRIVE_MANIFEST_DIR = DRIVE_DATASET_ROOT / "manifests"
DRIVE_OUTPUT_DIR = DRIVE_DATASET_ROOT / "outputs"

# ============================================================
# Processing zone: Colab local runtime
# ============================================================

RUNTIME_DATASET_ROOT = Path(
    "/content/data/mendeley-4channel-hand-gesture-v2"
)

RUNTIME_DOWNLOAD_DIR = RUNTIME_DATASET_ROOT / "downloads"
RUNTIME_ACQUIRED_DIR = RUNTIME_DATASET_ROOT / "acquired"
RUNTIME_EXTRACTED_DIR = RUNTIME_DATASET_ROOT / "extracted"
RUNTIME_INDEX_DIR = RUNTIME_DATASET_ROOT / "indexes"
RUNTIME_FEATURE_DIR = RUNTIME_DATASET_ROOT / "features"
RUNTIME_MATRIX_DIR = RUNTIME_DATASET_ROOT / "matrices"
RUNTIME_MANIFEST_DIR = RUNTIME_DATASET_ROOT / "manifests"
RUNTIME_LOG_DIR = RUNTIME_DATASET_ROOT / "logs"
RUNTIME_CACHE_DIR = RUNTIME_DATASET_ROOT / "cache"

ALL_DIRECTORIES = [
    DRIVE_DOWNLOAD_DIR,
    DRIVE_MANIFEST_DIR,
    DRIVE_OUTPUT_DIR,
    RUNTIME_DOWNLOAD_DIR,
    RUNTIME_ACQUIRED_DIR,
    RUNTIME_EXTRACTED_DIR,
    RUNTIME_INDEX_DIR,
    RUNTIME_FEATURE_DIR,
    RUNTIME_MATRIX_DIR,
    RUNTIME_MANIFEST_DIR,
    RUNTIME_LOG_DIR,
    RUNTIME_CACHE_DIR,
]

for directory in ALL_DIRECTORIES:
    directory.mkdir(parents=True, exist_ok=True)

DRIVE_ZIP_PATH = DRIVE_DOWNLOAD_DIR / DATASET_ARCHIVE_NAME
RUNTIME_ZIP_PATH = RUNTIME_DOWNLOAD_DIR / DATASET_ARCHIVE_NAME

print("[INFO] Storage architecture initialized.")
print()
print(f"[DRIVE ROOT]   {DRIVE_DATASET_ROOT}")
print(f"[RUNTIME ROOT] {RUNTIME_DATASET_ROOT}")
print()
print(f"[ZIP ON DRIVE] {DRIVE_ZIP_PATH}")
print(f"[ZIP RUNTIME]  {RUNTIME_ZIP_PATH}")

# %%
# === CELL 2A: Mount Google Drive ===

from google.colab import drive

drive.mount(
    "/content/drive"
)

# %%
# === CELL 2B: Configure persistent data root ===

from pathlib import Path

DATA_DIR = Path(
    "/content/drive/MyDrive/MyoLab-AI-data/"
    "mendeley-4channel-hand-gesture-v2"
)

CACHE_DIR = DATA_DIR / "cache"
ACQUIRED_DIR = DATA_DIR / "acquired"
EVIDENCE_DIR = DATA_DIR / "evidence"

for directory in [
    CACHE_DIR,
    ACQUIRED_DIR,
    EVIDENCE_DIR,
]:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

print(f"[INFO] DATA_DIR: {DATA_DIR}")
print(f"[INFO] CACHE_DIR: {CACHE_DIR}")

# %%
# === CELL 2C: Verify raw MAT inputs ===

from pathlib import Path

DATA_DIR = Path(DATA_DIR)

search_roots = [
    DATA_DIR / "cache",
    DATA_DIR / "acquired",
]

print("=" * 72)
print("[INPUT AUDIT]")
print(f"DATA_DIR: {DATA_DIR.resolve()}")

all_mat_files = []

for root in search_roots:
    print(f"\nDirectory: {root}")
    print(f"Exists: {root.exists()}")

    if root.exists():
        files = sorted(
            root.rglob("*_raw.mat")
        )

        print(
            f"Raw MAT count: {len(files)}"
        )

        for path in files[:10]:
            print(
                f"  - {path.name}: "
                f"{path.stat().st_size / 1024**2:.2f} MiB"
            )

        if len(files) > 10:
            print(
                f"  ... and {len(files) - 10} more"
            )

        all_mat_files.extend(files)

print("\n" + "-" * 72)
print(
    f"Total discovered raw MAT paths: "
    f"{len(all_mat_files)}"
)
print("=" * 72)

# %% [markdown]
# ## 1. Download Mendeley Raw Data (Day 27 — Ingestion)
#
# Sử dụng logic từ `scripts/data/run_mendeley_real_eda.py`:
# - API endpoint: `https://data.mendeley.com/api/datasets/ckwc76xr2z/files`
# - Chỉ tải `*_raw.mat` (~10MB/file, nhỏ hơn CSV 8 lần)
# - Mỗi file chứa: `data` (N×4 float64), `fs` (sampling rate), `iD` (subject ID)

# %%
# === CELL 3: Stage ZIP from Google Drive and acquire raw MAT files ===

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile


# ============================================================
# 1. Governance
# ============================================================

TRAINING_ALLOWED = False

assert TRAINING_ALLOWED is False, (
    "Notebook này chỉ thực hiện ETL. "
    "Không được phép train model trong notebook này."
)


# ============================================================
# 2. Dataset identity
# ============================================================

DATASET_ID = "ckwc76xr2z"
DATASET_VERSION = 2
DATASET_SLUG = "mendeley-4channel-hand-gesture-v2"

SOURCE_ZIP_NAME = "ckwc76xr2z-2.zip"

# Khi False:
# - ZIP giống nhau sẽ không copy lại
# - dataset đã giải nén đúng phiên bản sẽ không giải nén lại
#
# Chỉ đổi thành True khi muốn làm sạch và chạy lại acquisition.
FORCE_REFRESH = False


# ============================================================
# 3. Google Drive paths — persistent storage
# ============================================================

DRIVE_ROOT = (
    Path("/content/drive/MyDrive/MyoLab-AI-data")
    / DATASET_SLUG
)

DRIVE_DOWNLOAD_DIR = DRIVE_ROOT / "downloads"
DRIVE_MANIFEST_DIR = DRIVE_ROOT / "manifests"
DRIVE_OUTPUT_DIR = DRIVE_ROOT / "outputs"

SOURCE_ZIP_PATH = DRIVE_DOWNLOAD_DIR / SOURCE_ZIP_NAME


# ============================================================
# 4. Colab Runtime paths — fast temporary processing
# ============================================================

RUNTIME_ROOT = Path("/content/data") / DATASET_SLUG

RUNTIME_DOWNLOAD_DIR = RUNTIME_ROOT / "downloads"
ACQUIRED_DIR = RUNTIME_ROOT / "acquired"
EXTRACTED_DIR = RUNTIME_ROOT / "extracted"
INDEX_DIR = RUNTIME_ROOT / "indexes"
FEATURE_DIR = RUNTIME_ROOT / "features"
MATRIX_DIR = RUNTIME_ROOT / "matrices"
MANIFEST_DIR = RUNTIME_ROOT / "manifests"
LOG_DIR = RUNTIME_ROOT / "logs"
CACHE_DIR = RUNTIME_ROOT / "cache"

RUNTIME_ZIP_PATH = RUNTIME_DOWNLOAD_DIR / SOURCE_ZIP_NAME

ACQUISITION_MANIFEST_PATH = (
    MANIFEST_DIR / "acquisition-manifest.csv"
)

PROVENANCE_PATH = (
    MANIFEST_DIR / "acquisition-provenance.json"
)

EXTRACTION_MARKER_PATH = (
    CACHE_DIR / "extraction-state.json"
)


# ============================================================
# 5. Create required directories
# ============================================================

required_directories = [
    DRIVE_MANIFEST_DIR,
    DRIVE_OUTPUT_DIR,
    RUNTIME_DOWNLOAD_DIR,
    ACQUIRED_DIR,
    EXTRACTED_DIR,
    INDEX_DIR,
    FEATURE_DIR,
    MATRIX_DIR,
    MANIFEST_DIR,
    LOG_DIR,
    CACHE_DIR,
]

for directory in required_directories:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# 6. Helper functions
# ============================================================

def utc_now_iso() -> str:
    """Trả về timestamp UTC theo chuẩn ISO 8601."""

    return datetime.now(timezone.utc).isoformat()


def sha256_file(
    file_path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Tính SHA-256 theo từng chunk để không nạp toàn bộ file vào RAM.
    """

    digest = hashlib.sha256()

    with file_path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def atomic_copy(
    source_path: Path,
    destination_path: Path,
) -> None:
    """
    Copy qua file .part rồi atomic rename.

    Nếu Colab mất kết nối trong lúc copy, file đích chính thức
    sẽ không bị để lại ở trạng thái dở dang.
    """

    temporary_path = destination_path.with_suffix(
        destination_path.suffix + ".part"
    )

    temporary_path.unlink(missing_ok=True)

    try:
        shutil.copy2(source_path, temporary_path)

        if temporary_path.stat().st_size != source_path.stat().st_size:
            raise RuntimeError(
                "Kích thước file sau khi copy không khớp:\n"
                f"Source: {source_path.stat().st_size:,} bytes\n"
                f"Copied: {temporary_path.stat().st_size:,} bytes"
            )

        temporary_path.replace(destination_path)

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def is_zip_symlink(zip_info) -> bool:
    """
    Phát hiện symbolic link trong ZIP dựa trên Unix file mode.
    """

    unix_mode = zip_info.external_attr >> 16

    return stat.S_ISLNK(unix_mode)


def validate_zip_archive(
    zip_path: Path,
) -> list:
    """
    Kiểm tra:
    - đúng định dạng ZIP;
    - không có lỗi CRC;
    - không có path traversal;
    - không chứa symbolic link.

    Trả về danh sách ZipInfo.
    """

    if not zip_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy ZIP: {zip_path}"
        )

    if not zip_path.is_file():
        raise RuntimeError(
            f"Đường dẫn ZIP không phải file: {zip_path}"
        )

    if zip_path.stat().st_size <= 0:
        raise RuntimeError(
            f"ZIP có kích thước bằng 0 byte: {zip_path}"
        )

    destination_root = EXTRACTED_DIR.resolve()

    try:
        with ZipFile(zip_path, "r") as archive:
            members = archive.infolist()

            if not members:
                raise RuntimeError(
                    "ZIP hợp lệ về cấu trúc nhưng không chứa entry nào."
                )

            for member in members:
                if is_zip_symlink(member):
                    raise RuntimeError(
                        "Không cho phép symbolic link trong ZIP: "
                        f"{member.filename}"
                    )

                member_output_path = (
                    EXTRACTED_DIR / member.filename
                ).resolve()

                try:
                    member_output_path.relative_to(destination_root)
                except ValueError as exc:
                    raise RuntimeError(
                        "Phát hiện path traversal trong ZIP: "
                        f"{member.filename}"
                    ) from exc

            print("[INFO] Đang kiểm tra CRC của ZIP...")

            corrupted_member = archive.testzip()

            if corrupted_member is not None:
                raise RuntimeError(
                    "ZIP có entry lỗi CRC: "
                    f"{corrupted_member}"
                )

            return members

    except BadZipFile as exc:
        raise RuntimeError(
            f"File không phải ZIP hợp lệ hoặc đã bị hỏng: {zip_path}"
        ) from exc


def safe_extract_zip(
    zip_path: Path,
    destination: Path,
) -> None:
    """
    Giải nén ZIP sau khi đã kiểm tra cấu trúc và CRC.
    """

    with ZipFile(zip_path, "r") as archive:
        archive.extractall(destination)


def load_json_if_exists(
    json_path: Path,
) -> dict | None:
    """Đọc JSON nếu tồn tại và hợp lệ."""

    if not json_path.exists():
        return None

    try:
        with json_path.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    except (json.JSONDecodeError, OSError):
        return None


def write_json(
    payload: dict,
    output_path: Path,
) -> None:
    """Ghi JSON UTF-8, định dạng dễ đọc."""

    with output_path.open("w", encoding="utf-8") as file_obj:
        json.dump(
            payload,
            file_obj,
            ensure_ascii=False,
            indent=2,
        )


def raw_mat_sort_key(path: Path):
    """
    Sắp xếp tên subject theo số nếu filename có dạng:
    1_raw.mat, 2_raw.mat, ...
    """

    subject_id = path.name[:-len("_raw.mat")]

    if subject_id.isdigit():
        return 0, int(subject_id)

    return 1, subject_id.lower()


# ============================================================
# 7. Input gate — verify Drive and source ZIP
# ============================================================

print("=" * 78)
print("[CELL 3] STAGE AND ACQUIRE MENDELEY MAT DATASET")
print("=" * 78)

MY_DRIVE_PATH = Path("/content/drive/MyDrive")

if not MY_DRIVE_PATH.exists():
    raise RuntimeError(
        "Google Drive chưa được mount.\n\n"
        "Hãy chạy trước:\n"
        "from google.colab import drive\n"
        "drive.mount('/content/drive')"
    )

if not SOURCE_ZIP_PATH.exists():
    raise FileNotFoundError(
        "Không tìm thấy file ZIP nguồn.\n"
        f"Expected path:\n{SOURCE_ZIP_PATH}\n\n"
        "Hãy kiểm tra lại tên file và vị trí trong Google Drive."
    )

if not SOURCE_ZIP_PATH.is_file():
    raise RuntimeError(
        f"Đường dẫn nguồn không phải file: {SOURCE_ZIP_PATH}"
    )

if SOURCE_ZIP_PATH.suffix.lower() != ".zip":
    raise RuntimeError(
        f"File nguồn không có phần mở rộng .zip: {SOURCE_ZIP_PATH.name}"
    )

source_size_bytes = SOURCE_ZIP_PATH.stat().st_size

if source_size_bytes <= 0:
    raise RuntimeError(
        f"ZIP nguồn có kích thước bằng 0 byte: {SOURCE_ZIP_PATH}"
    )

print(f"[INPUT] Drive ZIP : {SOURCE_ZIP_PATH}")
print(
    f"[INPUT] Size      : "
    f"{source_size_bytes / 1024**2:.2f} MB"
)


# ============================================================
# 8. Calculate source SHA-256
# ============================================================

print("\n[INFO] Đang tính SHA-256 cho ZIP trên Google Drive...")

source_zip_sha256 = sha256_file(SOURCE_ZIP_PATH)

print(f"[INFO] Source SHA-256: {source_zip_sha256}")


# ============================================================
# 9. Stage ZIP from Drive to Colab Runtime
# ============================================================

copy_required = FORCE_REFRESH

if not RUNTIME_ZIP_PATH.exists():
    copy_required = True

elif RUNTIME_ZIP_PATH.stat().st_size != source_size_bytes:
    print(
        "[WARN] Runtime ZIP có kích thước khác source ZIP."
    )
    copy_required = True

else:
    print(
        "\n[INFO] Runtime ZIP đã tồn tại. "
        "Đang kiểm tra SHA-256..."
    )

    runtime_existing_sha256 = sha256_file(RUNTIME_ZIP_PATH)

    if runtime_existing_sha256 != source_zip_sha256:
        print(
            "[WARN] Runtime ZIP không cùng checksum với source ZIP."
        )
        copy_required = True


if copy_required:
    print(
        "\n[INFO] Đang copy ZIP từ Google Drive "
        "sang Colab Runtime..."
    )

    atomic_copy(
        source_path=SOURCE_ZIP_PATH,
        destination_path=RUNTIME_ZIP_PATH,
    )

    print(f"[OK] Copied ZIP: {RUNTIME_ZIP_PATH}")

else:
    print(
        "[SKIP] Runtime ZIP đã tồn tại và khớp checksum."
    )


# ============================================================
# 10. Verify staged ZIP checksum
# ============================================================

print("\n[INFO] Đang xác minh Runtime ZIP...")

runtime_zip_sha256 = sha256_file(RUNTIME_ZIP_PATH)

if runtime_zip_sha256 != source_zip_sha256:
    raise RuntimeError(
        "STAGING GATE FAILED: SHA-256 không khớp.\n"
        f"Source : {source_zip_sha256}\n"
        f"Runtime: {runtime_zip_sha256}"
    )

print("[PASS] Source ZIP và Runtime ZIP có cùng SHA-256.")


# ============================================================
# 11. Validate ZIP content and CRC
# ============================================================

zip_members = validate_zip_archive(RUNTIME_ZIP_PATH)

zip_mat_members = [
    member
    for member in zip_members
    if (
        not member.is_dir()
        and Path(member.filename).suffix.lower() == ".mat"
    )
]

zip_raw_mat_members = [
    member
    for member in zip_mat_members
    if Path(member.filename).name.lower().endswith("_raw.mat")
]

print(f"\n[INFO] ZIP entries       : {len(zip_members)}")
print(f"[INFO] MAT entries       : {len(zip_mat_members)}")
print(f"[INFO] *_raw.mat entries : {len(zip_raw_mat_members)}")

if not zip_mat_members:
    raise RuntimeError(
        "ZIP GATE FAILED: ZIP không chứa file .mat nào."
    )

if not zip_raw_mat_members:
    raise RuntimeError(
        "ZIP GATE FAILED: Không tìm thấy file '*_raw.mat'.\n"
        "Không được tự động thay đổi quy ước dữ liệu.\n"
        "Cần inspect cấu trúc ZIP trước khi tiếp tục."
    )

print("[PASS] ZIP hợp lệ, CRC đạt và có raw MAT files.")


# ============================================================
# 12. Decide whether extraction is required
# ============================================================

previous_extraction_state = load_json_if_exists(
    EXTRACTION_MARKER_PATH
)

extraction_required = FORCE_REFRESH

if previous_extraction_state is None:
    extraction_required = True

elif (
    previous_extraction_state.get("source_zip_sha256")
    != source_zip_sha256
):
    print(
        "[INFO] ZIP checksum đã thay đổi so với lần giải nén trước."
    )
    extraction_required = True

elif not EXTRACTED_DIR.exists():
    extraction_required = True

else:
    existing_extracted_raw_mat = [
        path
        for path in EXTRACTED_DIR.rglob("*")
        if (
            path.is_file()
            and path.name.lower().endswith("_raw.mat")
        )
    ]

    expected_raw_mat_count = int(
        previous_extraction_state.get(
            "raw_mat_file_count",
            -1,
        )
    )

    if len(existing_extracted_raw_mat) != expected_raw_mat_count:
        print(
            "[WARN] Số raw MAT hiện tại không khớp extraction marker."
        )
        extraction_required = True


# ============================================================
# 13. Safe extraction
# ============================================================

if extraction_required:
    print("\n[INFO] Đang chuẩn bị giải nén dataset...")

    if EXTRACTED_DIR.exists():
        shutil.rmtree(EXTRACTED_DIR)

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    safe_extract_zip(
        zip_path=RUNTIME_ZIP_PATH,
        destination=EXTRACTED_DIR,
    )

    print(f"[OK] Extracted to: {EXTRACTED_DIR}")

else:
    print(
        "\n[SKIP] Dataset đã được giải nén trước đó "
        "và extraction state vẫn hợp lệ."
    )


# ============================================================
# 14. Discover extracted MAT files
# ============================================================

extracted_mat_files = sorted(
    [
        path
        for path in EXTRACTED_DIR.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower() == ".mat"
        )
    ],
    key=lambda path: str(path).lower(),
)

extracted_raw_mat_files = sorted(
    [
        path
        for path in extracted_mat_files
        if path.name.lower().endswith("_raw.mat")
    ],
    key=raw_mat_sort_key,
)

print(
    f"\n[INFO] Extracted MAT files       : "
    f"{len(extracted_mat_files)}"
)

print(
    f"[INFO] Extracted *_raw.mat files: "
    f"{len(extracted_raw_mat_files)}"
)

if len(extracted_raw_mat_files) != len(zip_raw_mat_members):
    raise RuntimeError(
        "EXTRACTION GATE FAILED.\n"
        f"ZIP chứa {len(zip_raw_mat_members)} raw MAT nhưng "
        f"sau giải nén tìm thấy {len(extracted_raw_mat_files)}."
    )


# ============================================================
# 15. Build acquired zone
# ============================================================

# acquired/ chỉ chứa canonical raw MAT files.
# Xóa nội dung cũ để tránh dữ liệu stale từ ZIP trước.

if ACQUIRED_DIR.exists():
    shutil.rmtree(ACQUIRED_DIR)

ACQUIRED_DIR.mkdir(parents=True, exist_ok=True)

acquisition_rows = []
seen_filenames = set()

print("\n[INFO] Đang xây dựng acquired zone...")

for sequence_number, source_mat_path in enumerate(
    extracted_raw_mat_files,
    start=1,
):
    canonical_filename = source_mat_path.name

    if canonical_filename in seen_filenames:
        raise RuntimeError(
            "ACQUISITION GATE FAILED: Phát hiện trùng filename "
            "khi flatten raw MAT files:\n"
            f"{canonical_filename}"
        )

    seen_filenames.add(canonical_filename)

    acquired_path = ACQUIRED_DIR / canonical_filename

    shutil.copy2(
        source_mat_path,
        acquired_path,
    )

    source_relative_path = source_mat_path.relative_to(
        EXTRACTED_DIR
    )

    file_size_bytes = acquired_path.stat().st_size

    if file_size_bytes <= 0:
        raise RuntimeError(
            f"Acquired MAT có kích thước bằng 0: {acquired_path}"
        )

    file_sha256 = sha256_file(acquired_path)

    subject_id = canonical_filename[:-len("_raw.mat")]

    acquisition_rows.append(
        {
            "sequence_number": sequence_number,
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "subject_id": subject_id,
            "filename": canonical_filename,
            "source_relative_path": str(source_relative_path),
            "acquired_relative_path": str(
                acquired_path.relative_to(RUNTIME_ROOT)
            ),
            "size_bytes": file_size_bytes,
            "sha256": file_sha256,
            "training_allowed": TRAINING_ALLOWED,
        }
    )


# ============================================================
# 16. Write acquisition manifest CSV
# ============================================================

manifest_fieldnames = [
    "sequence_number",
    "dataset_id",
    "dataset_version",
    "subject_id",
    "filename",
    "source_relative_path",
    "acquired_relative_path",
    "size_bytes",
    "sha256",
    "training_allowed",
]

with ACQUISITION_MANIFEST_PATH.open(
    "w",
    newline="",
    encoding="utf-8",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=manifest_fieldnames,
    )

    writer.writeheader()
    writer.writerows(acquisition_rows)


# ============================================================
# 17. Write extraction marker
# ============================================================

extraction_state = {
    "schema_version": "extraction-state.v1",
    "created_at_utc": utc_now_iso(),
    "dataset_id": DATASET_ID,
    "dataset_version": DATASET_VERSION,
    "source_zip_name": SOURCE_ZIP_NAME,
    "source_zip_sha256": source_zip_sha256,
    "zip_entry_count": len(zip_members),
    "mat_file_count": len(extracted_mat_files),
    "raw_mat_file_count": len(extracted_raw_mat_files),
}

write_json(
    extraction_state,
    EXTRACTION_MARKER_PATH,
)


# ============================================================
# 18. Write acquisition provenance JSON
# ============================================================

provenance = {
    "schema_version": "acquisition-provenance.v1",
    "created_at_utc": utc_now_iso(),
    "operation": "stage_drive_zip_extract_and_acquire_raw_mat",
    "dataset": {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "dataset_slug": DATASET_SLUG,
    },
    "governance": {
        "training_allowed": TRAINING_ALLOWED,
        "notebook_scope": "ETL_only",
    },
    "source": {
        "storage": "google_drive",
        "zip_path": str(SOURCE_ZIP_PATH),
        "zip_name": SOURCE_ZIP_NAME,
        "size_bytes": source_size_bytes,
        "sha256": source_zip_sha256,
    },
    "runtime": {
        "root": str(RUNTIME_ROOT),
        "runtime_zip_path": str(RUNTIME_ZIP_PATH),
        "extracted_dir": str(EXTRACTED_DIR),
        "acquired_dir": str(ACQUIRED_DIR),
    },
    "counts": {
        "zip_entries": len(zip_members),
        "zip_mat_entries": len(zip_mat_members),
        "zip_raw_mat_entries": len(zip_raw_mat_members),
        "extracted_mat_files": len(extracted_mat_files),
        "acquired_raw_mat_files": len(acquisition_rows),
    },
    "artifacts": {
        "acquisition_manifest": str(
            ACQUISITION_MANIFEST_PATH
        ),
        "extraction_marker": str(
            EXTRACTION_MARKER_PATH
        ),
    },
}

write_json(
    provenance,
    PROVENANCE_PATH,
)


# ============================================================
# 19. Persist manifests back to Google Drive
# ============================================================

drive_manifest_csv = (
    DRIVE_MANIFEST_DIR / ACQUISITION_MANIFEST_PATH.name
)

drive_provenance_json = (
    DRIVE_MANIFEST_DIR / PROVENANCE_PATH.name
)

shutil.copy2(
    ACQUISITION_MANIFEST_PATH,
    drive_manifest_csv,
)

shutil.copy2(
    PROVENANCE_PATH,
    drive_provenance_json,
)


# ============================================================
# 20. Final validation gate
# ============================================================

local_raw_mat_files = sorted(
    ACQUIRED_DIR.glob("*_raw.mat"),
    key=raw_mat_sort_key,
)

if len(local_raw_mat_files) != len(extracted_raw_mat_files):
    raise RuntimeError(
        "FINAL ACQUISITION GATE FAILED.\n"
        f"Extracted raw MAT: {len(extracted_raw_mat_files)}\n"
        f"Acquired raw MAT : {len(local_raw_mat_files)}"
    )

if len(acquisition_rows) != len(local_raw_mat_files):
    raise RuntimeError(
        "FINAL MANIFEST GATE FAILED.\n"
        f"Manifest rows    : {len(acquisition_rows)}\n"
        f"Acquired raw MAT : {len(local_raw_mat_files)}"
    )

manifest_filename_set = {
    row["filename"]
    for row in acquisition_rows
}

local_filename_set = {
    path.name
    for path in local_raw_mat_files
}

if manifest_filename_set != local_filename_set:
    raise RuntimeError(
        "FINAL MANIFEST GATE FAILED: "
        "Danh sách filename trong manifest "
        "không khớp acquired directory."
    )


# ============================================================
# 21. Summary
# ============================================================

total_acquired_bytes = sum(
    path.stat().st_size
    for path in local_raw_mat_files
)

print("\n" + "=" * 78)
print("[CELL 3 SUMMARY]")
print("=" * 78)

print(f"Dataset ID          : {DATASET_ID}")
print(f"Dataset version     : {DATASET_VERSION}")
print(f"Source ZIP          : {SOURCE_ZIP_PATH}")
print(f"Source ZIP SHA-256  : {source_zip_sha256}")
print(f"Runtime ZIP         : {RUNTIME_ZIP_PATH}")
print(f"ZIP entries         : {len(zip_members)}")
print(f"MAT entries         : {len(zip_mat_members)}")
print(f"Raw MAT entries     : {len(zip_raw_mat_members)}")
print(f"Acquired raw MAT    : {len(local_raw_mat_files)}")

print(
    f"Acquired total size : "
    f"{total_acquired_bytes / 1024**2:.2f} MB"
)

print(f"Acquired directory  : {ACQUIRED_DIR}")
print(f"Runtime manifest    : {ACQUISITION_MANIFEST_PATH}")
print(f"Drive manifest      : {drive_manifest_csv}")
print(f"Training allowed    : {TRAINING_ALLOWED}")

print("\n[INFO] Một số raw MAT files đầu tiên:")

for path in local_raw_mat_files[:10]:
    print(
        f"  - {path.name:<30} "
        f"{path.stat().st_size / 1024**2:>10.2f} MB"
    )

print("\n" + "=" * 78)
print(
    "[PASS] CELL 3 hoàn tất: ZIP đã được stage, validate, "
    "extract và raw MAT files đã được đưa vào acquired zone."
)
print(
    "[NEXT] Có thể chuyển sang CELL 4: "
    "inspect cấu trúc nội bộ của MAT files."
)
print("=" * 78)

# %%
# === CELL 4: Build local MAT catalog and inspect MAT structures ===

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import scipy.io


# ============================================================
# 1. Governance
# ============================================================

TRAINING_ALLOWED = False

assert TRAINING_ALLOWED is False, (
    "Notebook này chỉ thực hiện ETL. "
    "Không được phép train model."
)


# ============================================================
# 2. Runtime paths
# ============================================================

DATASET_ID = "ckwc76xr2z"
DATASET_VERSION = 2
DATASET_SLUG = "mendeley-4channel-hand-gesture-v2"

RUNTIME_ROOT = Path("/content/data") / DATASET_SLUG
ACQUIRED_DIR = RUNTIME_ROOT / "acquired"
MANIFEST_DIR = RUNTIME_ROOT / "manifests"
LOG_DIR = RUNTIME_ROOT / "logs"

DRIVE_ROOT = (
    Path("/content/drive/MyDrive/MyoLab-AI-data")
    / DATASET_SLUG
)
DRIVE_MANIFEST_DIR = DRIVE_ROOT / "manifests"

MAT_CATALOG_CSV = MANIFEST_DIR / "raw-mat-catalog.csv"
MAT_STRUCTURE_CSV = MANIFEST_DIR / "mat-structure-inventory.csv"
MAT_STRUCTURE_JSON = MANIFEST_DIR / "mat-structure-summary.json"

EXPECTED_RAW_MAT_COUNT = 40

# Không giới hạn 36 subject.
# Cell 4 phải inspect toàn bộ 40 file.
MAX_SUBJECTS = None


# ============================================================
# 3. Create directories
# ============================================================

for directory in [
    MANIFEST_DIR,
    LOG_DIR,
    DRIVE_MANIFEST_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# 4. Helpers
# ============================================================

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Tính SHA-256 theo từng chunk.
    """

    digest = hashlib.sha256()

    with path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def subject_id_from_filename(filename: str) -> str:
    """
    Trích subject ID từ filename dạng '<subject>_raw.mat'.
    """

    suffix = "_raw.mat"

    if not filename.lower().endswith(suffix):
        raise ValueError(
            f"Không phải raw MAT filename hợp lệ: {filename}"
        )

    return filename[:-len(suffix)]


def subject_sort_key(subject_id: str):
    """
    Sắp xếp subject ID theo số nếu có thể.
    """

    if subject_id.isdigit():
        return 0, int(subject_id)

    return 1, subject_id.lower()


def normalize_shape(shape: tuple[int, ...]) -> str:
    """
    Chuyển shape tuple thành chuỗi dễ lưu CSV.
    """

    return "x".join(str(dim) for dim in shape)


def safe_python_scalar(value: Any) -> Any:
    """
    Chuyển NumPy scalar sang Python scalar để ghi JSON.
    """

    if isinstance(value, np.generic):
        return value.item()

    return value


def human_readable_bytes(size_bytes: int) -> str:
    """
    Hiển thị kích thước file.
    """

    value = float(size_bytes)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0:
            return f"{value:.2f} {unit}"

        value /= 1024.0

    return f"{value:.2f} PB"


# ============================================================
# 5. Input gate
# ============================================================

print("=" * 80)
print("[CELL 4] BUILD MAT CATALOG AND INSPECT MAT STRUCTURE")
print("=" * 80)

if not ACQUIRED_DIR.exists():
    raise FileNotFoundError(
        "Không tìm thấy acquired directory.\n"
        f"Expected: {ACQUIRED_DIR}\n"
        "Hãy chạy CELL 3 trước."
    )

raw_mat_paths = sorted(
    ACQUIRED_DIR.glob("*_raw.mat"),
    key=lambda path: subject_sort_key(
        subject_id_from_filename(path.name)
    ),
)

if not raw_mat_paths:
    raise FileNotFoundError(
        f"Không tìm thấy '*_raw.mat' trong:\n{ACQUIRED_DIR}"
    )

print(f"[INFO] Acquired directory : {ACQUIRED_DIR}")
print(f"[INFO] Raw MAT discovered  : {len(raw_mat_paths)}")


# ============================================================
# 6. Validate subject IDs and filenames
# ============================================================

subject_ids = [
    subject_id_from_filename(path.name)
    for path in raw_mat_paths
]

duplicate_subject_ids = [
    subject_id
    for subject_id, count in Counter(subject_ids).items()
    if count > 1
]

if duplicate_subject_ids:
    raise RuntimeError(
        "Phát hiện subject ID bị trùng:\n"
        + "\n".join(duplicate_subject_ids)
    )

numeric_subject_ids = [
    int(subject_id)
    for subject_id in subject_ids
    if subject_id.isdigit()
]

if len(numeric_subject_ids) == len(subject_ids):
    expected_subject_ids = set(range(1, EXPECTED_RAW_MAT_COUNT + 1))
    actual_subject_ids = set(numeric_subject_ids)

    missing_subject_ids = sorted(
        expected_subject_ids - actual_subject_ids
    )

    unexpected_subject_ids = sorted(
        actual_subject_ids - expected_subject_ids
    )

    if missing_subject_ids:
        raise RuntimeError(
            "Thiếu subject ID mong đợi: "
            f"{missing_subject_ids}"
        )

    if unexpected_subject_ids:
        raise RuntimeError(
            "Có subject ID ngoài phạm vi mong đợi: "
            f"{unexpected_subject_ids}"
        )


if len(raw_mat_paths) != EXPECTED_RAW_MAT_COUNT:
    raise RuntimeError(
        "RAW MAT COUNT GATE FAILED.\n"
        f"Expected: {EXPECTED_RAW_MAT_COUNT}\n"
        f"Actual  : {len(raw_mat_paths)}"
    )

print(
    f"[PASS] Subject gate đạt: "
    f"{len(subject_ids)} subject duy nhất."
)


# ============================================================
# 7. Build canonical local catalog
# ============================================================

catalog_rows = []

print("\n[INFO] Đang tính checksum cho 40 raw MAT files...")

for sequence_number, mat_path in enumerate(
    raw_mat_paths,
    start=1,
):
    subject_id = subject_id_from_filename(mat_path.name)

    size_bytes = mat_path.stat().st_size

    if size_bytes <= 0:
        raise RuntimeError(
            f"File MAT có kích thước bằng 0: {mat_path}"
        )

    checksum = sha256_file(mat_path)

    catalog_rows.append(
        {
            "sequence_number": sequence_number,
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "subject_id": subject_id,
            "filename": mat_path.name,
            "size_bytes": size_bytes,
            "size_human": human_readable_bytes(size_bytes),
            "sha256": checksum,
            "local_path": str(mat_path.resolve()),
            "source_mode": "runtime_acquired",
            "training_allowed": TRAINING_ALLOWED,
        }
    )

    print(
        f"  [{sequence_number:02d}/{len(raw_mat_paths):02d}] "
        f"{mat_path.name:<15} "
        f"{human_readable_bytes(size_bytes):>12}"
    )


catalog_fieldnames = [
    "sequence_number",
    "dataset_id",
    "dataset_version",
    "subject_id",
    "filename",
    "size_bytes",
    "size_human",
    "sha256",
    "local_path",
    "source_mode",
    "training_allowed",
]

with MAT_CATALOG_CSV.open(
    "w",
    newline="",
    encoding="utf-8",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=catalog_fieldnames,
    )
    writer.writeheader()
    writer.writerows(catalog_rows)

print(f"\n[OK] Raw MAT catalog: {MAT_CATALOG_CSV}")


# ============================================================
# 8. Inspect MAT headers without loading full arrays
# ============================================================

print(
    "\n[INFO] Đang inspect MAT headers bằng "
    "scipy.io.whosmat()..."
)

structure_rows = []
header_errors = []

for subject_index, catalog_item in enumerate(
    catalog_rows,
    start=1,
):
    subject_id = catalog_item["subject_id"]
    mat_path = Path(catalog_item["local_path"])

    try:
        variables = scipy.io.whosmat(mat_path)

    except Exception as exc:
        header_errors.append(
            {
                "subject_id": subject_id,
                "filename": mat_path.name,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )

        print(
            f"  [FAILED] {mat_path.name}: "
            f"{type(exc).__name__}: {exc}"
        )
        continue

    if not variables:
        header_errors.append(
            {
                "subject_id": subject_id,
                "filename": mat_path.name,
                "error_type": "EmptyMatFile",
                "error": "scipy.io.whosmat() không trả về variable nào.",
            }
        )
        continue

    print(
        f"  [{subject_index:02d}/{len(catalog_rows):02d}] "
        f"{mat_path.name}: {len(variables)} variables"
    )

    for variable_name, variable_shape, variable_class in variables:
        structure_rows.append(
            {
                "dataset_id": DATASET_ID,
                "dataset_version": DATASET_VERSION,
                "subject_id": subject_id,
                "filename": mat_path.name,
                "variable_name": variable_name,
                "variable_shape": normalize_shape(variable_shape),
                "ndim": len(variable_shape),
                "matlab_class": variable_class,
                "element_count": int(
                    np.prod(variable_shape, dtype=np.int64)
                ),
            }
        )

        print(
            f"      - {variable_name:<30} "
            f"shape={str(variable_shape):<20} "
            f"class={variable_class}"
        )


if header_errors:
    print("\n[HEADER ERRORS]")

    for error in header_errors:
        print(
            f"- {error['filename']}: "
            f"{error['error_type']}: {error['error']}"
        )

    raise RuntimeError(
        f"MAT HEADER GATE FAILED: "
        f"{len(header_errors)} file không đọc được header."
    )


# ============================================================
# 9. Write structure inventory CSV
# ============================================================

structure_fieldnames = [
    "dataset_id",
    "dataset_version",
    "subject_id",
    "filename",
    "variable_name",
    "variable_shape",
    "ndim",
    "matlab_class",
    "element_count",
]

with MAT_STRUCTURE_CSV.open(
    "w",
    newline="",
    encoding="utf-8",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=structure_fieldnames,
    )
    writer.writeheader()
    writer.writerows(structure_rows)

print(f"\n[OK] MAT structure inventory: {MAT_STRUCTURE_CSV}")


# ============================================================
# 10. Compare variable signatures across subjects
# ============================================================

signatures_by_subject = defaultdict(list)

for row in structure_rows:
    signatures_by_subject[row["subject_id"]].append(
        (
            row["variable_name"],
            row["variable_shape"],
            row["matlab_class"],
        )
    )

normalized_signatures = {}

for subject_id, signature_items in signatures_by_subject.items():
    normalized_signatures[subject_id] = tuple(
        sorted(signature_items)
    )

signature_groups = defaultdict(list)

for subject_id, signature in normalized_signatures.items():
    signature_groups[signature].append(subject_id)

print("\n" + "-" * 80)
print("[STRUCTURE CONSISTENCY]")
print("-" * 80)

print(
    f"Unique MAT structure signatures: "
    f"{len(signature_groups)}"
)

for group_index, (signature, grouped_subjects) in enumerate(
    signature_groups.items(),
    start=1,
):
    grouped_subjects = sorted(
        grouped_subjects,
        key=subject_sort_key,
    )

    print(
        f"\nSignature group {group_index}: "
        f"{len(grouped_subjects)} subjects"
    )

    print(f"Subjects: {grouped_subjects}")

    for variable_name, variable_shape, matlab_class in signature:
        print(
            f"  - {variable_name}: "
            f"shape={variable_shape}, "
            f"class={matlab_class}"
        )


# ============================================================
# 11. Load one representative MAT file
# ============================================================

sample_item = catalog_rows[0]
sample_path = Path(sample_item["local_path"])

print("\n" + "-" * 80)
print("[REPRESENTATIVE MAT SAMPLE]")
print("-" * 80)

print(f"Sample subject : {sample_item['subject_id']}")
print(f"Sample file    : {sample_path}")
print(
    f"Sample size    : "
    f"{human_readable_bytes(sample_path.stat().st_size)}"
)

try:
    sample_mat = scipy.io.loadmat(
        sample_path,
        squeeze_me=False,
        struct_as_record=False,
    )

except NotImplementedError as exc:
    raise RuntimeError(
        "MAT file có thể dùng định dạng MATLAB v7.3/HDF5. "
        "scipy.io.loadmat không hỗ trợ trực tiếp định dạng này. "
        "Cần inspect bằng h5py ở Cell tiếp theo."
    ) from exc

except Exception as exc:
    raise RuntimeError(
        "Không thể load representative MAT file:\n"
        f"{sample_path}\n"
        f"{type(exc).__name__}: {exc}"
    ) from exc


user_variable_names = sorted(
    key
    for key in sample_mat.keys()
    if not key.startswith("__")
)

if not user_variable_names:
    raise RuntimeError(
        "Representative MAT không có user variable."
    )

print("\n[INFO] MATLAB metadata:")

for metadata_key in [
    "__header__",
    "__version__",
    "__globals__",
]:
    metadata_value = sample_mat.get(metadata_key)

    if metadata_key == "__header__" and isinstance(
        metadata_value,
        bytes,
    ):
        metadata_value = metadata_value.decode(
            "utf-8",
            errors="replace",
        )

    print(f"  {metadata_key}: {metadata_value}")


print("\n[INFO] User variables:")

sample_variable_details = []

for variable_name in user_variable_names:
    value = sample_mat[variable_name]

    detail = {
        "variable_name": variable_name,
        "python_type": type(value).__name__,
        "numpy_dtype": (
            str(value.dtype)
            if isinstance(value, np.ndarray)
            else None
        ),
        "shape": (
            list(value.shape)
            if isinstance(value, np.ndarray)
            else None
        ),
        "ndim": (
            int(value.ndim)
            if isinstance(value, np.ndarray)
            else None
        ),
        "size": (
            int(value.size)
            if isinstance(value, np.ndarray)
            else None
        ),
    }

    sample_variable_details.append(detail)

    print(f"\n  Variable: {variable_name}")
    print(f"    Python type : {detail['python_type']}")
    print(f"    NumPy dtype : {detail['numpy_dtype']}")
    print(f"    Shape       : {detail['shape']}")
    print(f"    N-dimensional: {detail['ndim']}")
    print(f"    Element count: {detail['size']}")

    if (
        isinstance(value, np.ndarray)
        and np.issubdtype(value.dtype, np.number)
        and value.size > 0
    ):
        finite_mask = np.isfinite(value)
        finite_count = int(finite_mask.sum())
        nonfinite_count = int(value.size - finite_count)

        print(f"    Finite count   : {finite_count}")
        print(f"    Nonfinite count: {nonfinite_count}")

        if finite_count > 0:
            finite_values = value[finite_mask]

            print(
                f"    Min          : "
                f"{safe_python_scalar(np.min(finite_values))}"
            )
            print(
                f"    Max          : "
                f"{safe_python_scalar(np.max(finite_values))}"
            )
            print(
                f"    Mean         : "
                f"{safe_python_scalar(np.mean(finite_values))}"
            )


# ============================================================
# 12. Build structure summary JSON
# ============================================================

signature_group_payload = []

for group_index, (signature, grouped_subjects) in enumerate(
    signature_groups.items(),
    start=1,
):
    signature_group_payload.append(
        {
            "signature_group": group_index,
            "subject_count": len(grouped_subjects),
            "subject_ids": sorted(
                grouped_subjects,
                key=subject_sort_key,
            ),
            "variables": [
                {
                    "variable_name": variable_name,
                    "variable_shape": variable_shape,
                    "matlab_class": matlab_class,
                }
                for (
                    variable_name,
                    variable_shape,
                    matlab_class,
                ) in signature
            ],
        }
    )


structure_summary = {
    "schema_version": "mat-structure-summary.v1",
    "created_at_utc": utc_now_iso(),
    "dataset": {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "dataset_slug": DATASET_SLUG,
    },
    "governance": {
        "training_allowed": TRAINING_ALLOWED,
        "notebook_scope": "ETL_only",
    },
    "environment": {
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
    },
    "counts": {
        "raw_mat_files": len(catalog_rows),
        "structure_rows": len(structure_rows),
        "unique_structure_signatures": len(signature_groups),
        "header_errors": len(header_errors),
    },
    "representative_sample": {
        "subject_id": sample_item["subject_id"],
        "filename": sample_item["filename"],
        "sha256": sample_item["sha256"],
        "matlab_header": str(
            sample_mat.get("__header__")
        ),
        "matlab_version": str(
            sample_mat.get("__version__")
        ),
        "variables": sample_variable_details,
    },
    "signature_groups": signature_group_payload,
    "artifacts": {
        "raw_mat_catalog_csv": str(MAT_CATALOG_CSV),
        "mat_structure_inventory_csv": str(MAT_STRUCTURE_CSV),
    },
}

with MAT_STRUCTURE_JSON.open(
    "w",
    encoding="utf-8",
) as file_obj:
    json.dump(
        structure_summary,
        file_obj,
        ensure_ascii=False,
        indent=2,
    )

print(f"\n[OK] MAT structure summary: {MAT_STRUCTURE_JSON}")


# ============================================================
# 13. Persist manifests to Google Drive
# ============================================================

drive_catalog_csv = DRIVE_MANIFEST_DIR / MAT_CATALOG_CSV.name
drive_structure_csv = DRIVE_MANIFEST_DIR / MAT_STRUCTURE_CSV.name
drive_structure_json = DRIVE_MANIFEST_DIR / MAT_STRUCTURE_JSON.name

import shutil

shutil.copy2(
    MAT_CATALOG_CSV,
    drive_catalog_csv,
)

shutil.copy2(
    MAT_STRUCTURE_CSV,
    drive_structure_csv,
)

shutil.copy2(
    MAT_STRUCTURE_JSON,
    drive_structure_json,
)

print("\n[INFO] Persisted manifests to Google Drive:")
print(f"  - {drive_catalog_csv}")
print(f"  - {drive_structure_csv}")
print(f"  - {drive_structure_json}")


# ============================================================
# 14. Final validation gate
# ============================================================

assert len(catalog_rows) == EXPECTED_RAW_MAT_COUNT, (
    "Catalog không có đúng 40 subject."
)

assert len(signatures_by_subject) == EXPECTED_RAW_MAT_COUNT, (
    "Không phải tất cả subject đều có structure inventory."
)

assert not header_errors, (
    "Có MAT file không đọc được header."
)

assert MAT_CATALOG_CSV.exists(), (
    "Thiếu raw-mat-catalog.csv."
)

assert MAT_STRUCTURE_CSV.exists(), (
    "Thiếu mat-structure-inventory.csv."
)

assert MAT_STRUCTURE_JSON.exists(), (
    "Thiếu mat-structure-summary.json."
)


# ============================================================
# 15. Summary
# ============================================================

print("\n" + "=" * 80)
print("[CELL 4 SUMMARY]")
print("=" * 80)

print(f"Raw MAT files             : {len(catalog_rows)}")
print(f"Subjects                  : {subject_ids}")
print(f"Structure inventory rows  : {len(structure_rows)}")
print(f"Unique structure patterns : {len(signature_groups)}")
print(f"Header read errors        : {len(header_errors)}")
print(f"Representative subject    : {sample_item['subject_id']}")
print(f"Representative file       : {sample_item['filename']}")
print(f"User variables            : {user_variable_names}")
print(f"Runtime catalog           : {MAT_CATALOG_CSV}")
print(f"Runtime structure CSV     : {MAT_STRUCTURE_CSV}")
print(f"Runtime structure JSON    : {MAT_STRUCTURE_JSON}")
print(f"Training allowed          : {TRAINING_ALLOWED}")

print("\n" + "=" * 80)
print(
    "[PASS] CELL 4 hoàn tất: 40 raw MAT files đã được catalog "
    "và inspect cấu trúc."
)
print(
    "[NEXT] Phân tích output của CELL 4 để xác định "
    "canonical parser cho dữ liệu sEMG."
)
print("=" * 80)

# %% [markdown]
# ## 2. Preflight 40 MAT, metadata, paths và frozen contracts.

# %%
# === CELL 5: Preflight, paths, governance and frozen contracts ===
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import shutil
import sys
import time
import warnings
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import scipy
import scipy.io
import scipy.stats


# -----------------------------------------------------------------------------
# 1. Governance
# -----------------------------------------------------------------------------

TRAINING_ALLOWED = False
MODEL_FITTING_ALLOWED = False
SCALER_FITTING_ALLOWED = False
TEST_SIGNAL_ACCESS_ALLOWED = False
TEST_SET_OPENED = False
POOLED_TRAINING_ALLOWED = False

assert TRAINING_ALLOWED is False
assert MODEL_FITTING_ALLOWED is False
assert SCALER_FITTING_ALLOWED is False
assert TEST_SIGNAL_ACCESS_ALLOWED is False
assert TEST_SET_OPENED is False
assert POOLED_TRAINING_ALLOWED is False


# -----------------------------------------------------------------------------
# 2. Dataset and storage paths
# -----------------------------------------------------------------------------

DATASET_ID = "mendeley-4channel-hand-gesture-v2"
DATASET_SOURCE_ID = "ckwc76xr2z"
DATASET_VERSION = 2
DATASET_VIEW_ID = "mendeley_core4_primary_v1"

RUNTIME_ROOT = Path("/content/data") / DATASET_ID
ACQUIRED_DIR = RUNTIME_ROOT / "acquired"
INDEX_DIR = RUNTIME_ROOT / "indexes"
FEATURE_DIR = RUNTIME_ROOT / "features"
MATRIX_DIR = RUNTIME_ROOT / "matrices"
MANIFEST_DIR = RUNTIME_ROOT / "manifests"
LOG_DIR = RUNTIME_ROOT / "logs"
CACHE_DIR = RUNTIME_ROOT / "cache"

DRIVE_ROOT = (
    Path("/content/drive/MyDrive/MyoLab-AI-data")
    / DATASET_ID
)
DRIVE_MANIFEST_DIR = DRIVE_ROOT / "manifests"
DRIVE_OUTPUT_DIR = DRIVE_ROOT / "outputs"

for directory in [
    INDEX_DIR,
    FEATURE_DIR,
    MATRIX_DIR,
    MANIFEST_DIR,
    LOG_DIR,
    CACHE_DIR,
    DRIVE_MANIFEST_DIR,
    DRIVE_OUTPUT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# 3. Frozen segmentation, ontology, channel and feature contracts
# -----------------------------------------------------------------------------

EXPECTED_SUBJECT_COUNT = 40
EXPECTED_RAW_SHAPE = (1_280_000, 4)
EXPECTED_FS_HZ = 2_000
EXPECTED_DURATION_SECONDS = 640

SEGMENTATION_VERSION = "mendeley-official-timeline-python.v1"
SEGMENTATION_SOURCE = "EMG_gesture_segmentation.m"
SEGMENT_START_OFFSET_SECONDS = 0
SEGMENT_END_OFFSET_SECONDS = 6
SEGMENT_DURATION_SECONDS = (
    SEGMENT_END_OFFSET_SECONDS - SEGMENT_START_OFFSET_SECONDS
)

REPETITION_BASE_SECONDS = (4, 138, 272, 406, 540)

GESTURES = (
    {"gesture_index": 0, "raw_label": "rest",                    "canonical_label": "rest"},
    {"gesture_index": 1, "raw_label": "wrist_extension",         "canonical_label": "wrist_extension"},
    {"gesture_index": 2, "raw_label": "wrist_flexion",           "canonical_label": "wrist_flexion"},
    {"gesture_index": 3, "raw_label": "ulnar_deviation",         "canonical_label": None},
    {"gesture_index": 4, "raw_label": "radial_deviation",        "canonical_label": None},
    {"gesture_index": 5, "raw_label": "grip",                    "canonical_label": "hand_close"},
    {"gesture_index": 6, "raw_label": "abduction_all_fingers",   "canonical_label": None},
    {"gesture_index": 7, "raw_label": "adduction_all_fingers",   "canonical_label": None},
    {"gesture_index": 8, "raw_label": "supination",              "canonical_label": None},
    {"gesture_index": 9, "raw_label": "pronation",               "canonical_label": None},
)

PRIMARY_CLASS_ORDER = (
    "rest",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
)

LABEL_MAPPING_VERSION = "MENDELEY_4CH_GESTURE.taskA.v1"
SPLIT_VERSION = "mendeley-subject-holdout.v1"
WINDOWING_VERSION = "day30-windowing-200ms-100ms.v1"
PREPROCESSING_POLICY_ID = "per-record-channel-mean-v1"
PRIMARY_CHANNEL_POLICY_ID = "mendeley-ch123-primary-v1"
CH4_SENSITIVITY_POLICY_ID = "mendeley-ch1234-sensitivity-v1"

CANONICAL_CHANNEL_IDS = ("CH1", "CH2", "CH3", "CH4")
PRIMARY_CHANNEL_IDS = ("CH1", "CH2", "CH3")
PRIMARY_CHANNEL_INDICES = (0, 1, 2)

WINDOW_MS = 200
HOP_MS = 100

FEATURE_SET_VERSION = "feature-set-14.v1.0.0"
FEATURE_ORDER = (
    "rms",
    "mav",
    "skewness_unbiased",
    "kurtosis_fisher_unbiased",
    "max_signed",
    "min_signed",
    "std_sample_ddof1",
    "mean",
    "spectral_min_power",
    "spectral_max_power",
    "spectral_std_power_ddof1",
    "mdf_hz",
    "mnf_hz",
    "spectral_entropy_bits",
)

TD8_FEATURES = FEATURE_ORDER[:8]
SP6_FEATURES = FEATURE_ORDER[8:]
NO_MOMENTS12_FEATURES = tuple(
    feature
    for feature in FEATURE_ORDER
    if feature not in {
        "skewness_unbiased",
        "kurtosis_fisher_unbiased",
    }
)


# -----------------------------------------------------------------------------
# 4. Artifact paths
# -----------------------------------------------------------------------------

CELL5_PREFLIGHT_JSON = MANIFEST_DIR / "cell5-preflight.json"
SUBJECT_SPLIT_CSV = MANIFEST_DIR / "subject-split-manifest.csv"
SUBJECT_SPLIT_JSON = MANIFEST_DIR / "subject-split-manifest.json"
ALL_SEGMENTS_CSV = INDEX_DIR / "all-segments-index.csv"
PRIMARY_METADATA_CSV = INDEX_DIR / "metadata-index-mendeley-primary.csv"
WINDOW_INDEX_CSV_GZ = INDEX_DIR / "window-index-mendeley-primary.csv.gz"

SUBJECT_FEATURE_CACHE_DIR = CACHE_DIR / "day31-subject-features"
SUBJECT_FEATURE_TABLE_DIR = FEATURE_DIR / "by-subject"
SUBJECT_EXCLUSION_DIR = FEATURE_DIR / "exclusions-by-subject"

COMBINED_FEATURE_TABLE_CSV_GZ = (
    FEATURE_DIR / "day31-feature-table-channel-wide.csv.gz"
)
COMBINED_EXCLUSION_CSV = (
    FEATURE_DIR / "day31-feature-exclusion-report.csv"
)

FINAL_NPZ = MATRIX_DIR / "day31-mendeley-primary-fall14.npz"
COLUMN_MANIFEST_JSON = MATRIX_DIR / "day31-feature-column-manifest.json"
DAY31_EVIDENCE_JSON = MANIFEST_DIR / "day31-colab-etl-evidence.json"
FINAL_GATE_JSON = MANIFEST_DIR / "day31-final-gate.json"

for directory in [
    SUBJECT_FEATURE_CACHE_DIR,
    SUBJECT_FEATURE_TABLE_DIR,
    SUBJECT_EXCLUSION_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# 5. Helpers
# -----------------------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def round_half_up(value: float) -> int:
    return int(
        Decimal(str(value)).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def write_json(payload: Any, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.unlink(missing_ok=True)
    shutil.copy2(source, temporary)
    if temporary.stat().st_size != source.stat().st_size:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"Atomic copy size mismatch: {source} -> {destination}"
        )
    temporary.replace(destination)


def subject_id_from_filename(filename: str) -> str:
    suffix = "_raw.mat"
    if not filename.lower().endswith(suffix):
        raise ValueError(f"Invalid raw MAT filename: {filename}")
    return filename[:-len(suffix)]


def subject_sort_key(subject_id: str):
    return (
        (0, int(subject_id))
        if str(subject_id).isdigit()
        else (1, str(subject_id).lower())
    )


def matlab_text_list(value: Any) -> list[str]:
    array = np.asarray(value)
    if array.ndim == 0:
        return [str(array.item())]
    return [str(item) for item in array.reshape(-1).tolist()]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


# -----------------------------------------------------------------------------
# 6. Input gates
# -----------------------------------------------------------------------------

print("=" * 86)
print("[CELL 5] PREFLIGHT AND CONTRACT FREEZE")
print("=" * 86)

if not Path("/content/drive/MyDrive").exists():
    raise RuntimeError(
        "Google Drive chưa được mount. "
        "Hãy mount Drive trước khi chạy CELL 5."
    )

if not ACQUIRED_DIR.exists():
    raise FileNotFoundError(
        f"Không tìm thấy acquired directory: {ACQUIRED_DIR}\n"
        "Hãy chạy lại CELL 3."
    )

raw_mat_paths = sorted(
    ACQUIRED_DIR.glob("*_raw.mat"),
    key=lambda path: subject_sort_key(
        subject_id_from_filename(path.name)
    ),
)

if len(raw_mat_paths) != EXPECTED_SUBJECT_COUNT:
    raise RuntimeError(
        "RAW MAT COUNT GATE FAILED.\n"
        f"Expected: {EXPECTED_SUBJECT_COUNT}\n"
        f"Actual  : {len(raw_mat_paths)}"
    )

expected_subject_ids = {str(value) for value in range(1, 41)}
actual_subject_ids = {
    subject_id_from_filename(path.name)
    for path in raw_mat_paths
}

if actual_subject_ids != expected_subject_ids:
    raise RuntimeError(
        "SUBJECT ID GATE FAILED.\n"
        f"Missing   : {sorted(expected_subject_ids - actual_subject_ids)}\n"
        f"Unexpected: {sorted(actual_subject_ids - expected_subject_ids)}"
    )


# Prefer the checksum catalog produced by CELL 4.
raw_catalog_path = MANIFEST_DIR / "raw-mat-catalog.csv"
checksum_by_filename: dict[str, str] = {}

if raw_catalog_path.exists():
    for row in read_csv_rows(raw_catalog_path):
        checksum_by_filename[row["filename"]] = row["sha256"]

subject_catalog: list[dict[str, Any]] = []
metadata_signatures: Counter = Counter()

print("[INFO] Validating MAT metadata for 40 subjects...")

for index, mat_path in enumerate(raw_mat_paths, start=1):
    subject_id = subject_id_from_filename(mat_path.name)

    variables = scipy.io.whosmat(mat_path)
    variable_lookup = {
        name: (tuple(shape), matlab_class)
        for name, shape, matlab_class in variables
    }

    required_variables = {
        "data",
        "fs",
        "iD",
        "isi",
        "isi_units",
        "labels",
        "start_sample",
        "units",
    }

    missing_variables = required_variables - set(variable_lookup)
    if missing_variables:
        raise RuntimeError(
            f"{mat_path.name} missing variables: "
            f"{sorted(missing_variables)}"
        )

    if tuple(variable_lookup["data"][0]) != EXPECTED_RAW_SHAPE:
        raise RuntimeError(
            f"{mat_path.name}: unexpected data shape "
            f"{variable_lookup['data'][0]}"
        )

    metadata = scipy.io.loadmat(
        mat_path,
        variable_names=[
            "fs",
            "iD",
            "isi",
            "isi_units",
            "labels",
            "start_sample",
            "units",
        ],
        squeeze_me=True,
        struct_as_record=False,
    )

    fs_hz = int(np.asarray(metadata["fs"]).reshape(-1)[0])
    mat_subject_id = str(
        int(np.asarray(metadata["iD"]).reshape(-1)[0])
    )
    isi = float(np.asarray(metadata["isi"]).reshape(-1)[0])
    start_sample = int(
        np.asarray(metadata["start_sample"]).reshape(-1)[0]
    )
    isi_units = matlab_text_list(metadata["isi_units"])
    source_channel_labels = matlab_text_list(metadata["labels"])
    source_units = matlab_text_list(metadata["units"])

    if fs_hz != EXPECTED_FS_HZ:
        raise RuntimeError(
            f"{mat_path.name}: fs={fs_hz}, expected {EXPECTED_FS_HZ}"
        )

    if mat_subject_id != subject_id:
        raise RuntimeError(
            f"{mat_path.name}: filename subject={subject_id}, "
            f"MAT iD={mat_subject_id}"
        )

    if start_sample != 0:
        raise RuntimeError(
            f"{mat_path.name}: start_sample={start_sample}, expected 0"
        )

    if len(source_channel_labels) != 4 or len(source_units) != 4:
        raise RuntimeError(
            f"{mat_path.name}: expected 4 labels/units, got "
            f"{len(source_channel_labels)}/{len(source_units)}"
        )

    source_sha256 = checksum_by_filename.get(mat_path.name)
    if not source_sha256:
        source_sha256 = sha256_file(mat_path)

    signature = (
        fs_hz,
        round(isi, 12),
        tuple(isi_units),
        tuple(source_channel_labels),
        tuple(source_units),
    )
    metadata_signatures[signature] += 1

    subject_catalog.append(
        {
            "subject_id": subject_id,
            "subject_key": f"mendeley-S{int(subject_id):03d}",
            "filename": mat_path.name,
            "mat_path": str(mat_path.resolve()),
            "source_file_sha256": source_sha256,
            "size_bytes": mat_path.stat().st_size,
            "sampling_rate_hz": fs_hz,
            "sample_interval": isi,
            "sample_interval_units": isi_units,
            "source_channel_labels": source_channel_labels,
            "source_units": source_units,
            "n_samples": EXPECTED_RAW_SHAPE[0],
            "n_channels": EXPECTED_RAW_SHAPE[1],
        }
    )

    print(
        f"  [{index:02d}/40] {mat_path.name:<12} "
        f"fs={fs_hz}Hz shape={EXPECTED_RAW_SHAPE}"
    )

if len(metadata_signatures) != 1:
    raise RuntimeError(
        "METADATA CONSISTENCY GATE FAILED: "
        f"{len(metadata_signatures)} signatures found."
    )

window_samples = round_half_up(
    EXPECTED_FS_HZ * WINDOW_MS / 1000.0
)
hop_samples = round_half_up(
    EXPECTED_FS_HZ * HOP_MS / 1000.0
)
segment_samples = EXPECTED_FS_HZ * SEGMENT_DURATION_SECONDS

expected_windows_per_segment = (
    (segment_samples - window_samples) // hop_samples
) + 1

if window_samples != 400 or hop_samples != 200:
    raise RuntimeError(
        "WINDOW SAMPLE GATE FAILED: "
        f"window={window_samples}, hop={hop_samples}"
    )

if expected_windows_per_segment != 59:
    raise RuntimeError(
        "WINDOW COUNT GATE FAILED: "
        f"expected_windows_per_segment={expected_windows_per_segment}"
    )

contract_payload = {
    "dataset_id": DATASET_ID,
    "dataset_source_id": DATASET_SOURCE_ID,
    "dataset_version": DATASET_VERSION,
    "dataset_view_id": DATASET_VIEW_ID,
    "segmentation_version": SEGMENTATION_VERSION,
    "repetition_base_seconds": list(REPETITION_BASE_SECONDS),
    "segment_start_offset_seconds": SEGMENT_START_OFFSET_SECONDS,
    "segment_end_offset_seconds": SEGMENT_END_OFFSET_SECONDS,
    "window_ms": WINDOW_MS,
    "hop_ms": HOP_MS,
    "window_samples": window_samples,
    "hop_samples": hop_samples,
    "expected_windows_per_segment": expected_windows_per_segment,
    "primary_class_order": list(PRIMARY_CLASS_ORDER),
    "primary_channel_ids": list(PRIMARY_CHANNEL_IDS),
    "feature_order": list(FEATURE_ORDER),
    "training_allowed": TRAINING_ALLOWED,
    "model_fitting_allowed": MODEL_FITTING_ALLOWED,
    "test_signal_access_allowed": TEST_SIGNAL_ACCESS_ALLOWED,
}

CONTRACT_HASH = sha256_json(contract_payload)

cell5_preflight = {
    "schema_version": "cell5-preflight.v1",
    "created_at_utc": utc_now_iso(),
    "status": "PASS",
    "contract_hash": CONTRACT_HASH,
    "contract": contract_payload,
    "environment": {
        "python": sys.version,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    },
    "counts": {
        "raw_mat_files": len(subject_catalog),
        "metadata_signatures": len(metadata_signatures),
    },
    "subject_catalog": subject_catalog,
}

write_json(cell5_preflight, CELL5_PREFLIGHT_JSON)
atomic_copy(
    CELL5_PREFLIGHT_JSON,
    DRIVE_MANIFEST_DIR / CELL5_PREFLIGHT_JSON.name,
)

print("\n" + "=" * 86)
print("[CELL 5 SUMMARY]")
print("=" * 86)
print(f"Subjects                    : {len(subject_catalog)}")
print(f"Unique metadata signatures  : {len(metadata_signatures)}")
print(f"Sampling rate               : {EXPECTED_FS_HZ} Hz")
print(f"Raw shape per subject       : {EXPECTED_RAW_SHAPE}")
print(f"Segment length              : {segment_samples} samples")
print(f"Window / hop                : {window_samples} / {hop_samples} samples")
print(f"Windows per segment         : {expected_windows_per_segment}")
print(f"Primary feature dimension   : {len(PRIMARY_CHANNEL_IDS) * len(FEATURE_ORDER)}")
print(f"Contract hash               : {CONTRACT_HASH}")
print(f"Training allowed            : {TRAINING_ALLOWED}")
print("[PASS] CELL 5 hoàn tất.")

# %% [markdown]
# ## 3. Subject split trước segmentation/windowing
#
# Mỗi subject có đủ 5 repetition cho cả 10 gesture, nên primary view có class coverage cân bằng theo subject.  
# CELL 6 tạo holdout `32 train / 8 validation` bằng hash cố định, không dùng random-window split và không tạo test partition.

# %%
# === CELL 6: Deterministic subject-level train/validation split ===

SPLIT_SEED = 3001
VALIDATION_SUBJECT_COUNT = 8


def deterministic_subject_rank(subject_id: str) -> str:
    token = f"{SPLIT_SEED}|{DATASET_ID}|{subject_id}"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


ranked_subjects = sorted(
    [item["subject_id"] for item in subject_catalog],
    key=lambda subject_id: (
        deterministic_subject_rank(subject_id),
        subject_sort_key(subject_id),
    ),
)

validation_subject_ids = set(
    ranked_subjects[:VALIDATION_SUBJECT_COUNT]
)
train_subject_ids = set(ranked_subjects[VALIDATION_SUBJECT_COUNT:])

if train_subject_ids & validation_subject_ids:
    raise RuntimeError("SUBJECT LEAKAGE DETECTED.")

if len(train_subject_ids) != 32 or len(validation_subject_ids) != 8:
    raise RuntimeError(
        "Unexpected split size: "
        f"train={len(train_subject_ids)}, "
        f"validation={len(validation_subject_ids)}"
    )

split_rows = []

for item in sorted(
    subject_catalog,
    key=lambda row: subject_sort_key(row["subject_id"]),
):
    subject_id = item["subject_id"]
    partition = (
        "validation"
        if subject_id in validation_subject_ids
        else "train"
    )

    split_rows.append(
        {
            "dataset_id": DATASET_ID,
            "dataset_view_id": DATASET_VIEW_ID,
            "subject_id": subject_id,
            "subject_key": item["subject_key"],
            "partition": partition,
            "split_version": SPLIT_VERSION,
            "split_seed": SPLIT_SEED,
            "rank_sha256": deterministic_subject_rank(subject_id),
            "source_filename": item["filename"],
            "source_file_sha256": item["source_file_sha256"],
        }
    )

split_fieldnames = list(split_rows[0].keys())

with SUBJECT_SPLIT_CSV.open(
    "w",
    encoding="utf-8",
    newline="",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=split_fieldnames,
    )
    writer.writeheader()
    writer.writerows(split_rows)

split_hash = sha256_json(split_rows)

split_payload = {
    "schema_version": "mendeley-subject-split.v1",
    "created_at_utc": utc_now_iso(),
    "dataset_id": DATASET_ID,
    "dataset_view_id": DATASET_VIEW_ID,
    "split_version": SPLIT_VERSION,
    "split_seed": SPLIT_SEED,
    "split_hash": split_hash,
    "partition_counts": dict(
        Counter(row["partition"] for row in split_rows)
    ),
    "train_subject_ids": sorted(
        train_subject_ids,
        key=subject_sort_key,
    ),
    "validation_subject_ids": sorted(
        validation_subject_ids,
        key=subject_sort_key,
    ),
    "test_subject_ids": [],
    "test_set_opened": TEST_SET_OPENED,
    "training_allowed": TRAINING_ALLOWED,
}

write_json(split_payload, SUBJECT_SPLIT_JSON)

for artifact in [SUBJECT_SPLIT_CSV, SUBJECT_SPLIT_JSON]:
    atomic_copy(
        artifact,
        DRIVE_MANIFEST_DIR / artifact.name,
    )

partition_by_subject = {
    row["subject_id"]: row["partition"]
    for row in split_rows
}

print("=" * 86)
print("[CELL 6 SUMMARY]")
print("=" * 86)
print(
    "Train subjects      :",
    sorted(train_subject_ids, key=subject_sort_key),
)
print(
    "Validation subjects :",
    sorted(validation_subject_ids, key=subject_sort_key),
)
print(f"Split hash          : {split_hash}")
print(f"Test subjects       : 0")
print("[PASS] CELL 6 hoàn tất: subject split không leakage.")

# %% [markdown]
# ##4. Official timeline segmentation → metadata index
#
# Không chia `1_280_000` mẫu thành 10 khối bằng nhau.
#
# Python slice tương đương MATLAB:
#
# ```matlab
# data((start + rep_base + gesture*10)*fs + 1 : ...
#      (rep_base + gesture*10 + end)*fs, :)
# ```
#
# là:
#
# ```python
# data[start_sample:end_sample_exclusive, :]
# ```
#
# với `start_sample = (start + rep_base + gesture*10) * fs`.

# %%
# === CELL 7: Build official segment metadata indexes ===

all_segment_rows: list[dict[str, Any]] = []
primary_segment_rows: list[dict[str, Any]] = []

catalog_by_subject = {
    item["subject_id"]: item
    for item in subject_catalog
}

for subject_id in sorted(
    catalog_by_subject,
    key=subject_sort_key,
):
    subject = catalog_by_subject[subject_id]
    partition = partition_by_subject[subject_id]
    fs_hz = int(subject["sampling_rate_hz"])
    n_total_samples = int(subject["n_samples"])

    for repetition_index, repetition_base_seconds in enumerate(
        REPETITION_BASE_SECONDS,
        start=1,
    ):
        cycle_id = (
            f"{subject['subject_key']}-C{repetition_index:02d}"
        )

        for gesture in GESTURES:
            gesture_index = int(gesture["gesture_index"])
            raw_label = str(gesture["raw_label"])
            canonical_label = gesture["canonical_label"]
            target_eligible = canonical_label is not None

            gesture_anchor_seconds = (
                repetition_base_seconds + gesture_index * 10
            )
            segment_start_seconds = (
                gesture_anchor_seconds
                + SEGMENT_START_OFFSET_SECONDS
            )
            segment_end_seconds = (
                gesture_anchor_seconds
                + SEGMENT_END_OFFSET_SECONDS
            )

            segment_start_sample = round_half_up(
                segment_start_seconds * fs_hz
            )
            segment_end_sample_exclusive = round_half_up(
                segment_end_seconds * fs_hz
            )
            n_samples = (
                segment_end_sample_exclusive
                - segment_start_sample
            )

            if n_samples != segment_samples:
                raise RuntimeError(
                    "SEGMENT LENGTH GATE FAILED: "
                    f"subject={subject_id}, repetition={repetition_index}, "
                    f"gesture={raw_label}, n_samples={n_samples}"
                )

            if not (
                0 <= segment_start_sample
                < segment_end_sample_exclusive
                <= n_total_samples
            ):
                raise RuntimeError(
                    "SEGMENT BOUNDARY GATE FAILED: "
                    f"subject={subject_id}, repetition={repetition_index}, "
                    f"gesture={raw_label}, "
                    f"start={segment_start_sample}, "
                    f"end={segment_end_sample_exclusive}, "
                    f"record_length={n_total_samples}"
                )

            record_id = (
                f"{subject['subject_key']}"
                f"-R{repetition_index:02d}"
                f"-G{gesture_index:02d}"
                f"-{raw_label}"
            )
            repetition_id = (
                f"{subject['subject_key']}"
                f"-{raw_label}"
                f"-R{repetition_index:02d}"
            )

            row = {
                "dataset_id": DATASET_ID,
                "dataset_source_id": DATASET_SOURCE_ID,
                "dataset_version": DATASET_VERSION,
                "dataset_view_id": (
                    DATASET_VIEW_ID
                    if target_eligible
                    else "mendeley_non_target_audit_v1"
                ),
                "record_id": record_id,
                "subject_id": subject_id,
                "subject_key": subject["subject_key"],
                "day_id": "day-1",
                "session_id": "session-1",
                "cycle_id": cycle_id,
                "repetition_index": repetition_index,
                "repetition_id": repetition_id,
                "gesture_index": gesture_index,
                "raw_label": raw_label,
                "canonical_label": (
                    canonical_label
                    if canonical_label is not None
                    else ""
                ),
                "target_eligible": target_eligible,
                "partition": partition,
                "signal_path": str(
                    Path(subject["mat_path"]).relative_to(
                        RUNTIME_ROOT
                    )
                ),
                "source_filename": subject["filename"],
                "source_file_sha256": subject[
                    "source_file_sha256"
                ],
                "sampling_rate_hz": fs_hz,
                "n_channels": subject["n_channels"],
                "segment_start_seconds": segment_start_seconds,
                "segment_end_seconds": segment_end_seconds,
                "segment_start_sample": segment_start_sample,
                "segment_end_sample_exclusive": (
                    segment_end_sample_exclusive
                ),
                "n_samples": n_samples,
                "segmentation_version": SEGMENTATION_VERSION,
                "label_mapping_version": LABEL_MAPPING_VERSION,
                "split_version": SPLIT_VERSION,
                "channel_policy_id": (
                    PRIMARY_CHANNEL_POLICY_ID
                    if target_eligible
                    else "all4-audit-only-v1"
                ),
                "preprocessing_policy_id": (
                    PREPROCESSING_POLICY_ID
                ),
                "training_allowed": TRAINING_ALLOWED,
            }

            all_segment_rows.append(row)

            if target_eligible:
                primary_segment_rows.append(row.copy())


expected_all_segments = (
    EXPECTED_SUBJECT_COUNT
    * len(REPETITION_BASE_SECONDS)
    * len(GESTURES)
)
expected_primary_segments = (
    EXPECTED_SUBJECT_COUNT
    * len(REPETITION_BASE_SECONDS)
    * len(PRIMARY_CLASS_ORDER)
)

if len(all_segment_rows) != expected_all_segments:
    raise RuntimeError(
        f"ALL SEGMENT COUNT FAILED: {len(all_segment_rows)}"
    )

if len(primary_segment_rows) != expected_primary_segments:
    raise RuntimeError(
        "PRIMARY SEGMENT COUNT FAILED: "
        f"{len(primary_segment_rows)}"
    )

if len({
    row["record_id"]
    for row in all_segment_rows
}) != len(all_segment_rows):
    raise RuntimeError("Duplicate record_id detected.")

class_counts = Counter(
    row["canonical_label"]
    for row in primary_segment_rows
)
expected_per_class = (
    EXPECTED_SUBJECT_COUNT
    * len(REPETITION_BASE_SECONDS)
)

if class_counts != Counter({
    label: expected_per_class
    for label in PRIMARY_CLASS_ORDER
}):
    raise RuntimeError(
        f"PRIMARY CLASS COVERAGE FAILED: {dict(class_counts)}"
    )

partition_class_counts = Counter(
    (row["partition"], row["canonical_label"])
    for row in primary_segment_rows
)

for partition, expected_subjects in [
    ("train", 32),
    ("validation", 8),
]:
    for label in PRIMARY_CLASS_ORDER:
        expected_count = (
            expected_subjects
            * len(REPETITION_BASE_SECONDS)
        )
        actual_count = partition_class_counts[(partition, label)]
        if actual_count != expected_count:
            raise RuntimeError(
                "PARTITION CLASS COVERAGE FAILED: "
                f"{partition}/{label}: "
                f"expected={expected_count}, actual={actual_count}"
            )

segment_fieldnames = list(all_segment_rows[0].keys())

with ALL_SEGMENTS_CSV.open(
    "w",
    encoding="utf-8",
    newline="",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=segment_fieldnames,
    )
    writer.writeheader()
    writer.writerows(all_segment_rows)

with PRIMARY_METADATA_CSV.open(
    "w",
    encoding="utf-8",
    newline="",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=segment_fieldnames,
    )
    writer.writeheader()
    writer.writerows(primary_segment_rows)

for artifact in [ALL_SEGMENTS_CSV, PRIMARY_METADATA_CSV]:
    atomic_copy(
        artifact,
        DRIVE_MANIFEST_DIR / artifact.name,
    )

SEGMENT_INDEX_HASH = sha256_file(PRIMARY_METADATA_CSV)

print("=" * 86)
print("[CELL 7 SUMMARY]")
print("=" * 86)
print(f"All gesture segments     : {len(all_segment_rows)}")
print(f"Primary segments         : {len(primary_segment_rows)}")
print(f"Segments per class       : {dict(class_counts)}")
print(
    "Partition/class counts  :",
    dict(sorted(partition_class_counts.items())),
)
print(f"Primary metadata SHA-256 : {SEGMENT_INDEX_HASH}")
print(f"Output                    : {PRIMARY_METADATA_CSV}")
print("[PASS] CELL 7 hoàn tất: official segmentation index hợp lệ.")

# %% [markdown]
# ##5. Window index
#
# Mỗi gesture-repetition là atomic record `6 s = 12,000 samples`.
#
# Với `400 samples/window` và `200 samples/hop`:
#
# ```text
# windows_per_record = floor((12000 - 400) / 200) + 1 = 59
# ```
#
# Expected primary windows:
#
# ```text
# 40 subjects × 5 repetitions × 4 classes × 59 = 47,200
# ```

# %%
# === CELL 8: Build leakage-safe window index ===

window_rows: list[dict[str, Any]] = []

for segment in primary_segment_rows:
    segment_start = int(segment["segment_start_sample"])
    segment_end = int(segment["segment_end_sample_exclusive"])
    record_length = int(segment["n_samples"])

    window_ordinal = 0

    for relative_start in range(
        0,
        record_length - window_samples + 1,
        hop_samples,
    ):
        relative_end = relative_start + window_samples
        absolute_start = segment_start + relative_start
        absolute_end = segment_start + relative_end

        if absolute_end > segment_end:
            raise RuntimeError(
                "WINDOW CROSSES SEGMENT BOUNDARY: "
                f"{segment['record_id']}"
            )

        window_id = (
            f"{segment['record_id']}"
            f"-W{window_ordinal:03d}"
        )

        window_rows.append(
            {
                "dataset_id": DATASET_ID,
                "dataset_view_id": DATASET_VIEW_ID,
                "record_id": segment["record_id"],
                "window_id": window_id,
                "subject_id": segment["subject_id"],
                "subject_key": segment["subject_key"],
                "day_id": segment["day_id"],
                "session_id": segment["session_id"],
                "cycle_id": segment["cycle_id"],
                "repetition_id": segment["repetition_id"],
                "repetition_index": segment[
                    "repetition_index"
                ],
                "gesture_index": segment["gesture_index"],
                "raw_label": segment["raw_label"],
                "canonical_label": segment[
                    "canonical_label"
                ],
                "partition": segment["partition"],
                "signal_path": segment["signal_path"],
                "source_file_sha256": segment[
                    "source_file_sha256"
                ],
                "segment_start_sample": segment_start,
                "segment_end_sample_exclusive": segment_end,
                "window_ordinal": window_ordinal,
                "window_start_in_segment": relative_start,
                "window_end_in_segment_exclusive": relative_end,
                "start_sample": absolute_start,
                "end_sample_exclusive": absolute_end,
                "n_samples": window_samples,
                "sampling_rate_hz": segment[
                    "sampling_rate_hz"
                ],
                "window_ms": WINDOW_MS,
                "hop_ms": HOP_MS,
                "windowing_version": WINDOWING_VERSION,
                "split_version": SPLIT_VERSION,
                "label_mapping_version": (
                    LABEL_MAPPING_VERSION
                ),
                "channel_policy_id": (
                    PRIMARY_CHANNEL_POLICY_ID
                ),
                "preprocessing_policy_id": (
                    PREPROCESSING_POLICY_ID
                ),
                "training_allowed": TRAINING_ALLOWED,
            }
        )

        window_ordinal += 1

    if window_ordinal != expected_windows_per_segment:
        raise RuntimeError(
            "WINDOWS PER RECORD GATE FAILED: "
            f"{segment['record_id']} -> {window_ordinal}"
        )

expected_total_windows = (
    len(primary_segment_rows)
    * expected_windows_per_segment
)

if len(window_rows) != expected_total_windows:
    raise RuntimeError(
        "TOTAL WINDOW COUNT FAILED: "
        f"expected={expected_total_windows}, "
        f"actual={len(window_rows)}"
    )

window_ids = [row["window_id"] for row in window_rows]
if len(window_ids) != len(set(window_ids)):
    raise RuntimeError("Duplicate window_id detected.")

for row in window_rows:
    if row["partition"] not in {"train", "validation"}:
        raise RuntimeError(
            f"Forbidden partition in window index: "
            f"{row['partition']}"
        )

window_partition_counts = Counter(
    row["partition"]
    for row in window_rows
)
window_class_counts = Counter(
    row["canonical_label"]
    for row in window_rows
)

window_fieldnames = list(window_rows[0].keys())

with gzip.open(
    WINDOW_INDEX_CSV_GZ,
    "wt",
    encoding="utf-8",
    newline="",
) as file_obj:
    writer = csv.DictWriter(
        file_obj,
        fieldnames=window_fieldnames,
    )
    writer.writeheader()
    writer.writerows(window_rows)

atomic_copy(
    WINDOW_INDEX_CSV_GZ,
    DRIVE_MANIFEST_DIR / WINDOW_INDEX_CSV_GZ.name,
)

WINDOW_INDEX_HASH = sha256_file(WINDOW_INDEX_CSV_GZ)

windows_by_record: dict[str, list[dict[str, Any]]] = (
    defaultdict(list)
)

for row in window_rows:
    windows_by_record[row["record_id"]].append(row)

for record_id in windows_by_record:
    windows_by_record[record_id].sort(
        key=lambda row: int(row["window_ordinal"])
    )

print("=" * 86)
print("[CELL 8 SUMMARY]")
print("=" * 86)
print(f"Primary records       : {len(primary_segment_rows)}")
print(f"Windows per record    : {expected_windows_per_segment}")
print(f"Total windows         : {len(window_rows)}")
print(f"Partition counts      : {dict(window_partition_counts)}")
print(f"Class counts          : {dict(window_class_counts)}")
print(f"Window-index SHA-256  : {WINDOW_INDEX_HASH}")
print(f"Output                : {WINDOW_INDEX_CSV_GZ}")
print("[PASS] CELL 8 hoàn tất: window index không vượt atomic record.")

# %% [markdown]
# ## 6. Feature Set 14
#
# Hợp đồng:
#
# ```text
# x: window sau khi đã trừ mean của toàn gesture-repetition record theo channel
# P[k] = |rfft(x)[k]|² / N
# ```
#
# - Skewness: adjusted Fisher–Pearson, `bias=False`.
# - Kurtosis: Fisher excess, `bias=False`.
# - STD: `ddof=1`.
# - Spectrum: rectangular, full one-sided `0..Nyquist`, không nhân đôi interior bins.
# - Entropy: base 2, đơn vị bits.
# - Constant/zero-power/nonfinite: gắn flag và không impute.

# %%
# === CELL 9: Vectorized Feature Set 14 extractor + parity tests ===

def build_window_tensor(
    centered_segment: np.ndarray,
    window_samples: int,
    hop_samples: int,
) -> np.ndarray:
    """
    Input : (segment_samples, channels)
    Output: (n_windows, window_samples, channels)
    """
    if centered_segment.ndim != 2:
        raise ValueError(
            f"Expected 2D segment, got {centered_segment.shape}"
        )

    n_samples, n_channels = centered_segment.shape

    if n_samples < window_samples:
        raise ValueError(
            f"Segment too short: {n_samples} < {window_samples}"
        )

    starts = np.arange(
        0,
        n_samples - window_samples + 1,
        hop_samples,
        dtype=np.int64,
    )
    offsets = np.arange(
        window_samples,
        dtype=np.int64,
    )

    return centered_segment[
        starts[:, None] + offsets[None, :],
        :,
    ]


def extract_feature_set_14_batch(
    windows: np.ndarray,
    fs_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Parameters
    ----------
    windows:
        Shape (n_windows, n_samples, n_channels).

    Returns
    -------
    features:
        Shape (n_windows, n_channels, 14), FEATURE_ORDER.
    qc_flags:
        Object/string array shape (n_windows, n_channels).
    """
    x = np.asarray(windows, dtype=np.float64)

    if x.ndim != 3:
        raise ValueError(
            f"Expected 3D windows, got shape={x.shape}"
        )

    n_windows, n_samples, n_channels = x.shape

    if n_samples < 2:
        raise ValueError("Feature extraction requires N >= 2.")

    if not np.isfinite(x).all():
        raise ValueError(
            "Input contains NaN/Inf. Fail closed; no imputation."
        )

    mean_values = np.mean(x, axis=1)
    rms = np.sqrt(np.mean(np.square(x), axis=1))
    mav = np.mean(np.abs(x), axis=1)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        skewness = scipy.stats.skew(
            x,
            axis=1,
            bias=False,
            nan_policy="propagate",
        )
        kurtosis = scipy.stats.kurtosis(
            x,
            axis=1,
            fisher=True,
            bias=False,
            nan_policy="propagate",
        )

    max_signed = np.max(x, axis=1)
    min_signed = np.min(x, axis=1)
    std_sample = np.std(x, axis=1, ddof=1)

    fft_values = np.fft.rfft(
        x,
        n=n_samples,
        axis=1,
    )
    power = (
        np.abs(fft_values) ** 2
    ) / float(n_samples)

    frequencies = np.fft.rfftfreq(
        n_samples,
        d=1.0 / float(fs_hz),
    )

    spectral_min = np.min(power, axis=1)
    spectral_max = np.max(power, axis=1)
    spectral_std = np.std(power, axis=1, ddof=1)

    total_power = np.sum(power, axis=1)
    zero_power = total_power <= 0.0

    cumulative_power = np.cumsum(power, axis=1)
    half_power = total_power / 2.0
    mdf_indices = np.argmax(
        cumulative_power >= half_power[:, None, :],
        axis=1,
    )
    mdf = frequencies[mdf_indices].astype(np.float64)

    weighted_frequency_sum = np.sum(
        power * frequencies[None, :, None],
        axis=1,
    )
    mnf = np.full(
        (n_windows, n_channels),
        np.nan,
        dtype=np.float64,
    )
    np.divide(
        weighted_frequency_sum,
        total_power,
        out=mnf,
        where=~zero_power,
    )

    probabilities = np.zeros_like(
        power,
        dtype=np.float64,
    )
    np.divide(
        power,
        total_power[:, None, :],
        out=probabilities,
        where=~zero_power[:, None, :],
    )

    entropy_terms = np.zeros_like(probabilities)
    positive_probability = probabilities > 0.0
    entropy_terms[positive_probability] = (
        -probabilities[positive_probability]
        * np.log2(probabilities[positive_probability])
    )
    entropy = np.sum(entropy_terms, axis=1)

    mdf[zero_power] = np.nan
    mnf[zero_power] = np.nan
    entropy[zero_power] = np.nan

    features = np.stack(
        [
            rms,
            mav,
            skewness,
            kurtosis,
            max_signed,
            min_signed,
            std_sample,
            mean_values,
            spectral_min,
            spectral_max,
            spectral_std,
            mdf,
            mnf,
            entropy,
        ],
        axis=2,
    )

    constant_window = np.ptp(x, axis=1) == 0.0
    feature_nonfinite = ~np.isfinite(features).all(axis=2)

    qc_flags = np.full(
        (n_windows, n_channels),
        "",
        dtype=object,
    )

    for window_index in range(n_windows):
        for channel_index in range(n_channels):
            flags = []
            if n_samples < 4:
                flags.append("insufficient_samples_moments")
            if constant_window[window_index, channel_index]:
                flags.append("constant_window")
            if zero_power[window_index, channel_index]:
                flags.append("zero_power_window")
            if power.shape[1] < 2:
                flags.append("insufficient_spectral_bins")
            if feature_nonfinite[
                window_index,
                channel_index,
            ]:
                flags.append("feature_nonfinite")

            qc_flags[window_index, channel_index] = ";".join(
                flags
            )

    return features, qc_flags


def scalar_reference_feature_set_14(
    signal: np.ndarray,
    fs_hz: float,
) -> np.ndarray:
    x = np.asarray(signal, dtype=np.float64)
    n_samples = x.size

    fft_values = np.fft.rfft(x, n=n_samples)
    power = np.abs(fft_values) ** 2 / float(n_samples)
    frequencies = np.fft.rfftfreq(
        n_samples,
        d=1.0 / float(fs_hz),
    )

    total_power = float(np.sum(power))

    if total_power > 0:
        cumulative_power = np.cumsum(power)
        mdf_hz = float(
            frequencies[
                np.searchsorted(
                    cumulative_power,
                    total_power / 2.0,
                    side="left",
                )
            ]
        )
        mnf_hz = float(
            np.sum(frequencies * power) / total_power
        )
        probabilities = power / total_power
        positive = probabilities > 0
        entropy_bits = float(
            -np.sum(
                probabilities[positive]
                * np.log2(probabilities[positive])
            )
        )
    else:
        mdf_hz = np.nan
        mnf_hz = np.nan
        entropy_bits = np.nan

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        skewness = scipy.stats.skew(x, bias=False)
        kurtosis = scipy.stats.kurtosis(
            x,
            fisher=True,
            bias=False,
        )

    return np.asarray(
        [
            np.sqrt(np.mean(x**2)),
            np.mean(np.abs(x)),
            skewness,
            kurtosis,
            np.max(x),
            np.min(x),
            np.std(x, ddof=1),
            np.mean(x),
            np.min(power),
            np.max(power),
            np.std(power, ddof=1),
            mdf_hz,
            mnf_hz,
            entropy_bits,
        ],
        dtype=np.float64,
    )


# Deterministic extractor parity test.
rng = np.random.default_rng(3101)
test_windows = rng.normal(
    loc=0.0,
    scale=1.0,
    size=(3, window_samples, 4),
).astype(np.float64)

batch_features, batch_flags = extract_feature_set_14_batch(
    test_windows,
    EXPECTED_FS_HZ,
)

if batch_features.shape != (3, 4, 14):
    raise RuntimeError(
        f"Unexpected feature shape: {batch_features.shape}"
    )

for window_index in range(test_windows.shape[0]):
    for channel_index in range(test_windows.shape[2]):
        reference = scalar_reference_feature_set_14(
            test_windows[window_index, :, channel_index],
            EXPECTED_FS_HZ,
        )
        actual = batch_features[
            window_index,
            channel_index,
            :,
        ]

        if not np.allclose(
            actual,
            reference,
            rtol=1e-11,
            atol=1e-12,
            equal_nan=True,
        ):
            differences = {
                FEATURE_ORDER[i]: (
                    float(actual[i]),
                    float(reference[i]),
                )
                for i in range(len(FEATURE_ORDER))
                if not np.isclose(
                    actual[i],
                    reference[i],
                    rtol=1e-11,
                    atol=1e-12,
                    equal_nan=True,
                )
            }
            raise RuntimeError(
                f"Feature parity failed: {differences}"
            )

# Constant-window policy test.
constant_windows = np.ones(
    (1, window_samples, 1),
    dtype=np.float64,
)
constant_features, constant_flags = (
    extract_feature_set_14_batch(
        constant_windows,
        EXPECTED_FS_HZ,
    )
)

if "constant_window" not in constant_flags[0, 0]:
    raise RuntimeError("Constant-window QC test failed.")

if np.isfinite(
    constant_features[
        0,
        0,
        FEATURE_ORDER.index("skewness_unbiased"),
    ]
):
    raise RuntimeError(
        "Constant skewness must remain NaN."
    )

print("=" * 86)
print("[CELL 9 SUMMARY]")
print("=" * 86)
print(f"Feature count      : {len(FEATURE_ORDER)}")
print(f"Feature order      : {FEATURE_ORDER}")
print(f"Vectorized parity  : PASS")
print(f"Constant QC policy : PASS")
print("[PASS] CELL 9 hoàn tất: extractor đã khóa và tự kiểm thử.")

# %% [markdown]
# ## 7. Feature extraction theo subject, có checkpoint
#
# Mỗi subject tạo ba artifact cache:
#
# ```text
# cache/day31-subject-features/Sxxx-matrix.npz
# features/by-subject/Sxxx-features.csv.gz
# features/exclusions-by-subject/Sxxx-exclusions.csv
# ```
#
# Nếu source hash và pipeline fingerprint không đổi, lần chạy sau sẽ `SKIP` subject đã hoàn tất.

# %%
# === CELL 10: Resume-safe feature extraction by subject ===

FORCE_RECOMPUTE_FEATURES = False

feature_table_fieldnames = [
    "dataset_id",
    "dataset_view_id",
    "split_name",
    "subject_id",
    "subject_key",
    "record_id",
    "window_id",
    "cycle_id",
    "repetition_id",
    "repetition_index",
    "gesture_index",
    "raw_label",
    "canonical_label",
    "channel_id",
    "channel_index",
    "is_primary_channel",
    "sampling_rate_hz",
    "window_ms",
    "hop_ms",
    "source_file_sha256",
    "split_version",
    "segmentation_version",
    "windowing_version",
    "feature_set_version",
    "preprocessing_policy_id",
    "channel_policy_id",
    "qc_flags",
    "valid_feature_row",
    *FEATURE_ORDER,
]

exclusion_fieldnames = [
    "dataset_id",
    "dataset_view_id",
    "subject_id",
    "record_id",
    "window_id",
    "canonical_label",
    "partition",
    "repetition_id",
    "invalid_primary_channels",
    "qc_flags",
    "reason_code",
]


def subject_pipeline_fingerprint(
    subject: dict[str, Any],
) -> str:
    payload = {
        "contract_hash": CONTRACT_HASH,
        "split_hash": split_hash,
        "segment_index_hash": SEGMENT_INDEX_HASH,
        "window_index_hash": WINDOW_INDEX_HASH,
        "subject_id": subject["subject_id"],
        "source_file_sha256": subject[
            "source_file_sha256"
        ],
        "partition": partition_by_subject[
            subject["subject_id"]
        ],
        "feature_set_version": FEATURE_SET_VERSION,
        "feature_order": list(FEATURE_ORDER),
        "primary_channels": list(PRIMARY_CHANNEL_IDS),
    }
    return sha256_json(payload)


def subject_cache_paths(subject_key: str) -> dict[str, Path]:
    return {
        "matrix": (
            SUBJECT_FEATURE_CACHE_DIR
            / f"{subject_key}-matrix.npz"
        ),
        "features": (
            SUBJECT_FEATURE_TABLE_DIR
            / f"{subject_key}-features.csv.gz"
        ),
        "exclusions": (
            SUBJECT_EXCLUSION_DIR
            / f"{subject_key}-exclusions.csv"
        ),
        "evidence": (
            SUBJECT_FEATURE_CACHE_DIR
            / f"{subject_key}-evidence.json"
        ),
    }


def subject_cache_is_valid(
    paths: dict[str, Path],
    fingerprint: str,
) -> bool:
    if FORCE_RECOMPUTE_FEATURES:
        return False

    if not all(
        paths[key].exists()
        for key in [
            "matrix",
            "features",
            "exclusions",
            "evidence",
        ]
    ):
        return False

    try:
        evidence = json.loads(
            paths["evidence"].read_text(encoding="utf-8")
        )
    except Exception:
        return False

    if evidence.get("pipeline_fingerprint") != fingerprint:
        return False

    try:
        with np.load(
            paths["matrix"],
            allow_pickle=False,
        ) as cached:
            required = {
                "X",
                "y",
                "subject_ids",
                "window_ids",
                "record_ids",
                "repetition_ids",
                "split_names",
            }
            if not required.issubset(set(cached.files)):
                return False
            if cached["X"].ndim != 2:
                return False
            if cached["X"].shape[1] != 42:
                return False
            if not np.isfinite(cached["X"]).all():
                return False
    except Exception:
        return False

    return True


primary_segments_by_subject: dict[
    str,
    list[dict[str, Any]],
] = defaultdict(list)

for row in primary_segment_rows:
    primary_segments_by_subject[row["subject_id"]].append(row)

for subject_id in primary_segments_by_subject:
    primary_segments_by_subject[subject_id].sort(
        key=lambda row: (
            int(row["repetition_index"]),
            int(row["gesture_index"]),
        )
    )


subject_run_summaries = []
overall_start_time = time.monotonic()

print("=" * 86)
print("[CELL 10] FEATURE EXTRACTION")
print("=" * 86)

for subject_number, subject in enumerate(
    sorted(
        subject_catalog,
        key=lambda row: subject_sort_key(row["subject_id"]),
    ),
    start=1,
):
    subject_id = subject["subject_id"]
    subject_key = subject["subject_key"]
    paths = subject_cache_paths(subject_key)
    fingerprint = subject_pipeline_fingerprint(subject)

    if subject_cache_is_valid(paths, fingerprint):
        evidence = json.loads(
            paths["evidence"].read_text(encoding="utf-8")
        )
        subject_run_summaries.append(evidence)
        print(
            f"[{subject_number:02d}/40] {subject_key}: "
            f"[SKIP] valid cache, "
            f"matrix_rows={evidence['matrix_rows']}"
        )
        continue

    subject_start_time = time.monotonic()
    mat_path = Path(subject["mat_path"])

    loaded = scipy.io.loadmat(
        mat_path,
        variable_names=["data", "fs", "iD"],
        squeeze_me=True,
        struct_as_record=False,
    )

    data = np.asarray(
        loaded["data"],
        dtype=np.float64,
    )
    fs_hz = int(np.asarray(loaded["fs"]).reshape(-1)[0])
    mat_id = str(
        int(np.asarray(loaded["iD"]).reshape(-1)[0])
    )

    if data.shape != EXPECTED_RAW_SHAPE:
        raise RuntimeError(
            f"{subject_key}: data shape={data.shape}"
        )

    if fs_hz != EXPECTED_FS_HZ:
        raise RuntimeError(
            f"{subject_key}: fs={fs_hz}"
        )

    if mat_id != subject_id:
        raise RuntimeError(
            f"{subject_key}: MAT iD={mat_id}"
        )

    if not np.isfinite(data).all():
        raise RuntimeError(
            f"{subject_key}: raw data contains NaN/Inf."
        )

    temporary_feature_path = paths["features"].with_suffix(
        paths["features"].suffix + ".part"
    )
    temporary_exclusion_path = paths["exclusions"].with_suffix(
        paths["exclusions"].suffix + ".part"
    )
    temporary_matrix_path = paths["matrix"].with_suffix(
        paths["matrix"].suffix + ".part"
    )

    for temporary_path in [
        temporary_feature_path,
        temporary_exclusion_path,
        temporary_matrix_path,
    ]:
        temporary_path.unlink(missing_ok=True)

    subject_X_blocks = []
    subject_y = []
    subject_ids_array = []
    subject_keys_array = []
    subject_window_ids = []
    subject_record_ids = []
    subject_cycle_ids = []
    subject_repetition_ids = []
    subject_split_names = []
    subject_gesture_indices = []
    subject_window_starts = []
    subject_window_ends = []
    subject_source_hashes = []

    total_windows_subject = 0
    valid_windows_subject = 0
    invalid_windows_subject = 0
    feature_rows_subject = 0

    with gzip.open(
        temporary_feature_path,
        "wt",
        encoding="utf-8",
        newline="",
    ) as feature_file, temporary_exclusion_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as exclusion_file:
        feature_writer = csv.DictWriter(
            feature_file,
            fieldnames=feature_table_fieldnames,
        )
        exclusion_writer = csv.DictWriter(
            exclusion_file,
            fieldnames=exclusion_fieldnames,
        )
        feature_writer.writeheader()
        exclusion_writer.writeheader()

        for segment in primary_segments_by_subject[subject_id]:
            record_id = segment["record_id"]
            record_windows = windows_by_record[record_id]

            start_sample = int(segment["segment_start_sample"])
            end_sample = int(
                segment["segment_end_sample_exclusive"]
            )

            raw_segment = data[
                start_sample:end_sample,
                :,
            ]

            if raw_segment.shape != (
                segment_samples,
                4,
            ):
                raise RuntimeError(
                    f"{record_id}: segment shape="
                    f"{raw_segment.shape}"
                )

            # Day30 policy: per-record, per-channel mean subtraction.
            record_channel_mean = np.mean(
                raw_segment,
                axis=0,
                keepdims=True,
            )
            centered_segment = (
                raw_segment - record_channel_mean
            )

            window_tensor = build_window_tensor(
                centered_segment,
                window_samples,
                hop_samples,
            )

            if window_tensor.shape != (
                expected_windows_per_segment,
                window_samples,
                4,
            ):
                raise RuntimeError(
                    f"{record_id}: window tensor shape="
                    f"{window_tensor.shape}"
                )

            features, qc_flags = (
                extract_feature_set_14_batch(
                    window_tensor,
                    fs_hz,
                )
            )

            if features.shape != (
                expected_windows_per_segment,
                4,
                14,
            ):
                raise RuntimeError(
                    f"{record_id}: feature shape="
                    f"{features.shape}"
                )

            if len(record_windows) != expected_windows_per_segment:
                raise RuntimeError(
                    f"{record_id}: window-index count="
                    f"{len(record_windows)}"
                )

            for local_window_index, window_row in enumerate(
                record_windows
            ):
                total_windows_subject += 1

                primary_feature_block = features[
                    local_window_index,
                    :3,
                    :,
                ]
                primary_channel_flags = qc_flags[
                    local_window_index,
                    :3,
                ]

                valid_primary_window = bool(
                    np.isfinite(primary_feature_block).all()
                )

                if valid_primary_window:
                    flat_primary = primary_feature_block.reshape(
                        -1
                    )
                    if flat_primary.size != 42:
                        raise RuntimeError(
                            "Primary flatten dimension mismatch."
                        )

                    subject_X_blocks.append(flat_primary)
                    subject_y.append(
                        window_row["canonical_label"]
                    )
                    subject_ids_array.append(subject_id)
                    subject_keys_array.append(subject_key)
                    subject_window_ids.append(
                        window_row["window_id"]
                    )
                    subject_record_ids.append(record_id)
                    subject_cycle_ids.append(
                        window_row["cycle_id"]
                    )
                    subject_repetition_ids.append(
                        window_row["repetition_id"]
                    )
                    subject_split_names.append(
                        window_row["partition"]
                    )
                    subject_gesture_indices.append(
                        int(window_row["gesture_index"])
                    )
                    subject_window_starts.append(
                        int(window_row["start_sample"])
                    )
                    subject_window_ends.append(
                        int(
                            window_row[
                                "end_sample_exclusive"
                            ]
                        )
                    )
                    subject_source_hashes.append(
                        window_row["source_file_sha256"]
                    )
                    valid_windows_subject += 1
                else:
                    invalid_windows_subject += 1
                    invalid_channels = [
                        PRIMARY_CHANNEL_IDS[channel_index]
                        for channel_index in range(3)
                        if not np.isfinite(
                            primary_feature_block[
                                channel_index,
                                :,
                            ]
                        ).all()
                    ]
                    flags = sorted({
                        flag
                        for channel_flags in primary_channel_flags
                        for flag in str(channel_flags).split(";")
                        if flag
                    })

                    exclusion_writer.writerow(
                        {
                            "dataset_id": DATASET_ID,
                            "dataset_view_id": DATASET_VIEW_ID,
                            "subject_id": subject_id,
                            "record_id": record_id,
                            "window_id": window_row[
                                "window_id"
                            ],
                            "canonical_label": window_row[
                                "canonical_label"
                            ],
                            "partition": window_row[
                                "partition"
                            ],
                            "repetition_id": window_row[
                                "repetition_id"
                            ],
                            "invalid_primary_channels": (
                                ";".join(invalid_channels)
                            ),
                            "qc_flags": ";".join(flags),
                            "reason_code": (
                                "NONFINITE_PRIMARY_FEATURE"
                            ),
                        }
                    )

                for channel_index, channel_id in enumerate(
                    CANONICAL_CHANNEL_IDS
                ):
                    channel_features = features[
                        local_window_index,
                        channel_index,
                        :,
                    ]
                    feature_row = {
                        "dataset_id": DATASET_ID,
                        "dataset_view_id": (
                            DATASET_VIEW_ID
                            if channel_index < 3
                            else (
                                "mendeley_ch4_sensitivity_v1"
                            )
                        ),
                        "split_name": window_row[
                            "partition"
                        ],
                        "subject_id": subject_id,
                        "subject_key": subject_key,
                        "record_id": record_id,
                        "window_id": window_row[
                            "window_id"
                        ],
                        "cycle_id": window_row["cycle_id"],
                        "repetition_id": window_row[
                            "repetition_id"
                        ],
                        "repetition_index": window_row[
                            "repetition_index"
                        ],
                        "gesture_index": window_row[
                            "gesture_index"
                        ],
                        "raw_label": window_row[
                            "raw_label"
                        ],
                        "canonical_label": window_row[
                            "canonical_label"
                        ],
                        "channel_id": channel_id,
                        "channel_index": channel_index,
                        "is_primary_channel": (
                            channel_index < 3
                        ),
                        "sampling_rate_hz": fs_hz,
                        "window_ms": WINDOW_MS,
                        "hop_ms": HOP_MS,
                        "source_file_sha256": window_row[
                            "source_file_sha256"
                        ],
                        "split_version": SPLIT_VERSION,
                        "segmentation_version": (
                            SEGMENTATION_VERSION
                        ),
                        "windowing_version": (
                            WINDOWING_VERSION
                        ),
                        "feature_set_version": (
                            FEATURE_SET_VERSION
                        ),
                        "preprocessing_policy_id": (
                            PREPROCESSING_POLICY_ID
                        ),
                        "channel_policy_id": (
                            PRIMARY_CHANNEL_POLICY_ID
                            if channel_index < 3
                            else CH4_SENSITIVITY_POLICY_ID
                        ),
                        "qc_flags": qc_flags[
                            local_window_index,
                            channel_index,
                        ],
                        "valid_feature_row": bool(
                            np.isfinite(
                                channel_features
                            ).all()
                        ),
                    }

                    feature_row.update({
                        feature_name: float(
                            channel_features[
                                feature_index
                            ]
                        )
                        for feature_index, feature_name
                        in enumerate(FEATURE_ORDER)
                    })

                    feature_writer.writerow(feature_row)
                    feature_rows_subject += 1

    X_subject = (
        np.vstack(subject_X_blocks).astype(np.float64)
        if subject_X_blocks
        else np.empty((0, 42), dtype=np.float64)
    )

    if X_subject.shape[0] != valid_windows_subject:
        raise RuntimeError(
            f"{subject_key}: matrix row count mismatch."
        )

    if X_subject.shape[1] != 42:
        raise RuntimeError(
            f"{subject_key}: matrix dimension={X_subject.shape}"
        )

    if not np.isfinite(X_subject).all():
        raise RuntimeError(
            f"{subject_key}: nonfinite reached matrix cache."
        )

    with temporary_matrix_path.open("wb") as matrix_file:
        np.savez_compressed(
            matrix_file,
            X=X_subject,
            y=np.asarray(subject_y, dtype="U32"),
            subject_ids=np.asarray(
                subject_ids_array,
                dtype="U8",
            ),
            subject_keys=np.asarray(
                subject_keys_array,
                dtype="U32",
            ),
            window_ids=np.asarray(
                subject_window_ids,
                dtype="U128",
            ),
            record_ids=np.asarray(
                subject_record_ids,
                dtype="U128",
            ),
            cycle_ids=np.asarray(
                subject_cycle_ids,
                dtype="U64",
            ),
            repetition_ids=np.asarray(
                subject_repetition_ids,
                dtype="U128",
            ),
            split_names=np.asarray(
                subject_split_names,
                dtype="U16",
            ),
            gesture_indices=np.asarray(
                subject_gesture_indices,
                dtype=np.int16,
            ),
            start_samples=np.asarray(
                subject_window_starts,
                dtype=np.int64,
            ),
            end_samples_exclusive=np.asarray(
                subject_window_ends,
                dtype=np.int64,
            ),
            source_file_sha256=np.asarray(
                subject_source_hashes,
                dtype="U64",
            ),
        )

    temporary_feature_path.replace(paths["features"])
    temporary_exclusion_path.replace(paths["exclusions"])
    temporary_matrix_path.replace(paths["matrix"])

    invalid_ratio = (
        invalid_windows_subject / total_windows_subject
        if total_windows_subject
        else 0.0
    )

    elapsed = time.monotonic() - subject_start_time

    evidence = {
        "schema_version": "day31-subject-cache.v1",
        "created_at_utc": utc_now_iso(),
        "pipeline_fingerprint": fingerprint,
        "contract_hash": CONTRACT_HASH,
        "subject_id": subject_id,
        "subject_key": subject_key,
        "partition": partition_by_subject[subject_id],
        "source_filename": subject["filename"],
        "source_file_sha256": subject[
            "source_file_sha256"
        ],
        "total_windows": total_windows_subject,
        "matrix_rows": valid_windows_subject,
        "invalid_windows": invalid_windows_subject,
        "invalid_window_ratio": invalid_ratio,
        "feature_rows": feature_rows_subject,
        "matrix_sha256": sha256_file(paths["matrix"]),
        "feature_table_sha256": sha256_file(
            paths["features"]
        ),
        "exclusion_sha256": sha256_file(
            paths["exclusions"]
        ),
        "elapsed_seconds": elapsed,
        "training_allowed": TRAINING_ALLOWED,
    }

    write_json(evidence, paths["evidence"])
    subject_run_summaries.append(evidence)

    del data
    del loaded

    print(
        f"[{subject_number:02d}/40] {subject_key}: "
        f"windows={total_windows_subject}, "
        f"valid={valid_windows_subject}, "
        f"invalid={invalid_windows_subject}, "
        f"elapsed={elapsed:.1f}s"
    )


total_elapsed = time.monotonic() - overall_start_time

if len(subject_run_summaries) != 40:
    raise RuntimeError(
        "SUBJECT FEATURE COVERAGE FAILED: "
        f"{len(subject_run_summaries)}"
    )

total_feature_windows = sum(
    int(item["total_windows"])
    for item in subject_run_summaries
)
total_valid_windows = sum(
    int(item["matrix_rows"])
    for item in subject_run_summaries
)
total_invalid_windows = sum(
    int(item["invalid_windows"])
    for item in subject_run_summaries
)
total_feature_rows = sum(
    int(item["feature_rows"])
    for item in subject_run_summaries
)

overall_invalid_ratio = (
    total_invalid_windows / total_feature_windows
    if total_feature_windows
    else 0.0
)

if overall_invalid_ratio > 0.05:
    raise RuntimeError(
        "FEATURE INVALID-RATIO GATE BLOCKED: "
        f"{overall_invalid_ratio:.2%} > 5%."
    )

if overall_invalid_ratio > 0.01:
    print(
        "[WARN] Invalid-window ratio exceeds provisional "
        f"warning threshold: {overall_invalid_ratio:.2%}"
    )

print("\n" + "=" * 86)
print("[CELL 10 SUMMARY]")
print("=" * 86)
print(f"Subjects processed/cached : {len(subject_run_summaries)}")
print(f"Total windows             : {total_feature_windows}")
print(f"Valid matrix windows      : {total_valid_windows}")
print(f"Invalid windows           : {total_invalid_windows}")
print(f"Invalid ratio             : {overall_invalid_ratio:.4%}")
print(f"Feature rows (4 channels) : {total_feature_rows}")
print(f"Elapsed                   : {total_elapsed:.1f}s")
print("[PASS] CELL 10 hoàn tất: subject feature caches ready.")

# %% [markdown]
# ## 8. Aggregate feature partitions, pivot primary view, export NPZ
#
# Primary matrix order:
#
# ```text
# CH1 × 14 features
# CH2 × 14 features
# CH3 × 14 features
# ```
#
# `CH4` vẫn nằm trong feature table partition nhưng không đi vào `X` primary.
#
# Notebook xuất một NPZ tương thích Day 32 với key chính `X`, đồng thời thêm metadata để đánh giá theo subject/repetition và chống leakage.

# %%
# === CELL 11: Aggregate, pivot, export NPZ and evidence ===

# -----------------------------------------------------------------------------
# 1. Combine partitioned feature tables and exclusion reports
# -----------------------------------------------------------------------------

temporary_combined_feature = (
    COMBINED_FEATURE_TABLE_CSV_GZ.with_suffix(
        COMBINED_FEATURE_TABLE_CSV_GZ.suffix + ".part"
    )
)
temporary_combined_exclusion = (
    COMBINED_EXCLUSION_CSV.with_suffix(
        COMBINED_EXCLUSION_CSV.suffix + ".part"
    )
)

temporary_combined_feature.unlink(missing_ok=True)
temporary_combined_exclusion.unlink(missing_ok=True)

with gzip.open(
    temporary_combined_feature,
    "wt",
    encoding="utf-8",
    newline="",
) as output_feature_file:
    output_writer = csv.DictWriter(
        output_feature_file,
        fieldnames=feature_table_fieldnames,
    )
    output_writer.writeheader()

    for subject in sorted(
        subject_catalog,
        key=lambda row: subject_sort_key(row["subject_id"]),
    ):
        paths = subject_cache_paths(subject["subject_key"])
        with gzip.open(
            paths["features"],
            "rt",
            encoding="utf-8",
            newline="",
        ) as input_file:
            reader = csv.DictReader(input_file)
            if reader.fieldnames != feature_table_fieldnames:
                raise RuntimeError(
                    f"Feature schema mismatch: {paths['features']}"
                )
            for row in reader:
                output_writer.writerow(row)

with temporary_combined_exclusion.open(
    "w",
    encoding="utf-8",
    newline="",
) as output_exclusion_file:
    output_writer = csv.DictWriter(
        output_exclusion_file,
        fieldnames=exclusion_fieldnames,
    )
    output_writer.writeheader()

    for subject in sorted(
        subject_catalog,
        key=lambda row: subject_sort_key(row["subject_id"]),
    ):
        paths = subject_cache_paths(subject["subject_key"])
        with paths["exclusions"].open(
            "r",
            encoding="utf-8",
            newline="",
        ) as input_file:
            reader = csv.DictReader(input_file)
            if reader.fieldnames != exclusion_fieldnames:
                raise RuntimeError(
                    f"Exclusion schema mismatch: "
                    f"{paths['exclusions']}"
                )
            for row in reader:
                output_writer.writerow(row)

temporary_combined_feature.replace(
    COMBINED_FEATURE_TABLE_CSV_GZ
)
temporary_combined_exclusion.replace(
    COMBINED_EXCLUSION_CSV
)


# -----------------------------------------------------------------------------
# 2. Aggregate subject matrix caches
# -----------------------------------------------------------------------------

matrix_parts: dict[str, list[np.ndarray]] = defaultdict(list)

required_matrix_keys = (
    "X",
    "y",
    "subject_ids",
    "subject_keys",
    "window_ids",
    "record_ids",
    "cycle_ids",
    "repetition_ids",
    "split_names",
    "gesture_indices",
    "start_samples",
    "end_samples_exclusive",
    "source_file_sha256",
)

for subject in sorted(
    subject_catalog,
    key=lambda row: subject_sort_key(row["subject_id"]),
):
    paths = subject_cache_paths(subject["subject_key"])

    with np.load(
        paths["matrix"],
        allow_pickle=False,
    ) as subject_npz:
        missing_keys = (
            set(required_matrix_keys) - set(subject_npz.files)
        )
        if missing_keys:
            raise RuntimeError(
                f"{paths['matrix']} missing keys: "
                f"{sorted(missing_keys)}"
            )

        row_count = subject_npz["X"].shape[0]

        for key in required_matrix_keys:
            array = subject_npz[key]
            if key != "X" and array.shape[0] != row_count:
                raise RuntimeError(
                    f"{paths['matrix']}: key={key}, "
                    f"rows={array.shape[0]}, expected={row_count}"
                )
            matrix_parts[key].append(array.copy())

aggregated = {
    key: np.concatenate(parts, axis=0)
    for key, parts in matrix_parts.items()
}

X = aggregated["X"].astype(np.float64, copy=False)
y = aggregated["y"]
subject_ids_np = aggregated["subject_ids"]
subject_keys_np = aggregated["subject_keys"]
window_ids_np = aggregated["window_ids"]
record_ids_np = aggregated["record_ids"]
cycle_ids_np = aggregated["cycle_ids"]
repetition_ids_np = aggregated["repetition_ids"]
split_names_np = aggregated["split_names"]
gesture_indices_np = aggregated["gesture_indices"]
start_samples_np = aggregated["start_samples"]
end_samples_np = aggregated["end_samples_exclusive"]
source_hashes_np = aggregated["source_file_sha256"]

row_count = X.shape[0]

if X.shape[1] != 42:
    raise RuntimeError(
        f"MATRIX CONTRACT FAILED: X.shape={X.shape}"
    )

if not np.isfinite(X).all():
    raise RuntimeError(
        "MATRIX NULL POLICY FAILED: X contains NaN/Inf."
    )

if len(np.unique(window_ids_np)) != row_count:
    raise RuntimeError("Duplicate window_id in matrix.")

if set(np.unique(split_names_np)) - {"train", "validation"}:
    raise RuntimeError(
        f"Forbidden split values: {np.unique(split_names_np)}"
    )

if len(np.unique(subject_ids_np)) != 40:
    raise RuntimeError(
        "Matrix does not cover all 40 subjects."
    )

train_subjects_matrix = set(
    subject_ids_np[split_names_np == "train"].tolist()
)
validation_subjects_matrix = set(
    subject_ids_np[
        split_names_np == "validation"
    ].tolist()
)

if train_subjects_matrix & validation_subjects_matrix:
    raise RuntimeError(
        "MATRIX SUBJECT LEAKAGE DETECTED."
    )

if train_subjects_matrix != train_subject_ids:
    raise RuntimeError(
        "Matrix train subjects differ from split manifest."
    )

if validation_subjects_matrix != validation_subject_ids:
    raise RuntimeError(
        "Matrix validation subjects differ from split manifest."
    )


# -----------------------------------------------------------------------------
# 3. Column and feature-arm manifests
# -----------------------------------------------------------------------------

feature_columns = np.asarray(
    [
        f"{channel_id}__{feature_name}"
        for channel_id in PRIMARY_CHANNEL_IDS
        for feature_name in FEATURE_ORDER
    ],
    dtype="U80",
)

if feature_columns.size != 42:
    raise RuntimeError("Feature-column count must be 42.")

column_index_by_name = {
    name: index
    for index, name in enumerate(feature_columns.tolist())
}


def feature_arm_indices(
    feature_names: Iterable[str],
) -> np.ndarray:
    names = set(feature_names)
    indices = [
        index
        for index, column_name
        in enumerate(feature_columns.tolist())
        if column_name.split("__", 1)[1] in names
    ]
    return np.asarray(indices, dtype=np.int32)


f_td8_indices = feature_arm_indices(TD8_FEATURES)
f_sp6_indices = feature_arm_indices(SP6_FEATURES)
f_all14_indices = feature_arm_indices(FEATURE_ORDER)
f_no_moments12_indices = feature_arm_indices(
    NO_MOMENTS12_FEATURES
)

expected_arm_dimensions = {
    "F-TD8": 24,
    "F-SP6": 18,
    "F-ALL14": 42,
    "F-NO-MOMENTS12": 36,
}

actual_arm_dimensions = {
    "F-TD8": int(f_td8_indices.size),
    "F-SP6": int(f_sp6_indices.size),
    "F-ALL14": int(f_all14_indices.size),
    "F-NO-MOMENTS12": int(
        f_no_moments12_indices.size
    ),
}

if actual_arm_dimensions != expected_arm_dimensions:
    raise RuntimeError(
        "FEATURE ARM DIMENSION GATE FAILED: "
        f"{actual_arm_dimensions}"
    )

column_manifest = {
    "schema_version": "day31-feature-columns.v1",
    "created_at_utc": utc_now_iso(),
    "dataset_id": DATASET_ID,
    "dataset_view_id": DATASET_VIEW_ID,
    "feature_set_version": FEATURE_SET_VERSION,
    "channel_order": list(PRIMARY_CHANNEL_IDS),
    "feature_order_per_channel": list(FEATURE_ORDER),
    "flatten_order": "channel_major_then_feature",
    "columns": [
        {
            "column_index": index,
            "column_name": column_name,
            "channel_id": column_name.split("__", 1)[0],
            "feature_id": column_name.split("__", 1)[1],
        }
        for index, column_name
        in enumerate(feature_columns.tolist())
    ],
    "feature_arms": {
        "F-TD8": f_td8_indices.tolist(),
        "F-SP6": f_sp6_indices.tolist(),
        "F-ALL14": f_all14_indices.tolist(),
        "F-NO-MOMENTS12": (
            f_no_moments12_indices.tolist()
        ),
    },
    "expected_dimensions": expected_arm_dimensions,
    "training_allowed": TRAINING_ALLOWED,
}

write_json(column_manifest, COLUMN_MANIFEST_JSON)


# -----------------------------------------------------------------------------
# 4. Save canonical NPZ
# -----------------------------------------------------------------------------

temporary_npz = FINAL_NPZ.with_suffix(
    FINAL_NPZ.suffix + ".part"
)
temporary_npz.unlink(missing_ok=True)

with temporary_npz.open("wb") as output_file:
    np.savez_compressed(
        output_file,
        X=X,
        y=y.astype("U32"),
        groups=subject_ids_np.astype("U8"),
        subject_id=subject_ids_np.astype("U8"),
        subject_key=subject_keys_np.astype("U32"),
        repetition_ids=repetition_ids_np.astype("U128"),
        repetition_id=repetition_ids_np.astype("U128"),
        cycle_id=cycle_ids_np.astype("U64"),
        record_id=record_ids_np.astype("U128"),
        window_id=window_ids_np.astype("U128"),
        split_names=split_names_np.astype("U16"),
        partition=split_names_np.astype("U16"),
        gesture_id=gesture_indices_np.astype(np.int16),
        window_start=start_samples_np.astype(np.int64),
        window_end=end_samples_np.astype(np.int64),
        source_file_sha256=source_hashes_np.astype("U64"),
        dataset_ids=np.full(
            row_count,
            DATASET_ID,
            dtype="U64",
        ),
        feature_names=feature_columns,
        channel_names=np.asarray(
            PRIMARY_CHANNEL_IDS,
            dtype="U8",
        ),
        class_order=np.asarray(
            PRIMARY_CLASS_ORDER,
            dtype="U32",
        ),
        F_TD8_indices=f_td8_indices,
        F_SP6_indices=f_sp6_indices,
        F_ALL14_indices=f_all14_indices,
        F_NO_MOMENTS12_indices=f_no_moments12_indices,
        schema_version=np.asarray(
            "day31-mendeley-feature-matrix.v1"
        ),
        dataset_version=np.asarray(
            DATASET_VERSION,
            dtype=np.int16,
        ),
        dataset_view_id=np.asarray(DATASET_VIEW_ID),
        feature_set_version=np.asarray(
            FEATURE_SET_VERSION
        ),
        segmentation_version=np.asarray(
            SEGMENTATION_VERSION
        ),
        windowing_version=np.asarray(
            WINDOWING_VERSION
        ),
        split_version=np.asarray(SPLIT_VERSION),
        preprocessing_policy_id=np.asarray(
            PREPROCESSING_POLICY_ID
        ),
        channel_policy_id=np.asarray(
            PRIMARY_CHANNEL_POLICY_ID
        ),
        sampling_rate_hz=np.asarray(
            EXPECTED_FS_HZ,
            dtype=np.int32,
        ),
        window_ms=np.asarray(WINDOW_MS, dtype=np.int32),
        hop_ms=np.asarray(HOP_MS, dtype=np.int32),
        training_allowed=np.asarray(
            TRAINING_ALLOWED,
            dtype=np.bool_,
        ),
        model_fitting_allowed=np.asarray(
            MODEL_FITTING_ALLOWED,
            dtype=np.bool_,
        ),
        test_set_opened=np.asarray(
            TEST_SET_OPENED,
            dtype=np.bool_,
        ),
        pooled_training_allowed=np.asarray(
            POOLED_TRAINING_ALLOWED,
            dtype=np.bool_,
        ),
    )

temporary_npz.replace(FINAL_NPZ)

NPZ_SHA256 = sha256_file(FINAL_NPZ)
FEATURE_TABLE_SHA256 = sha256_file(
    COMBINED_FEATURE_TABLE_CSV_GZ
)
EXCLUSION_REPORT_SHA256 = sha256_file(
    COMBINED_EXCLUSION_CSV
)
COLUMN_MANIFEST_SHA256 = sha256_file(
    COLUMN_MANIFEST_JSON
)


# -----------------------------------------------------------------------------
# 5. Evidence
# -----------------------------------------------------------------------------

class_distribution = {
    str(label): int(count)
    for label, count in zip(
        *np.unique(y, return_counts=True)
    )
}
subject_distribution = {
    str(subject): int(count)
    for subject, count in zip(
        *np.unique(
            subject_ids_np,
            return_counts=True,
        )
    )
}
partition_distribution = {
    str(partition): int(count)
    for partition, count in zip(
        *np.unique(
            split_names_np,
            return_counts=True,
        )
    )
}

day31_evidence = {
    "schema_version": "day31-colab-etl-evidence.v2",
    "created_at_utc": utc_now_iso(),
    "status": "PASS",
    "pipeline": "Day27_31_Colab_ETL_Cell5_Onward",
    "dataset_id": DATASET_ID,
    "dataset_source_id": DATASET_SOURCE_ID,
    "dataset_version": DATASET_VERSION,
    "dataset_view_id": DATASET_VIEW_ID,
    "contracts": {
        "contract_hash": CONTRACT_HASH,
        "split_hash": split_hash,
        "segment_index_hash": SEGMENT_INDEX_HASH,
        "window_index_hash": WINDOW_INDEX_HASH,
        "segmentation_version": SEGMENTATION_VERSION,
        "windowing_version": WINDOWING_VERSION,
        "feature_set_version": FEATURE_SET_VERSION,
        "preprocessing_policy_id": (
            PREPROCESSING_POLICY_ID
        ),
        "channel_policy_id": (
            PRIMARY_CHANNEL_POLICY_ID
        ),
        "label_mapping_version": (
            LABEL_MAPPING_VERSION
        ),
    },
    "governance": {
        "training_allowed": TRAINING_ALLOWED,
        "model_fitting_allowed": (
            MODEL_FITTING_ALLOWED
        ),
        "scaler_fitting_allowed": (
            SCALER_FITTING_ALLOWED
        ),
        "test_signal_access_allowed": (
            TEST_SIGNAL_ACCESS_ALLOWED
        ),
        "test_set_opened": TEST_SET_OPENED,
        "pooled_training_allowed": (
            POOLED_TRAINING_ALLOWED
        ),
    },
    "counts": {
        "subjects": int(
            len(np.unique(subject_ids_np))
        ),
        "all_gesture_segments": len(all_segment_rows),
        "primary_segments": len(primary_segment_rows),
        "window_index_rows": len(window_rows),
        "valid_matrix_rows": int(row_count),
        "excluded_windows": int(
            total_invalid_windows
        ),
        "feature_table_rows": int(
            total_feature_rows
        ),
        "matrix_features": int(X.shape[1]),
    },
    "distributions": {
        "class": class_distribution,
        "subject": subject_distribution,
        "partition": partition_distribution,
    },
    "feature_arms": actual_arm_dimensions,
    "artifacts": {
        "feature_table": {
            "path": str(
                COMBINED_FEATURE_TABLE_CSV_GZ
            ),
            "sha256": FEATURE_TABLE_SHA256,
            "size_bytes": (
                COMBINED_FEATURE_TABLE_CSV_GZ
                .stat()
                .st_size
            ),
        },
        "exclusion_report": {
            "path": str(COMBINED_EXCLUSION_CSV),
            "sha256": EXCLUSION_REPORT_SHA256,
            "size_bytes": (
                COMBINED_EXCLUSION_CSV
                .stat()
                .st_size
            ),
        },
        "matrix_npz": {
            "path": str(FINAL_NPZ),
            "sha256": NPZ_SHA256,
            "size_bytes": FINAL_NPZ.stat().st_size,
            "shape": list(X.shape),
        },
        "column_manifest": {
            "path": str(COLUMN_MANIFEST_JSON),
            "sha256": COLUMN_MANIFEST_SHA256,
        },
    },
    "null_policy": {
        "imputation_performed": False,
        "matrix_nonfinite_count": int(
            np.size(X) - np.isfinite(X).sum()
        ),
        "excluded_window_count": int(
            total_invalid_windows
        ),
        "invalid_window_ratio": float(
            overall_invalid_ratio
        ),
    },
    "environment": {
        "python": sys.version,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    },
}

write_json(day31_evidence, DAY31_EVIDENCE_JSON)


# -----------------------------------------------------------------------------
# 6. Persist primary outputs to Google Drive
# -----------------------------------------------------------------------------

drive_artifacts = [
    FINAL_NPZ,
    COLUMN_MANIFEST_JSON,
    DAY31_EVIDENCE_JSON,
    COMBINED_EXCLUSION_CSV,
    COMBINED_FEATURE_TABLE_CSV_GZ,
]

for artifact in drive_artifacts:
    destination_root = (
        DRIVE_OUTPUT_DIR
        if artifact in {
            FINAL_NPZ,
            COMBINED_FEATURE_TABLE_CSV_GZ,
        }
        else DRIVE_MANIFEST_DIR
    )

    destination = destination_root / artifact.name
    atomic_copy(artifact, destination)

    copied_hash = sha256_file(destination)
    original_hash = sha256_file(artifact)

    if copied_hash != original_hash:
        raise RuntimeError(
            f"Drive persistence checksum failed: "
            f"{artifact.name}"
        )

print("=" * 86)
print("[CELL 11 SUMMARY]")
print("=" * 86)
print(f"X shape                  : {X.shape}")
print(f"y shape                  : {y.shape}")
print(f"Subjects                 : {len(np.unique(subject_ids_np))}")
print(f"Repetition groups        : {len(np.unique(repetition_ids_np))}")
print(f"Class distribution       : {class_distribution}")
print(f"Partition distribution   : {partition_distribution}")
print(f"Feature arms             : {actual_arm_dimensions}")
print(f"Nonfinite in X           : {np.size(X) - np.isfinite(X).sum()}")
print(f"NPZ SHA-256              : {NPZ_SHA256}")
print(f"NPZ                      : {FINAL_NPZ}")
print(f"Drive NPZ                : {DRIVE_OUTPUT_DIR / FINAL_NPZ.name}")
print("[PASS] CELL 11 hoàn tất: primary 42-D NPZ đã được xuất.")

# %% [markdown]
# ## 9. Final validation gate
#
# CELL 12 reload NPZ bằng `allow_pickle=False`, kiểm lại dimensions, hashes, split leakage, feature arms và governance flags.  
# Browser download mặc định tắt vì file đã được lưu bền vững trong Google Drive.

# %%
# === CELL 12: Final gate, Drive verification and optional download ===

DOWNLOAD_TO_BROWSER = False

required_npz_keys = {
    "X",
    "y",
    "groups",
    "subject_id",
    "repetition_ids",
    "window_id",
    "record_id",
    "split_names",
    "feature_names",
    "channel_names",
    "class_order",
    "F_TD8_indices",
    "F_SP6_indices",
    "F_ALL14_indices",
    "F_NO_MOMENTS12_indices",
    "schema_version",
    "dataset_view_id",
    "feature_set_version",
    "training_allowed",
    "model_fitting_allowed",
    "test_set_opened",
    "pooled_training_allowed",
}

with np.load(FINAL_NPZ, allow_pickle=False) as final_data:
    missing_keys = required_npz_keys - set(final_data.files)
    if missing_keys:
        raise RuntimeError(
            f"FINAL NPZ missing keys: {sorted(missing_keys)}"
        )

    X_check = final_data["X"]
    y_check = final_data["y"]
    groups_check = final_data["groups"]
    repetitions_check = final_data["repetition_ids"]
    windows_check = final_data["window_id"]
    splits_check = final_data["split_names"]
    feature_names_check = final_data["feature_names"]

    if X_check.shape != (row_count, 42):
        raise RuntimeError(
            f"FINAL X shape mismatch: {X_check.shape}"
        )

    for array_name, array in [
        ("y", y_check),
        ("groups", groups_check),
        ("repetition_ids", repetitions_check),
        ("window_id", windows_check),
        ("split_names", splits_check),
    ]:
        if array.shape[0] != X_check.shape[0]:
            raise RuntimeError(
                f"FINAL row mismatch: {array_name}"
            )

    if feature_names_check.shape != (42,):
        raise RuntimeError(
            "FINAL feature_names must have 42 columns."
        )

    if not np.isfinite(X_check).all():
        raise RuntimeError(
            "FINAL X contains nonfinite values."
        )

    if len(np.unique(windows_check)) != X_check.shape[0]:
        raise RuntimeError(
            "FINAL window_id uniqueness failed."
        )

    if bool(final_data["training_allowed"].item()):
        raise RuntimeError(
            "Governance violation: training_allowed=True"
        )

    if bool(final_data["model_fitting_allowed"].item()):
        raise RuntimeError(
            "Governance violation: model_fitting_allowed=True"
        )

    if bool(final_data["test_set_opened"].item()):
        raise RuntimeError(
            "Governance violation: test_set_opened=True"
        )

    if bool(
        final_data["pooled_training_allowed"].item()
    ):
        raise RuntimeError(
            "Governance violation: pooled_training_allowed=True"
        )

    train_groups = set(
        groups_check[splits_check == "train"].tolist()
    )
    validation_groups = set(
        groups_check[
            splits_check == "validation"
        ].tolist()
    )

    if train_groups & validation_groups:
        raise RuntimeError(
            "FINAL subject leakage detected."
        )

    final_arm_dimensions = {
        "F-TD8": int(
            final_data["F_TD8_indices"].size
        ),
        "F-SP6": int(
            final_data["F_SP6_indices"].size
        ),
        "F-ALL14": int(
            final_data["F_ALL14_indices"].size
        ),
        "F-NO-MOMENTS12": int(
            final_data[
                "F_NO_MOMENTS12_indices"
            ].size
        ),
    }

    if final_arm_dimensions != expected_arm_dimensions:
        raise RuntimeError(
            f"FINAL arm dimensions: {final_arm_dimensions}"
        )

drive_npz = DRIVE_OUTPUT_DIR / FINAL_NPZ.name
drive_feature_table = (
    DRIVE_OUTPUT_DIR
    / COMBINED_FEATURE_TABLE_CSV_GZ.name
)
drive_evidence = (
    DRIVE_MANIFEST_DIR
    / DAY31_EVIDENCE_JSON.name
)

for required_path in [
    drive_npz,
    drive_feature_table,
    drive_evidence,
]:
    if not required_path.exists():
        raise RuntimeError(
            f"Drive artifact missing: {required_path}"
        )

if sha256_file(drive_npz) != NPZ_SHA256:
    raise RuntimeError(
        "Drive NPZ checksum does not match runtime NPZ."
    )

final_gate = {
    "schema_version": "day31-final-gate.v1",
    "created_at_utc": utc_now_iso(),
    "status": "PASS",
    "dataset_id": DATASET_ID,
    "dataset_view_id": DATASET_VIEW_ID,
    "matrix_shape": list(X_check.shape),
    "matrix_sha256": NPZ_SHA256,
    "subjects": int(len(np.unique(groups_check))),
    "repetition_groups": int(
        len(np.unique(repetitions_check))
    ),
    "classes": {
        str(label): int(count)
        for label, count in zip(
            *np.unique(y_check, return_counts=True)
        )
    },
    "partitions": {
        str(partition): int(count)
        for partition, count in zip(
            *np.unique(
                splits_check,
                return_counts=True,
            )
        )
    },
    "feature_arms": final_arm_dimensions,
    "subject_leakage": False,
    "matrix_nonfinite_count": 0,
    "test_set_opened": False,
    "training_allowed": False,
    "model_fitting_allowed": False,
    "drive_checksum_verified": True,
    "next_step": (
        "Issue Day32 authorization, then run "
        "separate grouped classical baselines."
    ),
}

write_json(final_gate, FINAL_GATE_JSON)
atomic_copy(
    FINAL_GATE_JSON,
    DRIVE_MANIFEST_DIR / FINAL_GATE_JSON.name,
)

print("=" * 86)
print("[CELL 12 FINAL GATE]")
print("=" * 86)
print(f"Status                  : PASS")
print(f"Matrix shape            : {X_check.shape}")
print(f"Subjects                : {len(np.unique(groups_check))}")
print(f"Repetition groups       : {len(np.unique(repetitions_check))}")
print(f"Subject leakage         : False")
print(f"Nonfinite matrix values : 0")
print(f"Training allowed        : False")
print(f"Test set opened         : False")
print(f"Drive checksum verified : True")
print(f"Runtime NPZ             : {FINAL_NPZ}")
print(f"Drive NPZ               : {drive_npz}")
print(f"Final gate              : {FINAL_GATE_JSON}")
print(
    "[PASS] Day 27→31 Mendeley ETL hoàn tất. "
    "Chưa có model nào được train."
)

if DOWNLOAD_TO_BROWSER:
    try:
        from google.colab import files
        files.download(str(FINAL_NPZ))
        files.download(str(DAY31_EVIDENCE_JSON))
        print("[INFO] Browser download triggered.")
    except ImportError:
        print(
            "[INFO] Không chạy trong Colab; "
            "không thể trigger browser download."
        )
else:
    print(
        "[INFO] Browser download đang tắt. "
        "Output đã được lưu bền vững trong Google Drive."
    )

# %% [markdown]
# # Expected outputs
#
# ## Runtime
#
# ```text
# /content/data/mendeley-4channel-hand-gesture-v2/
# ├── indexes/
# │   ├── all-segments-index.csv
# │   ├── metadata-index-mendeley-primary.csv
# │   └── window-index-mendeley-primary.csv.gz
# ├── features/
# │   ├── by-subject/
# │   ├── exclusions-by-subject/
# │   ├── day31-feature-table-channel-wide.csv.gz
# │   └── day31-feature-exclusion-report.csv
# ├── matrices/
# │   ├── day31-mendeley-primary-fall14.npz
# │   └── day31-feature-column-manifest.json
# └── manifests/
#     ├── cell5-preflight.json
#     ├── subject-split-manifest.csv
#     ├── subject-split-manifest.json
#     ├── day31-colab-etl-evidence.json
#     └── day31-final-gate.json
# ```
#
# ## Google Drive
#
# ```text
# /content/drive/MyDrive/MyoLab-AI-data/
# └── mendeley-4channel-hand-gesture-v2/
#     ├── manifests/
#     └── outputs/
#         ├── day31-mendeley-primary-fall14.npz
#         └── day31-feature-table-channel-wide.csv.gz
# ```
#
# ## Expected primary dimensions
#
# ```text
# 40 subjects
# 800 target gesture-repetition records
# 47,200 windows before QC exclusion
# 3 primary channels
# 14 features/channel
# 42 features/window
# ```
#
# Day 32 must still issue its own authorization before model fitting.
