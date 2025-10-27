
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from backend.infixtopostfix import infix_to_postfix
from backend.kmap import postfix_to_simplified_SOP_kmap_2d

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("kmap_main")

app = FastAPI(title="K-Map Simplifier API", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimplifyRequest(BaseModel):
    infix: str = Field(..., description="Boolean expression in infix notation (e.g. A+B'C)")
    return_kmap: bool = Field(False, description="Include K-map 2D array in response")

@app.post("/simplify")
async def simplify_boolean(req: SimplifyRequest):
    logger.info("Received simplify request: infix=%s return_kmap=%s", req.infix, req.return_kmap)
    try:
        infix_expr = req.infix.replace(" ", "")
        postfix_expr = infix_to_postfix(infix_expr)
        logger.info("Converted infix to postfix: %s -> %s", infix_expr, postfix_expr)

        simplified, vars_list, minterms, kmap = postfix_to_simplified_SOP_kmap_2d(postfix_expr)
        logger.info(
            "Simplification result: simplified=%s vars=%s minterms=%s kmap_present=%s",
            simplified, vars_list, minterms, bool(kmap)
        )

        return {
            "success": True,
            "infix": req.infix,
            "postfix": postfix_expr,
            "simplified": simplified,
            "variables": vars_list,
            "minterms": sorted(minterms) if minterms else [],
            "kmap": kmap if req.return_kmap else None,
            "message": "Simplification successful"
        }
    except ValueError as e:
        logger.exception("Invalid input")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected internal error")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)