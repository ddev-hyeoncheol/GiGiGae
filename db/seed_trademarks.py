"""
상표 데이터 + CLIP 이미지 임베딩 DB 적재 스크립트

사용법:
  python db/seed_trademarks.py [xlsx_path]           # 단일 파일
  python db/seed_trademarks.py db/data/*.xlsx        # 여러 파일 glob
  python db/seed_trademarks.py --batch-size 64       # 배치 크기 조정
  python db/seed_trademarks.py --reset               # 기존 데이터 삭제 후 적재
"""

import argparse
import os
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import clip
import numpy as np
import psycopg2
import psycopg2.extras
import torch
from PIL import Image
from tqdm import tqdm

# ── 설정 ──
IMAGE_DIR = Path(__file__).parent.parent / "image"
DB_IMAGE_BASE = "/data/image"  # Docker 내부 공유 경로

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gigigae")
DB_USER = os.getenv("DB_USER", "gigigae")
DB_PASS = os.getenv("DB_PASS", "gigigae")


# ── 1) xlsx XML 직접 파싱 ──
def parse_xlsx(xlsx_path: Path) -> tuple[list[dict], dict[int, str]]:
    """xlsx → (records, {row_idx: image_rel_path}) 반환"""
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

    headers = rows_data.get(1, {})
    col_map = {col: name for col, name in headers.items()}

    records = []
    for r in range(2, max(rows_data.keys()) + 1):
        if r not in rows_data:
            continue
        row = {col_map.get(c, f"col{c}"): v for c, v in rows_data[r].items()}
        row["_row_idx"] = r
        records.append(row)

    # 이미지 매핑 (drawing → row)
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
        pass  # 이미지 없는 xlsx

    return records, row_image_map


# ── 2) 이미지 추출 ──
def extract_images(
    xlsx_path: Path, row_image_map: dict[int, str], image_dir: Path, offset: int = 0
) -> dict[int, Path]:
    """xlsx에서 이미지 추출, {row_idx: local_path} 반환"""
    zf = zipfile.ZipFile(xlsx_path)
    extracted: dict[int, Path] = {}

    for row_idx in sorted(row_image_map.keys()):
        media_path = row_image_map[row_idx]
        zip_path = "xl/" + media_path.replace("../", "")

        seq = offset + row_idx
        out_name = f"{seq:06d}.jpg"
        out_path = image_dir / out_name

        try:
            data = zf.read(zip_path)
            with open(out_path, "wb") as f:
                f.write(data)
            extracted[row_idx] = out_path
        except KeyError:
            pass

    return extracted


# ── 3) CLIP 배치 임베딩 ──
def build_embeddings_batch(
    image_paths: dict[int, Path],
    batch_size: int = 32,
) -> dict[int, np.ndarray]:
    """이미지 배치 처리 → CLIP 벡터 (512차원)"""
    if not image_paths:
        return {}

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"  CLIP device: {device}, batch_size: {batch_size}")

    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()

    # 이미지 로드 + 전처리
    indices = sorted(image_paths.keys())
    all_tensors: list[tuple[int, torch.Tensor]] = []

    for idx in indices:
        try:
            img = Image.open(image_paths[idx]).convert("RGB")
            tensor = preprocess(img).unsqueeze(0)
            all_tensors.append((idx, tensor))
        except Exception:
            pass

    # 배치 인퍼런스
    embeddings: dict[int, np.ndarray] = {}
    batches = [all_tensors[i : i + batch_size] for i in range(0, len(all_tensors), batch_size)]

    for batch in tqdm(batches, desc="  Embedding", unit="batch"):
        batch_indices = [b[0] for b in batch]
        batch_tensors = torch.cat([b[1] for b in batch], dim=0).to(device)

        with torch.no_grad():
            vecs = model.encode_image(batch_tensors)
            vecs = vecs / vecs.norm(dim=-1, keepdim=True)

        vecs_np = vecs.cpu().numpy()
        for i, idx in enumerate(batch_indices):
            embeddings[idx] = vecs_np[i]

    return embeddings


# ── 4) 날짜 파싱 ──
def parse_date(val: str | None) -> str | None:
    if not val:
        return None
    return val.replace(".", "-") if "." in val else val


