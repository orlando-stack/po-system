from __future__ import annotations

import pandas as pd


def _as_str(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s == "":
        return None
    return s


def _as_float(v):
    if pd.isna(v) or v == "":
        return None
    try:
        return float(v)
    except Exception:
        # 有些是字串帶逗號
        try:
            return float(str(v).replace(",", "").strip())
        except Exception:
            return None


def _as_int_like_str(v):
    """
    像 NCM 7315.0 這種，轉成 '7315'
    """
    if pd.isna(v):
        return None
    try:
        f = float(v)
        if f.is_integer():
            return str(int(f))
        return str(v).strip()
    except Exception:
        return str(v).strip() if str(v).strip() else None


def normalize_po_items(header: dict, items_raw: pd.DataFrame) -> pd.DataFrame:
    """
    你的 Excel 欄位（我在檔案裡看到）：
    序, 货号, 中文品名, 产品叙述, 规格, 件数, 装箱数/件, 订单数量, ...
    单价 (RMB), 总金额 (RMB), 提单显示品名, 提单NCM, 葡文品名
    """
    df = items_raw.copy()

    # 欄位名可能有些空格差異，先做一次 strip
    df.columns = [str(c).strip() for c in df.columns]

    def col(*names):
        for n in names:
            if n in df.columns:
                return n
        return None

    c_seq = col("序", "序号")
    c_code = col("货号", "產品編號", "产品编号")
    c_cn = col("中文品名", "品名(中文)")
    c_pt = col("葡文品名", "品名(葡文)", "葡文名稱")
    c_ncm = col("提单NCM", "NCM", "提单 NCM")
    c_qty = col("订单数量", "数量", "訂單數量")
    c_price = col("单价 (RMB)", "单价(RMB)", "单价")
    c_total = col("总金额 (RMB)", "总金额(RMB)", "总金额")

    out = pd.DataFrame()
    out["seq"] = df[c_seq].apply(_as_float) if c_seq else None
    out["product_code"] = df[c_code].apply(_as_str) if c_code else None
    out["product_name_cn"] = df[c_cn].apply(_as_str) if c_cn else None
    out["product_name_pt"] = df[c_pt].apply(_as_str) if c_pt else None
    out["ncm"] = df[c_ncm].apply(_as_int_like_str) if c_ncm else None
    out["qty"] = df[c_qty].apply(_as_float) if c_qty else None
    out["unit_price_rmb"] = df[c_price].apply(_as_float) if c_price else None
    out["line_total_rmb"] = df[c_total].apply(_as_float) if c_total else None

    # seq 轉 int（顯示更好看）
    if "seq" in out.columns:
        out["seq"] = out["seq"].apply(lambda x: int(x) if x is not None and float(x).is_integer() else x)

    return out
