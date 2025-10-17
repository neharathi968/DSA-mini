# kmap_backend_fixed.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple, Set, Dict, Any
import re
import math
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("kmap_backend_fixed")

app = FastAPI(title="K-Map Simplifier (fixed)", version="1.0")

# ---------------- Models ----------------
class SimplifyRequest(BaseModel):
    postfix: str = Field(..., description="Boolean expression in postfix (RPN).")
    return_kmap: bool = Field(False, description="Include 2D K-map (rows x cols) in response")

class SimplifyResponse(BaseModel):
    success: bool
    simplified: str
    variables: List[str]
    minterms: Optional[List[int]] = None
    kmap: Optional[List[List[int]]] = None
    message: Optional[str] = None

# ---------------- Utilities ----------------
def tokenize_postfix(expr: str) -> List[str]:
    expr = expr.strip()
    if ' ' in expr:
        return [t for t in expr.split() if t != ""]
    return list(expr)

def eval_postfix(tokens: List[str], valuation: Dict[str, bool]) -> bool:
    stack: List[bool] = []
    for tok in tokens:
        if tok == '':
            continue
        if re.fullmatch(r"[A-Za-z]", tok):
            stack.append(bool(valuation.get(tok, False)))
        elif tok in ('~', '!'):
            if not stack:
                raise ValueError("Malformed postfix: missing operand for NOT")
            a = stack.pop(); stack.append(not a)
        elif tok in ('&', '.'):
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for AND")
            b = stack.pop(); a = stack.pop(); stack.append(a and b)
        elif tok in ('|', '+'):
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for OR")
            b = stack.pop(); a = stack.pop(); stack.append(a or b)
        elif tok == '^':
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for XOR")
            b = stack.pop(); a = stack.pop(); stack.append(bool(a) ^ bool(b))
        elif tok == '>':  # implication A -> B = (not A) or B
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for IMPLIES")
            b = stack.pop(); a = stack.pop(); stack.append((not a) or b)
        elif tok == '=':  # equivalence
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for EQUIV")
            b = stack.pop(); a = stack.pop(); stack.append(a == b)
        else:
            raise ValueError(f"Unknown token '{tok}'")
    if len(stack) != 1:
        raise ValueError("Invalid postfix expression (stack length != 1 at end)")
    return bool(stack[0])

def gray_code(n: int) -> List[str]:
    if n <= 0:
        return ['']
    if n == 1:
        return ['0', '1']
    prev = gray_code(n - 1)
    return ['0' + p for p in prev] + ['1' + p for p in reversed(prev)]

# ---------------- Build K-map ----------------
def build_kmap_and_minterms(postfix_expr: str, max_vars: int = 8):
    tokens = tokenize_postfix(postfix_expr)
    vars_list = sorted({t for t in tokens if re.fullmatch(r"[A-Za-z]", t)})  # single-letter vars
    n = len(vars_list)

    # constant expression (no variables)
    if n == 0:
        val = eval_postfix(tokens, {})
        return None, vars_list, None, None, ([], {}), val

    if n > max_vars:
        raise ValueError(f"Supports up to {max_vars} variables only.")

    # split into row and col bits
    r_bits = math.ceil(n / 2)
    c_bits = n - r_bits
    row_gray = gray_code(r_bits)
    col_gray = gray_code(c_bits)

    # pad gray strings to exact lengths (important when c_bits == 0 or r_bits == 0)
    row_gray = [s.zfill(r_bits) for s in row_gray]
    col_gray = [s.zfill(c_bits) for s in col_gray]

    rows = len(row_gray)
    cols = len(col_gray)

    # initialize 2D kmap
    kmap: List[List[int]] = [[0 for _ in range(cols)] for _ in range(rows)]
    cell_to_minterm: Dict[Tuple[int,int], int] = {}
    minterm_to_cell: Dict[int, Tuple[int,int]] = {}
    minterms_list: List[int] = []

    for i, rcode in enumerate(row_gray):
        for j, ccode in enumerate(col_gray):
            bits = (rcode + ccode)
            # bits length should equal n; if not, pad on left (defensive)
            if len(bits) != n:
                bits = bits.zfill(n)[-n:]
            # map bits -> variables in vars_list order
            valuation: Dict[str, bool] = {}
            for idx, var in enumerate(vars_list):
                # if bits shorter (defensive), assume '0'
                b = bits[idx] if idx < len(bits) else '0'
                valuation[var] = (b == '1')
            val = eval_postfix(tokens, valuation)
            kmap[i][j] = 1 if val else 0
            # minterm index: interpret the bits string as binary with vars_list order as MSB->LSB
            try:
                m = int(bits, 2)
            except ValueError:
                m = 0
            cell_to_minterm[(i,j)] = m
            minterm_to_cell[m] = (i,j)
            if val:
                minterms_list.append(m)

    # return kmap, vars_list, row_gray, col_gray, minterms_list, cell_to_minterm, None (no const_val)
    return kmap, vars_list, row_gray, col_gray, minterms_list, cell_to_minterm, None

