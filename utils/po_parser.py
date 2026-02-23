from __future__ import annotations
import pandas as pd


def parse_po_excel(uploaded_file):
    """
    强力版：
    - 用 pandas 直接读整张 Excel
    - 自动识别 header
    - 自动识别明细表头
    """

    # 读取 Excel
    df_all = pd.read_excel(uploaded_file, header=None)

    # ---------- 找 header ----------
    po_no = None
    supplier = None

    for i in range(min(20, len(df_all))):
        row = df_all.iloc[i].astype(str)

        if "买方合同号" in " ".join(row):
            for cell in row:
                if "PO-" in str(cell):
                    po_no = str(cell).strip()

        if "厂商名称" in " ".join(row):
            idx = row[row.str.contains("厂商名称")].index[0]
            supplier = str(df_all.iloc[i, idx + 1]).strip()

    header = {
        "po_no": po_no,
        "supplier_name": supplier
    }

    # ---------- 找明细表头 ----------
    header_row_index = None

    for i in range(len(df_all)):
        row = df_all.iloc[i].astype(str)
        text = " ".join(row)

        if "序" in text and "货号" in text and "中文品名" in text:
            header_row_index = i
            break

    if header_row_index is None:
        return header, pd.DataFrame()

    df_items = pd.read_excel(
        uploaded_file,
        header=header_row_index
    )

    # 删除全空行
    df_items = df_items.dropna(how="all")

    return header, df_items
