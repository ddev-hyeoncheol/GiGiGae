"""
이미지 추출 + DB image_path 업데이트 (CLIP 임베딩 제외, 빠른 실행)

사용법:
  python db/seed_images.py              # db/data/*.xlsx 전체
  python db/seed_images.py --reset      # 기존 이미지 삭제 후 재추출
"""

import argparse
import os
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import psycopg2

IMAGE_DIR = Path(__file__).parent.parent / "image"
DB_IMAGE_BASE = "/data/image"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gigigae")
DB_USER = os.getenv("DB_USER", "gigigae")
DB_PASS = os.getenv("DB_PASS", "gigigae")


def parse_xlsx_with_images(xlsx_path: Path) -> list[tuple[str, str]]:
    """xlsx에서 (출원번호, 이미지zip경로) 쌍 추출"""
    zf = zipfile.ZipFile(xlsx_path)
    ns_ss = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ns_xdr = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
    ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    ns_r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

    # shared strings
    ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    shared_strings = []
    for si in ss_root.findall(f"{{{ns_ss}}}si"):
        t = si.find(f"{{{ns_ss}}}t")
        if t is not None and t.text:
            shared_strings.append(t.text)
        else:
            parts = [r.text or "" for r in si.findall(f".//{{{ns_ss}}}t")]
            shared_strings.append("".join(parts))

    # sheet data
    sheet_root = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))

    def parse_ref(ref: str):
        m = re.match(r"([A-Z]+)(\d+)", ref)
        col_str, row = m.group(1), int(m.group(2))
        col = 0
        for c in col_str:
            col = col * 26 + (ord(c) - ord("A") + 1)
        return row, col

    rows_data: dict[int, dict[int, str | None]] = {}
    for c_el in sheet_root.findall(f".//{{{ns_ss}}}c"):
        row, col = parse_ref(c_el.attrib["r"])
        t = c_el.attrib.get("t", "")
        v = c_el.find(f"{{{ns_ss}}}v")
        val = None
        if v is not None and v.text:
            val = shared_strings[int(v.text)] if t == "s" else v.text
        rows_data.setdefault(row, {})[col] = val

    # 헤더 행 탐색
    header_row = 1
    for r in sorted(rows_data.keys()):
        vals = [v for v in rows_data[r].values() if v]
        if any("출원" in str(v) for v in vals):
            header_row = r
            break

    headers = rows_data.get(header_row, {})
    col_map = {col: name for col, name in headers.items()}

    # 출원번호 컬럼 인덱스 찾기
    app_no_col = None
    for col, name in col_map.items():
        if "출원" in name and "번호" in name:
            app_no_col = col
            break

    if app_no_col is None:
        return []

    # row → 출원번호 매핑
    row_to_app_no: dict[int, str] = {}
    for r in range(header_row + 1, max(rows_data.keys()) + 1):
        if r not in rows_data:
            continue
        app_no = rows_data[r].get(app_no_col, "")
        if app_no:
            row_to_app_no[r] = app_no

    # 이미지 매핑 (drawing row → image file)
    row_image_map: dict[int, str] = {}
    try:
        rels_xml = zf.read("xl/drawings/_rels/drawing1.xml.rels")
        rels_root = ET.fromstring(rels_xml)
        rid_to_file = {
            rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_root
        }

        drawing_xml = zf.read("xl/drawings/drawing1.xml")
        dr_root = ET.fromstring(drawing_xml)

        for tag in ["oneCellAnchor", "twoCellAnchor"]:
            for anc in dr_root.findall(f"{{{ns_xdr}}}{tag}"):
                from_el = anc.find(f"{{{ns_xdr}}}from")
                if from_el is None:
                    continue
                row = int(from_el.find(f"{{{ns_xdr}}}row").text)
                blip = anc.find(f".//{{{ns_a}}}blip")
                if blip is None:
                    continue
                embed = blip.attrib.get(f"{{{ns_r}}}embed")
                if embed and embed in rid_to_file:
                    row_image_map[row] = rid_to_file[embed]
    except (KeyError, ET.ParseError):
        return []

    # (출원번호, zip내_이미지경로) 쌍 생성
    pairs = []
    for row_idx, media_path in row_image_map.items():
        # drawing row는 0-based, data row는 1-based
        # drawing의 row는 셀 행(0-based) → +1 해서 sheet row와 맞춤
        data_row = row_idx + 1
        app_no = row_to_app_no.get(data_row)
        if app_no:
            zip_path = "xl/" + media_path.replace("../", "")
            pairs.append((app_no, zip_path))

    return pairs


def main():
    parser = argparse.ArgumentParser(description="이미지 추출 + DB image_path 업데이트")
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("--reset", action="store_true", help="기존 이미지 파일 삭제")
    args = parser.parse_args()

    xlsx_files = [Path(f) for f in args.files] if args.files else sorted(Path("db/data").glob("*.xlsx"))
    if not xlsx_files:
        print("xlsx 파일을 찾을 수 없습니다.")
        sys.exit(1)

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    if args.reset:
        for f in IMAGE_DIR.glob("*.jpg"):
            f.unlink()
        for f in IMAGE_DIR.glob("*.png"):
            f.unlink()
        print("기존 이미지 삭제 완료")

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    conn.autocommit = False
    cur = conn.cursor()

    print(f"대상 파일: {len(xlsx_files)}개")
    total_start = time.time()
    total_extracted = 0
    total_updated = 0
    seq = 1

    for i, xlsx_path in enumerate(xlsx_files, 1):
        zf = zipfile.ZipFile(xlsx_path)
        pairs = parse_xlsx_with_images(xlsx_path)

        extracted = 0
        updated = 0
        for app_no, zip_path in pairs:
            out_name = f"{seq:06d}.jpg"
            out_path = IMAGE_DIR / out_name
            try:
                data = zf.read(zip_path)
                with open(out_path, "wb") as f:
                    f.write(data)
                extracted += 1

                db_path = f"{DB_IMAGE_BASE}/{out_name}"
                cur.execute(
                    "UPDATE trademarks SET image_path = %s WHERE application_no = %s",
                    (db_path, app_no),
                )
                if cur.rowcount > 0:
                    updated += 1
                seq += 1
            except KeyError:
                pass

        if extracted > 0:
            conn.commit()
            total_extracted += extracted
            total_updated += updated
            print(f"[{i}/{len(xlsx_files)}] {xlsx_path.name}: 이미지 {extracted}건, DB 업데이트 {updated}건")
        else:
            if i % 50 == 0:
                print(f"[{i}/{len(xlsx_files)}] 진행 중...")

    conn.commit()
    cur.close()
    conn.close()

    elapsed = time.time() - total_start
    print(f"\n완료: 이미지 {total_extracted}건 추출, DB {total_updated}건 업데이트 ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