# ---------------- Block checks ----------------
def all_ones_in_block(kmap: List[List[int]], top_i:int, left_j:int, height:int, width:int) -> bool:
    rows = len(kmap); cols = len(kmap[0])
    for di in range(height):
        i = (top_i + di) % rows
        for dj in range(width):
            j = (left_j + dj) % cols
            if kmap[i][j] != 1:
                return False
    return True

def collect_block_minterms(cell_to_minterm: Dict[Tuple[int,int],int], top_i:int, left_j:int, height:int, width:int) -> Set[int]:
    rows = max(k[0] for k in cell_to_minterm.keys()) + 1
    cols = max(k[1] for k in cell_to_minterm.keys()) + 1
    s: Set[int] = set()
    for di in range(height):
        i = (top_i + di) % rows
        for dj in range(width):
            j = (left_j + dj) % cols
            s.add(cell_to_minterm[(i,j)])
    return s

# ---------------- Petrick & literal conversion (unchanged logic) ----------------
def petrick_method_generic(minterm_to_implicants: Dict[int, List[int]], implicant_cost: Dict[int, int]):
    product = []
    for m, implicant_list in sorted(minterm_to_implicants.items()):
        product.append(set(implicant_list))

    solutions = [frozenset()]
    for clause in product:
        new_sols = set()
        for sol in solutions:
            for imp in clause:
                new = set(sol); new.add(imp)
                new_sols.add(frozenset(new))
        # prune dominated supersets
        pruned = set()
        sorted_sols = sorted(new_sols, key=lambda s: (len(s), sorted(s)))
        for s in sorted_sols:
            if not any(p.issubset(s) and p != s for p in pruned):
                pruned.add(s)
        solutions = pruned
        if len(solutions) > 3000:
            return None
    if not solutions:
        return None
    min_size = min(len(s) for s in solutions)
    candidates = [s for s in solutions if len(s) == min_size]
    best = min(candidates, key=lambda s: sum(implicant_cost.get(i, 0) for i in s))
    return set(best)

def minterms_to_literal(minterms: Set[int], vars_list: List[str]) -> str:
    n = len(vars_list)
    bits_list = [format(m, f'0{n}b') for m in sorted(minterms)]
    common = []
    for pos in range(n):
        col = [b[pos] for b in bits_list]
        if all(x == col[0] for x in col):
            common.append(col[0])
        else:
            common.append('-')
    parts = []
    for bit, var in zip(common, vars_list):
        if bit == '1':
            parts.append(var)
        elif bit == '0':
            parts.append(f'~{var}')
    if not parts:
        return "1"
    return " & ".join(parts)

