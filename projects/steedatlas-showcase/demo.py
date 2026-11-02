"""SteedAtlas public MINI showcase: synthetic evidence, no external services.

This clean-room demo is NOT the full private application and does not
validate actual historical truth or perform LLM reasoning.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from math import log
import re
from time import monotonic
import unicodedata


TRANSLATE = str.maketrans("雲駒馬記載與", "云驹马记载与")


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).translate(TRANSLATE).casefold()


def terms(text: str) -> list[str]:
    s = normalize(text)
    han = "".join(re.findall(r"[\u3400-\u9fff]", s))
    return ([han[i:i+2] for i in range(len(han)-1)] or ([han] if han else [])) + re.findall(r"[a-z0-9]+", s)


def digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Passage:
    key: str
    entity: str
    source: str
    genre: str
    revision: int
    text: str
    quote: str
    span: tuple[int, int]
    hash: str
    relation: str
    proposition: str
    lineage: str
    verification: str = "SYNTHETIC_ANNOTATION"
    rights: str = "SYNTHETIC_CC0"
    visibility: str = "PUBLIC"
    active: bool = True


def sample(key: str, entity: str, source: str, genre: str, text: str, quote: str,
           relation: str = "MENTIONS", proposition: str = "", lineage: str = "demo", verification: str = "SYNTHETIC_ANNOTATION") -> Passage:
    start = text.index(quote)
    return Passage(key, entity, source, genre, 1, text, quote, (start, start+len(quote)),
                   digest(text), relation, proposition, lineage, verification)


def synthetic_corpus() -> list[Passage]:
    return [
        sample("a1", "red", "甲史", "HISTORY", "甲史记载：赤云随骑手甲出行。", "赤云随骑手甲出行", "SUPPORTS", "rider-red", "edition-a"),
        sample("a2", "red", "乙史", "HISTORY", "乙史记载：赤云并未随骑手甲出行。", "赤云并未随骑手甲出行", "CONTRADICTS", "rider-red", "edition-b"),
        sample("a3", "red", "甲史转载", "HISTORY", "甲史转载：赤云随骑手甲出行。", "赤云随骑手甲出行", "SUPPORTS", "rider-red", "edition-a"),
        sample("b1", "black", "丙小说", "LITERATURE", "丙小说描绘：玄驹越过山谷。", "玄驹越过山谷", lineage="fiction-c", verification="MACHINE_VERIFIED"),
        sample("c1", "blue", "丁纪", "HISTORY", "丁纪记载：苍岚马出现在集市。", "苍岚马出现在集市", lineage="edition-d", verification="MACHINE_VERIFIED"),
    ]


ALIASES = {"red": ("赤云", "赤雲", "赤云马"), "black": ("玄驹", "玄駒"), "blue": ("苍岚", "蒼嵐")}


def entity_ids(query: str) -> set[str]:
    s = normalize(query)
    return {k for k, vals in ALIASES.items() if any(normalize(v) in s for v in vals)}


def validate(p: Passage) -> tuple[bool, str]:
    if not p.active or p.visibility != "PUBLIC":
        return False, "RESTRICTED"
    if p.rights != "SYNTHETIC_CC0":
        return False, "RIGHTS_UNKNOWN"
    if p.revision < 1 or not p.key or not p.source:
        return False, "INVALID_REFERENCE"
    if p.hash != digest(p.text):
        return False, "HASH_MISMATCH"
    a, b = p.span
    if not (0 <= a < b <= len(p.text)) or p.text[a:b] != p.quote:
        return False, "QUOTE_MISMATCH"
    if p.verification == "MACHINE_VERIFIED" and p.relation != "MENTIONS":
        return False, "MENTION_NOT_FACT_PROOF"
    if p.verification not in ("MACHINE_VERIFIED", "SYNTHETIC_ANNOTATION"):
        return False, "UNKNOWN_VERIFICATION"
    return True, "EXACT_QUOTE_NOT_HISTORICAL_TRUTH"


def bm25(query: str, documents: list[str]) -> list[float]:
    bags = [Counter(terms(d)) for d in documents]
    mean_length = sum(sum(x.values()) for x in bags) / max(1, len(bags))
    result = []
    for bag in bags:
        size = sum(bag.values())
        score = 0.0
        for token in set(terms(query)):
            tf = bag[token]
            if not tf:
                continue
            df = sum(token in other for other in bags)
            idf = log(1 + (len(bags)-df+0.5)/(df+0.5))
            score += idf*tf*2.2/(tf+1.2*(0.25+0.75*size/max(1,mean_length)))
        result.append(score)
    return result


def opposes(a: Passage, b: Passage) -> bool:
    return bool(a.entity == b.entity and a.proposition and a.proposition == b.proposition
                and {a.relation,b.relation} == {"SUPPORTS","CONTRADICTS"}
                and a.genre == b.genre == "HISTORY")


class EvidenceRepository:
    def __init__(self, passages: list[Passage] | None = None):
        self.passages = passages if passages is not None else synthetic_corpus()

    def search(self, query: str, *, scope: str = "all", limit: int = 4) -> dict:
        if scope not in ("all", "historical", "literary") or not 1 <= limit <= 20:
            raise ValueError("Invalid scope or limit")
        asked = entity_ids(query)
        allowed = [p for p in self.passages if validate(p)[0]
                   and (not asked or p.entity in asked)
                   and (scope != "historical" or p.genre == "HISTORY")
                   and (scope != "literary" or p.genre == "LITERATURE")]
        scores = bm25(query, [p.text+" "+p.source for p in allowed])
        ranked = [p for score,p in sorted(zip(scores,allowed),key=lambda x:(-x[0],x[1].key)) if score > 0]
        pairs = [(a,b) for a in ranked for b in ranked if a.key < b.key and opposes(a,b)]
        chosen: list[Passage] = []
        def add(p: Passage):
            if len(chosen) < limit and p.key not in {x.key for x in chosen}:
                chosen.append(p)
        for a,b in pairs:
            add(a);add(b)
        for ent in sorted(asked):
            r=next((p for p in ranked if p.entity==ent),None)
            if r: add(r)
        for p in ranked:
            if p.lineage not in {x.lineage for x in chosen}: add(p)
        for p in ranked: add(p)
        seen={p.key for p in chosen}
        return {"hits":[{"id":p.key,"entity":p.entity,"source":p.source,"genre":p.genre,
                          "revision":p.revision,"quote":p.quote,"span":list(p.span),
                          "relation":p.relation,"verification":p.verification,"lineage":p.lineage} for p in chosen],
                "coverage":{"missing_entities":sorted(asked-{p.entity for p in chosen}),
                            "known_opposition_pairs":len(pairs),
                            "opposition_truncated":any(a.key not in seen or b.key not in seen for a,b in pairs),
                            "independent_support_groups":len({p.lineage for p in chosen if p.relation=="SUPPORTS"}),
                            "limit":limit},
                "notice":"Synthetic excerpts demonstrate provenance mechanics, not historical truth."}

    def answer(self, query: str, *, scope: str = "all", limit: int = 4) -> dict:
        result=self.search(query,scope=scope,limit=limit)
        hits=result["hits"]
        if not hits or re.search("出生|生日|哪年哪月|唯一主人|最后结局",normalize(query)):
            mode="INSUFFICIENT"
        elif ({x["relation"] for x in hits}>={"SUPPORTS","CONTRADICTS"}
              and result["coverage"]["known_opposition_pairs"]):
            mode="CONFLICT"
        elif all(x["genre"]=="LITERATURE" for x in hits):
            mode="LITERARY_ATTRIBUTED"
        else: mode="SOURCE_ATTRIBUTED"
        return {"mode":mode,"citations":hits,"coverage":result["coverage"],
                "generation_mode":"RETRIEVAL_ONLY","model":None,
                "message":"Only synthetic sources are used; a verified quote is not proof of history."}


class ResearchWorkflow:
    def __init__(self,repo:EvidenceRepository,max_calls:int=5,max_seconds:float=3.):
        self.repo=repo
        self.max_calls=max_calls
        self.max_seconds=max_seconds
        self.started=monotonic()
        self.trace:list[dict]=[]

    def call(self,tool:str,**args):
        if tool not in {"search_entities","search_evidence","compare_sources","check_coverage"}:
            raise PermissionError("Tool not permitted")
        if len(self.trace)>=self.max_calls or monotonic()-self.started>self.max_seconds:
            raise RuntimeError("Research budget exhausted")
        start=monotonic()
        try:
            if tool=="search_entities": value=sorted(entity_ids(args["query"]))
            elif tool=="search_evidence": value=self.repo.search(args["query"],limit=args.get("limit",4))
            elif tool=="compare_sources": value=sorted({(p.source,p.lineage) for p in self.repo.passages if p.source in args["sources"]})
            else: value={"passages":len(self.repo.passages),"entities":len(ALIASES)}
        except Exception as exc:
            self.trace.append({"tool":tool,"status":"FAILED","error_type":type(exc).__name__})
            raise
        self.trace.append({"tool":tool,"status":"OK","elapsed_ms":round((monotonic()-start)*1000,3)})
        return value

    def run(self,query:str)->dict:
        ents=self.call("search_entities",query=query)
        evidence=self.call("search_evidence",query=query)
        sources=self.call("compare_sources",sources={x["source"] for x in evidence["hits"]})
        counts=self.call("check_coverage")
        return {"mode":"RULE_BASED","entities":ents,"evidence":evidence,"source_groups":sources,
                "coverage":counts,"trace":self.trace,"model_calls":0,"paid_cost":0}


def main():
    parser=argparse.ArgumentParser(description="Offline synthetic SteedAtlas portfolio demo")
    parser.add_argument("--query",default="赤云归属")
    parser.add_argument("--scope",choices=("all","historical","literary"),default="all")
    parser.add_argument("--limit",type=int,default=3)
    parser.add_argument("--agent",action="store_true")
    args=parser.parse_args()
    repo=EvidenceRepository()
    data=ResearchWorkflow(repo).run(args.query) if args.agent else repo.answer(args.query,scope=args.scope,limit=args.limit)
    print(json.dumps(data,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
