"""CLIP 이미지 임베딩 플러그인 — 싱글톤으로 모델 1회 로딩"""

import os
from pathlib import Path

import clip
import numpy as np
import torch
from PIL import Image

# 볼륨 마운트된 모델 경로 우선, 없으면 기본 다운로드
MODEL_PATH = Path("/data/model/ViT-B-32.pt")


class ClipPlugin:
    _instance: "ClipPlugin | None" = None

    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_source = str(MODEL_PATH) if MODEL_PATH.exists() else "ViT-B/32"
        self.model, self.preprocess = clip.load(model_source, device=self.device)
        self.model.eval()

    @classmethod
    def get(cls) -> "ClipPlugin":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_image(self, image: Image.Image) -> list[float]:
        """PIL Image → 512차원 정규화 벡터"""
        tensor = self.preprocess(image.convert("RGB")).unsqueeze(0).to(self.device)
        with torch.no_grad():
            vec = self.model.encode_image(tensor)
            vec = vec / vec.norm(dim=-1, keepdim=True)
        return vec.cpu().numpy().flatten().tolist()