# ── 5) DB 적재 (배치 INSERT) ──
def seed_db(
    records: list[dict],
    embeddings: dict[int, np.ndarray],
    extracted_images: dict[int, Path],
    reset: bool = False,
):
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
            %s, %s, %s
        )
        ON CONFLICT (application_no) DO UPDATE SET
            name = EXCLUDED.name,
            image_path = COALESCE(EXCLUDED.image_path, trademarks.image_path),
            image_embedding = COALESCE(EXCLUDED.image_embedding, trademarks.image_embedding)
    """

    rows_to_insert = []
    for rec in records:
        row_idx = rec["_row_idx"]
        app_no = rec.get("출원(국제등록)번호", "")
        if not app_no:
            continue

        name = rec.get("명칭", "")
        nice_class = rec.get("상품분류", "")
        legal_status = rec.get("상태", "")
        app_date = parse_date(rec.get("출원(국제등록)일자"))
        reg_no = rec.get("등록번호", "")
        reg_date = parse_date(rec.get("등록일자"))
        applicant = rec.get("출원인", "")
        right_holder = rec.get("최종권리자", "")
        pub_no = rec.get("출원공고번호", "")
        pub_date = parse_date(rec.get("출원공고일자"))
        design_code = rec.get("도형코드", "")

        # 이미지 경로
        img_path = extracted_images.get(row_idx)
        image_db_path = f"{DB_IMAGE_BASE}/{img_path.name}" if img_path else None

        # 임베딩 벡터
        vec = embeddings.get(row_idx)
        vec_str = None
        if vec is not None:
            vec_str = "[" + ",".join(f"{v:.6f}" for v in vec) + "]"

        rows_to_insert.append((
            name, nice_class or None, app_no, legal_status or None,
            app_date, reg_no or None, reg_date,
            applicant or None, right_holder or None,
            pub_no or None, pub_date,
            design_code or None, image_db_path, vec_str,
        ))

    # 배치 실행
    BATCH = 500
    for i in range(0, len(rows_to_insert), BATCH):
        batch = rows_to_insert[i : i + BATCH]
        psycopg2.extras.execute_batch(cur, sql, batch, page_size=BATCH)
        print(f"  DB insert: {min(i + BATCH, len(rows_to_insert))}/{len(rows_to_insert)}")

    conn.commit()
    cur.close()
    conn.close()


# ── main ──
def main():
    parser = argparse.ArgumentParser(description="상표 데이터 + CLIP 임베딩 DB 적재")
    parser.add_argument("files", nargs="*", default=[], help="xlsx 파일 경로 (여러 개 가능)")
    parser.add_argument("--batch-size", type=int, default=32, help="CLIP 배치 크기 (기본 32)")
    parser.add_argument("--reset", action="store_true", help="기존 데이터 삭제 후 적재")
    parser.add_argument("--skip-embedding", action="store_true", help="임베딩 생성 건너뛰기")
    args = parser.parse_args()

    # 파일 경로 결정
    xlsx_files = [Path(f) for f in args.files] if args.files else list(Path("db/data").glob("*.xlsx"))
    if not xlsx_files:
        print("xlsx 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"대상 파일: {len(xlsx_files)}개")
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    total_start = time.time()
    global_offset = 0
    first_file = True

    for xlsx_path in xlsx_files:
        print(f"\n{'='*60}")
        print(f"처리 중: {xlsx_path.name}")
        print(f"{'='*60}")

        # 1) 파싱
        t0 = time.time()
        records, row_image_map = parse_xlsx(xlsx_path)
        print(f"[1/4] 파싱 완료: {len(records)}건 ({time.time()-t0:.1f}s)")

        # 2) 이미지 추출
        t0 = time.time()
        extracted = extract_images(xlsx_path, row_image_map, IMAGE_DIR, offset=global_offset)
        print(f"[2/4] 이미지 추출: {len(extracted)}건 ({time.time()-t0:.1f}s)")

        # 3) CLIP 임베딩
        t0 = time.time()
        if args.skip_embedding:
            embeddings = {}
            print("[3/4] 임베딩 건너뛰기")
        else:
            embeddings = build_embeddings_batch(extracted, batch_size=args.batch_size)
            print(f"[3/4] 임베딩 완료: {len(embeddings)}건 ({time.time()-t0:.1f}s)")

        # 4) DB 적재
        t0 = time.time()
        seed_db(records, embeddings, extracted, reset=(args.reset and first_file))
        print(f"[4/4] DB 적재 완료: {len(records)}건 ({time.time()-t0:.1f}s)")

        global_offset += len(records) + 1
        first_file = False

    elapsed = time.time() - total_start
    print(f"\n총 소요 시간: {elapsed:.1f}s ({elapsed/60:.1f}m)")


if __name__ == "__main__":
    main()
