from httpx import AsyncClient


async def get_bboxes(img: str) -> list[str]:
    async with AsyncClient() as client:
        result = await client.post(
            "http://localhost:8000/bbox",
            params={"img": img},
            timeout=60,
        )

    result.raise_for_status()
    json = result.json()

    return json
