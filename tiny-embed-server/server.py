from itertools import batched

import torch
from fastapi import FastAPI
from PIL import Image, ImageFile
from transformers import AutoModel, AutoProcessor

from extractor import find_all_cards_from_obbox

app = FastAPI()

ImageFile.LOAD_TRUNCATED_IMAGES = True

MODEL = "facebook/dinov3-vits16-pretrain-lvd1689m"

processor = AutoProcessor.from_pretrained(MODEL, use_fast=True)
model = AutoModel.from_pretrained(
    MODEL,
    dtype=torch.bfloat16,
    device_map="auto",
    attn_implementation="sdpa",
)


@torch.inference_mode()
def get_embeddings(images: list[ImageFile.ImageFile]):
    inputs = processor(images=images, return_tensors="pt").to(model.device)
    outputs = model(**inputs)
    embeddings = outputs.pooler_output

    return embeddings.float().cpu().tolist()


def load_images(paths: tuple[str, ...]):
    imgs = []

    for path in paths:
        img = Image.open(path)

        if img.mode != "RGB":
            img = img.convert("RGB")

        imgs.append(img)

    return imgs


@app.post("/embed")
async def embed(images: list[str], batch_size: int = 128):
    result = []

    for batch in batched(images, batch_size):
        imgs = load_images(batch)
        features = get_embeddings(imgs)
        result += features

    return result


@app.post("/bbox")
async def bbox(img: str):
    return find_all_cards_from_obbox(img)
