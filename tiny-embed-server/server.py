from itertools import batched

import torch
from fastapi import FastAPI
from PIL import Image, ImageFile
from transformers import AutoModel, AutoProcessor

app = FastAPI()

ImageFile.LOAD_TRUNCATED_IMAGES = True

# MODEL = "google/siglip2-so400m-patch16-naflex"
MODEL = "facebook/dinov2-base"
batch_size = 128

model = AutoModel.from_pretrained(MODEL, device_map="auto").eval()
processor = AutoProcessor.from_pretrained(MODEL, use_fast=True)


@torch.no_grad()
def get_embeddings(images: list[ImageFile.ImageFile]):
    inputs = processor(images=images, return_tensors="pt").to(model.device)
    outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0].cpu().tolist()


@app.post("/embed")
def embed(images: list[str]):
    result = []

    for batch in batched(images, batch_size):
        imgs = [Image.open(path) for path in batch]
        features = get_embeddings(imgs)
        result += features

    return result
