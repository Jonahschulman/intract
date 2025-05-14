from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONTRACT_ADDRESS = "0x802ae625C2bdac1873B8bbb709679CC401F57abc"
ALCHEMY_URL = "https://eth-sepolia.g.alchemy.com/v2/3h-55W2oiNtyO-rWGRA5QT95DhzlbDRA"

@app.post("/api/intract/verify")
async def verify_intract(request: Request):
    try:
        body = await request.json()
        address = body.get("address", "").lower()
        if not address:
            return { "error": { "code": 1, "message": "Address not provided" }, "data": { "result": False } }

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getAssetTransfers",
            "params": [{
                "fromAddress": address,
                "toAddress": CONTRACT_ADDRESS.lower(),
                "category": ["external", "erc20", "erc721", "erc1155"],
                "withMetadata": False,
                "maxCount": "0x64",
                "order": "desc"
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(ALCHEMY_URL, json=payload)
            data = response.json().get("result", {})
            has_interacted = len(data.get("transfers", [])) > 0

        return { "error": { "code": 0, "message": "" }, "data": { "result": has_interacted } }

    except Exception as e:
        return { "error": { "code": 500, "message": str(e) }, "data": { "result": False } }
