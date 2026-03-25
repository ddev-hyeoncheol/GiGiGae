"""
상표 데이터 DB 적재 (이미지/임베딩 제외, 텍스트 데이터만)

사용법:
  python db/seed_trademarks_lite.py                # db/data/*.xlsx 전체
  python db/seed_trademarks_lite.py --reset        # 기존 데이터 삭제 후 적재
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
import psycopg2.extras

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gigigae")
DB_USER = os.getenv("DB_USER", "gigigae")
DB_PASS = os.getenv("DB_PASS", "gigigae")


def parse_xlsx(xlsx_path: Path) -> list[dict]:
    """xlsx → records 반환 (이미지 매핑 제외)"""
    zf = zipfile.ZipFile(xlsx_path)
    ns_ss = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

    ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    shared_strings = []
    for si in ss_root.findall(f"{{{ns_ss}}}si"):
        t = si.find(f"{{{ns_ss}}}t")
        if t is not None and t.text:
            shared_strings.append(t.text)
        else:
            parts = [r.text or "" for r in si.findall(f".//{{{ns_ss}}}t")]
            shared_strings.append("".join(parts))

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

    # 헤더 행 자동 탐색 (순번, 상표명칭 등이 있는 행)
    header_row = 1
    for r in sorted(rows_data.keys()):
        vals = [v for v in rows_data[r].values() if v]
        if any("출원" in str(v) for v in vals):
            header_row = r
            break

    headers = rows_data.get(header_row, {})
    col_map = {col: name for col, name in headers.items()}

    records = []
    for r in range(header_row + 1, max(rows_data.keys()) + 1):
        if r not in rows_data:
            continue
        row = {col_map.get(c, f"col{c}"): v for c, v in rows_data[r].items()}
        records.append(row)

    return records


def parse_date(val: str | None) -> str | None:
    if not val:
        return None
    return val.replace(".", "-") if "." in val else val


def seed_db(records: list[dict], reset: bool = False):
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    conn.autocommit = False
    cur = conn.cursor()

    if reset:
        cur.execute("DELETE FROM trademarks")
        print("  기존 데이터 삭제 완료")

    sql = """
        INSERT INTO trademarks (
            name, nice_class, application_no, legal_status,
            application_date, registration_no, registration_date,
            applicant, final_right_holder,
            publication_no, publication_date,
            design_code, image_path, image_embedding
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, NULL, NULL
        )
        ON CONFLICT (application_no) DO UPDATE SET
            name = EXCLUDED.name,
            nice_class = EXCLUDED.nice_class,
            legal_status = EXCLUDED.legal_status
    """

    # 출원인/최종권리자에서 이름만 추출 (순서/이름/... 형식)
    def extract_name(val: str | None) -> str | None:
        if not val:
            return None
        parts = val.split("/")
        return parts[1].strip() if len(parts) >= 2 else val.strip()

    rows_to_insert = []
    skipped = 0
    for rec in records:
        app_no = rec.get("출원(국제등록)번호", "")
        if not app_no:
            skipped += 1
            continue

        rows_to_insert.append((
            rec.get("상표명칭", ""),
            rec.get("상품분류", "") or None,
            app_no,
            rec.get("법적상태", "") or None,
            parse_date(rec.get("출원(국제등록)일자")),
            rec.get("등록번호", "") or None,
            parse_date(rec.get("등록일자")),
            extract_name(rec.get("출원인(순서/출원인/특허고객번호/개인법인구분/주소/대표자명)")),
            extract_name(rec.get("최종권리자(순서/최종권리자/특허고객번호/개인법인구분/주소/대표자명)")),
            rec.get("출원공고번호", "") or None,
            parse_date(rec.get("출원공고일자")),
            rec.get("비엔나코드", "") or None,
        ))

    BATCH = 1000
    for i in range(0, len(rows_to_insert), BATCH):
        batch = rows_to_insert[i : i + BATCH]
        psycopg2.extras.execute_batch(cur, sql, batch, page_size=BATCH)

    conn.commit()
    cur.close()
    conn.close()
    return len(rows_to_insert), skipped


def main():
    parser = argparse.ArgumentParser(description="상표 데이터 DB 적재 (텍스트만)")
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    xlsx_files = [Path(f) for f in args.files] if args.files else sorted(Path("db/data").glob("*.xlsx"))
    if not xlsx_files:
        print("xlsx 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"대상 파일: {len(xlsx_files)}개")
    total_start = time.time()
    total_inserted = 0
    total_skipped = 0
    first_file = True

    for i, xlsx_path in enumerate(xlsx_files, 1):
        t0 = time.time()
        records = parse_xlsx(xlsx_path)
        inserted, skipped = seed_db(records, reset=(args.reset and first_file))
        total_inserted += inserted
        total_skipped += skipped
        first_file = False
        print(f"[{i}/{len(xlsx_files)}] {xlsx_path.name}: {inserted}건 ({time.time()-t0:.1f}s)")

    elapsed = time.time() - total_start
    print(f"\n완료: {total_inserted}건 적재, {total_skipped}건 스킵 ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