# ---------------- Simplification (K-map grouping + Petrick) ----------------
def postfix_to_simplified_SOP_kmap_2d(postfix_expr: str, max_vars: int = 8):
    kmap, vars_list, row_gray, col_gray, all_minterms, cell_to_minterm, const_val = build_kmap_and_minterms(postfix_expr, max_vars)
    if const_val is not None:
        return ("1" if const_val else "0"), vars_list, all_minterms, kmap
    n = len(vars_list)
    if n == 0:
        return "0", vars_list, all_minterms, kmap

    rows = len(kmap); cols = len(kmap[0])

    # collect candidate power-of-two blocks (area, height, width)
    blocks = []
    max_h_pow = int(math.log2(rows)) if rows > 0 else 0
    max_w_pow = int(math.log2(cols)) if cols > 0 else 0
    sizes = []
    for h_pow in range(max_h_pow + 1):
        for w_pow in range(max_w_pow + 1):
            area = (2 ** h_pow) * (2 ** w_pow)
            height = 2 ** h_pow; width = 2 ** w_pow
            sizes.append((area, height, width))
    sizes = sorted(sizes, key=lambda x: -x[0])

    for area, height, width in sizes:
        for i in range(rows):
            for j in range(cols):
                if all_ones_in_block(kmap, i, j, height, width):
                    covered = collect_block_minterms(cell_to_minterm, i, j, height, width)
                    blocks.append((frozenset(covered), (i,j,height,width)))

    # dedupe by coverage set (frozenset key)
    unique_blocks_dict: Dict[frozenset, Tuple[int,int,int,int]] = {}
    for covered, meta in blocks:
        unique_blocks_dict.setdefault(covered, meta)
    unique_blocks = list(unique_blocks_dict.keys())

    # remove strict subsets (non-prime)
    non_redundant: List[frozenset] = []
    covered_list = list(unique_blocks)
    for i, b in enumerate(covered_list):
        is_subset = False
        for j, other in enumerate(covered_list):
            if i == j: continue
            if b.issubset(other) and b != other:
                is_subset = True
                break
        if not is_subset:
            non_redundant.append(b)

    implicants = non_redundant

    # build minterm->implicant map and implicant costs
    minterm_to_implicants: Dict[int, List[int]] = defaultdict(list)
    implicant_cost: Dict[int, int] = {}
    for idx, imp in enumerate(implicants):
        if len(imp) == 0:
            n_fixed = 0
        else:
            bits_list = [format(m, f'0{n}b') for m in sorted(imp)]
            fixed = 0
            for pos in range(n):
                col = [b[pos] for b in bits_list]
                if all(x == col[0] for x in col):
                    fixed += 1
            n_fixed = fixed
        implicant_cost[idx] = max(1, n_fixed)
        for m in imp:
            minterm_to_implicants[m].append(idx)

    if not implicants:
        return "0", vars_list, all_minterms, kmap

    # essential implicants
    selected: Set[int] = set()
    covered_minterms: Set[int] = set()
    for m, ilist in minterm_to_implicants.items():
        if len(ilist) == 1:
            selected.add(ilist[0])
    for s in selected:
        covered_minterms |= set(implicants[s])

    remaining_minterms = set(all_minterms) - covered_minterms

    # Petrick for remaining
    if remaining_minterms:
        reduced_chart: Dict[int, List[int]] = {}
        for m in remaining_minterms:
            reduced_chart[m] = [i for i in minterm_to_implicants[m]]
        used_implicants = set()
        for lst in reduced_chart.values():
            used_implicants.update(lst)
        reduced_cost = {i: implicant_cost[i] for i in used_implicants}
        petrick_sol = petrick_method_generic(reduced_chart, reduced_cost)
        if petrick_sol is None:
            # greedy fallback
            rem = set(remaining_minterms)
            while rem:
                best = None; best_cover = set()
                for i in used_implicants:
                    cover = set(implicants[i]) & rem
                    if len(cover) > len(best_cover):
                        best_cover = cover; best = i
                if best is None:
                    break
                selected.add(best)
                rem -= best_cover
        else:
            selected |= petrick_sol

    # convert selected implicants to literal strings
    terms: List[str] = []
    for i in sorted(selected):
        lit = minterms_to_literal(set(implicants[i]), vars_list)
        terms.append(lit)

    if not terms:
        return "0", vars_list, all_minterms, kmap
    formatted = " | ".join(f"({t})" if " & " in t else t for t in terms)
    return formatted, vars_list, all_minterms, kmap

# ---------------- API Endpoints ----------------
@app.post("/simplify", response_model=SimplifyResponse)
async def simplify(req: SimplifyRequest):
    logger.info("Received simplify request")
    if not req.postfix or not req.postfix.strip():
        raise HTTPException(status_code=400, detail="postfix expression required")
    try:
        simplified, vars_list, minterms, kmap = postfix_to_simplified_SOP_kmap_2d(req.postfix)
        return SimplifyResponse(
            success=True,
            simplified=simplified,
            variables=vars_list,
            minterms=sorted(minterms) if minterms else [],
            kmap=kmap if req.return_kmap else None,
            message="OK"
        )
    except ValueError as e:
        logger.exception("ValueError while simplifying")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("kmap_backend_fixed:app", host="127.0.0.1", port=8000, log_level="info")
