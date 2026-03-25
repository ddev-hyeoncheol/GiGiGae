FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 (git for CLIP install)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# torch CPU 버전 (경량)
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# CLIP (모델은 /data/model 볼륨에서 로드)
RUN pip install --no-cache-dir git+https://github.com/openai/CLIP.git

# 앱 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]
