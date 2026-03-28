# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import logging
import os

from backend.infixtopostfix import infix_to_postfix
from backend.kmap import postfix_to_simplified_SOP_kmap_2d
from backend.expressiontree import exptree
from backend.tree_to_graph import tree_to_graph
from backend.graph_to_reactflow import save_circuit_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kmap_main")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://logic-gate-simulator.onrender.com",
        "https://dsa-mini-eight.vercel.app/", # Add your specific Vercel URL here
        "http://localhost:5173", # Good to keep for local frontend dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class SimplifyRequest(BaseModel):
    infix: str
    return_kmap: bool = False
    return_circuit: bool = False

@app.post("/simplify")
async def simplify_boolean(req: SimplifyRequest):
    try:
        infix_expr = req.infix.replace(" ", "")
        postfix_expr = infix_to_postfix(infix_expr)
        simplified, vars_list, minterms, kmap = postfix_to_simplified_SOP_kmap_2d(postfix_expr)

        circuit_url = None
        if req.return_circuit and simplified not in ["0", "1"]:
            simp_postfix = infix_to_postfix(simplified)
            tree = exptree(simp_postfix)
            nodes, root_gate = tree_to_graph(tree)
            if root_gate:
                circuit_url = save_circuit_json(root_gate)

        return {
            "success": True,
            "infix": req.infix,
            "postfix": postfix_expr,
            "simplified": simplified,
            "variables": vars_list,
            "minterms": sorted(minterms) if minterms else [],
            "kmap": kmap if req.return_kmap else None,
            "circuit_url": circuit_url,
            "message": "Success"
        }
    except Exception as e:
        logger.exception("Error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
