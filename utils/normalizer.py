import pandas as pd

def _to_number(x):
    if x is None:
        return None
    try:
        s = str(x).strip()
        if s == "" or s.lower() == "nan":
            return None
        s = s.replace(",", "")
        return float(s)
    except Exception:
        return None

def normalize_po_items(header: dict, items_raw: pd.DataFrame) -> pd.DataFrame:
    if items_raw is None or len(items_raw) == 0:
        return pd.DataFrame(columns=[
            "po_no","supplier_name","seq","product_code","product_name_cn","product_name_pt","ncm",
            "qty","unit_price_rmb","line_total_rmb"
        ])

    df = items_raw.copy()

    df["po_no"] = header.get("po_no")
    df["supplier_name"] = header.get("supplier_name")

    if "qty" in df.columns:
        df["qty"] = df["qty"].apply(_to_number)
    else:
        df["qty"] = None

    if "unit_price_rmb" in df.columns:
        df["unit_price_rmb"] = df["unit_price_rmb"].apply(_to_number)
    else:
        df["unit_price_rmb"] = None

    # 文字欄位
    for col in ["ncm","product_code","product_name_cn","product_name_pt"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = ""

    df["line_total_rmb"] = (df["qty"].fillna(0) * df["unit_price_rmb"].fillna(0)).round(4)

    # 欄位排序
    df = df[[
        "po_no","supplier_name","seq","product_code","product_name_cn","product_name_pt","ncm",
        "qty","unit_price_rmb","line_total_rmb"
    ]]

    return df
