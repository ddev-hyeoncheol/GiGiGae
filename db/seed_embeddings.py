"""
DB에 저장된 이미지에 대해 CLIP 임베딩 생성 + image_embedding 업데이트

사용법:
  python db/seed_embeddings.py                # 임베딩 없는 레코드만 처리
  python db/seed_embeddings.py --reset        # 전체 재생성
  python db/seed_embeddings.py --batch-size 64
"""

import argparse
import os
import time
from pathlib import Path

import clip
import numpy as np
import psycopg2
import torch
from PIL import Image
from tqdm import tqdm

IMAGE_DIR = Path(__file__).parent.parent / "image"
MODEL_DIR = Path(__file__).parent.parent / "model"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gigigae")
DB_USER = os.getenv("DB_USER", "gigigae")
DB_PASS = os.getenv("DB_PASS", "gigigae")


def main():
    parser = argparse.ArgumentParser(description="CLIP 임베딩 생성")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--reset", action="store_true", help="전체 재생성")
    args = parser.parse_args()

    # CLIP 모델 로드
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"CLIP device: {device}, batch_size: {args.batch_size}")

    # 모델 캐시 디렉토리
    model_cache = MODEL_DIR if MODEL_DIR.exists() else None
    if model_cache:
        os.environ["TORCH_HOME"] = str(model_cache)

    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()
    print("CLIP 모델 로드 완료")

    # DB에서 이미지 경로 조회
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()

    if args.reset:
        cur.execute("SELECT application_no, image_path FROM trademarks WHERE image_path IS NOT NULL")
    else:
        cur.execute("SELECT application_no, image_path FROM trademarks WHERE image_path IS NOT NULL AND image_embedding IS NULL")

    rows = cur.fetchall()
    print(f"처리 대상: {len(rows)}건")

    if not rows:
        print("처리할 이미지가 없습니다.")
        return

    # 배치 처리
    total_start = time.time()
    updated = 0
    failed = 0

    for i in range(0, len(rows), args.batch_size):
        batch_rows = rows[i : i + args.batch_size]
        tensors = []
        valid_rows = []

        for app_no, db_path in batch_rows:
            # /data/image/000001.jpg → image/000001.jpg
            filename = db_path.split("/")[-1]
            local_path = IMAGE_DIR / filename

            if not local_path.exists():
                failed += 1
                continue

            try:
                img = Image.open(local_path).convert("RGB")
                tensor = preprocess(img).unsqueeze(0)
                tensors.append(tensor)
                valid_rows.append(app_no)
            except Exception:
                failed += 1

        if not tensors:
            continue

        # 배치 인퍼런스
        batch_tensor = torch.cat(tensors, dim=0).to(device)
        with torch.no_grad():
            vecs = model.encode_image(batch_tensor)
            vecs = vecs / vecs.norm(dim=-1, keepdim=True)
        vecs_np = vecs.cpu().numpy()

        # DB 업데이트
        for j, app_no in enumerate(valid_rows):
            vec_str = "[" + ",".join(f"{v:.6f}" for v in vecs_np[j]) + "]"
            cur.execute(
                "UPDATE trademarks SET image_embedding = %s::vector WHERE application_no = %s",
                (vec_str, app_no),
            )
            updated += 1

        conn.commit()

        if (i // args.batch_size) % 50 == 0:
            elapsed = time.time() - total_start
            print(f"  진행: {updated}/{len(rows)} ({elapsed:.0f}s)")

    conn.commit()
    cur.close()
    conn.close()

    elapsed = time.time() - total_start
    print(f"\n완료: {updated}건 임베딩, {failed}건 실패 ({elapsed:.1f}s / {elapsed/60:.1f}m)")


if __name__ == "__main__":
    main()
