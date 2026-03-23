"""KIPRIS xlsx 상표권 데이터를 PostgreSQL에 적재하는 스크립트

사용법:
    cd db
    python load_data.py [--data-dir ./data] [--db-url postgresql://gigigae:gigigae@localhost:5432/gigigae]
"""

import argparse
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import psycopg

SCRIPT_DIR = Path(__file__).parent
CREATE_TABLE_SQL = SCRIPT_DIR / "init.sql"

COLUMN_MAP = {
    "B": "name",
    "C": "nice_class",
    "D": "application_no",
    "E": "application_date",
    "G": "registration_no",
    "H": "registration_date",
    "P": "legal_status",
    "S": "trademark_type",
    "Y": "english_name",
}

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DATE_COLUMNS = {"application_date", "registration_date"}
HEADER_SKIP_ROWS = 8
BATCH_SIZE = 1000

INSERT_SQL = """
    INSERT INTO trademarks (name, nice_class, application_no, application_date,
        registration_no, registration_date, legal_status, trademark_type, english_name)
    VALUES (%(name)s, %(nice_class)s, %(application_no)s, %(application_date)s,
        %(registration_no)s, %(registration_date)s, %(legal_status)s,
        %(trademark_type)s, %(english_name)s)
    ON CONFLICT (application_no) DO NOTHING
"""


def parse_xlsx(filepath: Path) -> list[dict]:
    """xlsx 파일에서 상표 데이터 추출 (zipfile + XML 직접 파싱)"""
    records = []

    with zipfile.ZipFile(filepath) as z:
        ss_xml = z.read("xl/sharedStrings.xml")
        ss_root = ET.fromstring(ss_xml)
        strings = [t.text or "" for si in ss_root for t in si]

        sheet_xml = z.read("xl/worksheets/sheet1.xml")
        sheet_root = ET.fromstring(sheet_xml)
        rows = sheet_root.findall(f".//{{{NS}}}row")

        for row in rows:
            row_num = int(row.attrib.get("r", "0"))
            if row_num <= HEADER_SKIP_ROWS:
                continue

            record = {}
            for cell in row.findall(f"{{{NS}}}c"):
                ref = cell.attrib.get("r", "")
                col_letter = "".join(c for c in ref if c.isalpha())

                if col_letter not in COLUMN_MAP:
                    continue

                val_el = cell.find(f"{{{NS}}}v")
                if val_el is None:
                    continue

                raw = val_el.text or ""
                if cell.attrib.get("t") == "s":
                    raw = strings[int(raw)] if raw else ""

                db_col = COLUMN_MAP[col_letter]
                if db_col in DATE_COLUMNS:
                    record[db_col] = parse_date(raw)
                else:
                    record[db_col] = raw[:500] if raw else None

            if record.get("name") and record.get("application_no"):
                for col in COLUMN_MAP.values():
                    record.setdefault(col, None)
                records.append(record)

    return records


def parse_date(value: str) -> datetime | None:
    """다양한 날짜 포맷 파싱"""
    if not value:
        return None
    for fmt in ("%Y.%m.%d", "%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description="KIPRIS xlsx → PostgreSQL 적재")
    parser.add_argument(
        "--data-dir",
        default=str(SCRIPT_DIR / "data"),
        help="xlsx 파일 디렉토리 경로",
    )
    parser.add_argument(
        "--db-url",
        default="postgresql://gigigae:gigigae@localhost:5432/gigigae",
        help="PostgreSQL 접속 URL",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    xlsx_files = sorted(data_dir.glob("*.xlsx"))
    if not xlsx_files:
        print(f"[ERROR] xlsx 파일 없음: {data_dir}")
        sys.exit(1)

    print(f"[INFO] DB: {args.db_url}")
    print(f"[INFO] xlsx 파일 {len(xlsx_files)}개 발견")

    with psycopg.connect(args.db_url) as conn:
        with conn.cursor() as cur:
            init_sql = CREATE_TABLE_SQL.read_text()
            cur.execute(init_sql)
            conn.commit()
            print("[INFO] 테이블 생성 완료")

        total = 0
        for i, filepath in enumerate(xlsx_files, 1):
            print(f"[{i}/{len(xlsx_files)}] {filepath.name} 파싱 중...", end=" ")
            records = parse_xlsx(filepath)
            print(f"{len(records)}건", end=" → ")

            with conn.cursor() as cur:
                for j in range(0, len(records), BATCH_SIZE):
                    batch = records[j : j + BATCH_SIZE]
                    cur.executemany(INSERT_SQL, batch)
                conn.commit()

            total += len(records)
            print("적재 완료")

        print(f"\n[DONE] 총 {total}건 적재 완료")


if __name__ == "__main__":
    main()
