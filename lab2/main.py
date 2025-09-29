# main.py — Lab 2, Variant 4
# Tasks:
#   1) Count titles longer than 30 chars
#   2) Search by author with Variant-4 filter (Price <= 200 rubles)
#   3) Generate 20 bibliography lines "<author>. <title> - <year>" and save to a txt with numbering
#   4) Parse currency.xml into dict {NumCode(int) -> CharCode}
#   5) Extra: unique publishers (no duplicates) and Top-20 most popular (by Downloads)

import argparse
from pathlib import Path
import random
import re
import pandas as pd
import xml.etree.ElementTree as ET

# Try to use tabulate for nice left-aligned printing; fallback gracefully
try:
    from tabulate import tabulate
    HAVE_TABULATE = True
except Exception:
    HAVE_TABULATE = False

# ---------------- Configuration ----------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

BOOKS_FILE = "books-en.csv"
XML_FILE   = "currency.xml"
BIBLIO_OUT = "bibliography.txt"

# ---------------- CSV reading & normalization ----------------
def read_books(path: str) -> pd.DataFrame:
    """
    Read semicolon-separated CSV, handle UTF-8/BOM, coerce important numeric columns.
    Expected columns:
      ISBN;Book-Title;Book-Author;Year-Of-Publication;Publisher;Downloads;Price
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{path} not found.")

    try:
        df = pd.read_csv(p, sep=";", encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        df = pd.read_csv(p, sep=";", encoding="utf-8", on_bad_lines="skip")

    expected = [
        "Book-Title", "Book-Author", "Year-Of-Publication",
        "Publisher", "Downloads", "Price"
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise KeyError(f"Missing expected columns: {missing}. Found: {list(df.columns)}")

    # normalize price
    df["Price_num"] = (
        df["Price"].astype(str)
        .str.replace("\u00A0", " ", regex=False)
        .str.replace(r"[^\d,.\-]", "", regex=True)
        .str.replace(",", ".", regex=False)
    )
    df["Price_num"] = pd.to_numeric(df["Price_num"], errors="coerce")

    # year + downloads numeric
    df["Year_num"] = pd.to_numeric(df["Year-Of-Publication"], errors="coerce")
    df["Downloads_num"] = pd.to_numeric(df["Downloads"], errors="coerce")

    return df

# ---------------- Core tasks ----------------
def count_long_titles(df: pd.DataFrame, threshold: int = 30) -> int:
    return int((df["Book-Title"].astype(str).str.len() > threshold).sum())

def search_author_variant4(df: pd.DataFrame, author_query: str) -> pd.DataFrame:
    mask_author = df["Book-Author"].astype(str).str.contains(author_query, case=False, na=False)
    mask_price = df["Price_num"] <= 200
    res = df[mask_author & mask_price].copy()
    cols = ["Book-Title", "Book-Author", "Year-Of-Publication", "Price"]
    return res[cols].reset_index(drop=True)

def make_bibliography(df: pd.DataFrame, n: int = 20, out_path: str = BIBLIO_OUT):
    sample = df.sample(min(n, len(df)), random_state=RANDOM_SEED)
    lines = []
    for i, (_, row) in enumerate(sample.iterrows(), start=1):
        author = str(row["Book-Author"])
        title  = str(row["Book-Title"])
        year   = str(row["Year-Of-Publication"])
        piece = f"{author}. {title} - {year}".strip().rstrip("- ").strip()
        lines.append(f"{i}. {piece}")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    return out_path, lines

# ---------------- Robust XML parsing ----------------
def _read_text_guess_encoding(p: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1251", "latin1"):
        try:
            return p.read_text(encoding=enc)
        except Exception:
            continue
    return p.read_bytes().decode("utf-8", errors="ignore")

def _fix_malformed_xml(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    text = re.sub(r"&(?!(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);)", "&amp;", text)
    return text

def parse_currency_variant4(xml_path: str = XML_FILE):
    p = Path(xml_path)
    if not p.exists():
        raise FileNotFoundError(f"{xml_path} not found.")

    try:
        root = ET.parse(p).getroot()
    except ET.ParseError:
        raw = _read_text_guess_encoding(p)
        fixed = _fix_malformed_xml(raw)
        root = ET.fromstring(fixed)

    out = {}
    for v in root.findall(".//Valute"):
        num = v.findtext("NumCode")
        code = v.findtext("CharCode")
        if not (num and code):
            continue
        try:
            out[int(num)] = code.strip()
        except ValueError:
            continue
    return out

# ---------------- Extras ----------------
def unique_publishers(df: pd.DataFrame):
    items = sorted(set(map(str.strip, df["Publisher"].dropna().astype(str))))
    return "Unique publishers", items

def top20_popular(df: pd.DataFrame):
    top = (
        df.dropna(subset=["Downloads_num"])
          .sort_values("Downloads_num", ascending=False)
          .head(20)
          .reset_index(drop=True)
    )
    cols = ["Book-Title", "Book-Author", "Year-Of-Publication", "Downloads"]
    return "Downloads", top[cols]

# ---------------- CLI / Main ----------------
def main():
    parser = argparse.ArgumentParser(description="Lab 2 — Variant 4")
    parser.add_argument("-f", "--file", default=BOOKS_FILE, help="Path to CSV (default: books-en.csv)")
    parser.add_argument("-a", "--author", default="Grisham", help="Author substring to search (default: Grisham)")
    parser.add_argument("-n", "--nrefs", type=int, default=20, help="Number of bibliography lines (default: 20)")
    parser.add_argument("--biblio", default=BIBLIO_OUT, help="Output path for bibliography txt")
    args = parser.parse_args()

    # 1) CSV
    df = read_books(args.file)

    # 1) long titles
    n_long = count_long_titles(df)
    print(f"[1] Titles longer than 30 chars: {n_long}")

    # 2) search by author
    res = search_author_variant4(df, args.author)
    print(f"[2] Results for author '{args.author}' with Price <= 200: {len(res)} (showing up to 10)")
    print(res.head(10).to_string(index=False))

    # 3) bibliography
    out_path, lines = make_bibliography(df, n=args.nrefs, out_path=args.biblio)
    print(f"[3] Bibliography written to '{out_path}'. First 3 lines:")
    print("\n".join(lines[:3]))

    # 4) xml
    num2char = parse_currency_variant4(XML_FILE)
    print(f"[4] currency.xml parsed: {len(num2char)} items. Sample:", dict(list(num2char.items())[:5]))

    # 5) extras
    title, items = unique_publishers(df)
    print(f"[5a] {title} ({len(items)}) — first 10: {items[:10]}")
    metric, top = top20_popular(df)
    print(f"[5b] Top-20 most popular (metric: {metric}):")

    # Pretty, left-aligned print
    if HAVE_TABULATE:
        print(tabulate(top.values.tolist(), headers=top.columns.tolist(), tablefmt="plain", stralign="left"))
    else:
        # fallback: Markdown (also left-aligned and readable)
        try:
            print(top.to_markdown(index=False))
        except Exception:
            # last resort: to_string with left justification
            print(top.to_string(index=False, justify="left"))

if __name__ == "__main__":
    main()
