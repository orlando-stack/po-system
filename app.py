import streamlit as st
import pandas as pd

from utils.po_parser import parse_po_excel
from utils.normalizer import normalize_po_items

from db import ENGINE, get_db
from models import Base, POHeader, POItem

st.set_page_config(page_title="PO 系统（內部）", layout="wide")
st.title("📦 PO 系统（V1：PO 上傳 + 存庫 + 查詢）")

# 第一次运行会建表
Base.metadata.create_all(bind=ENGINE)

tab1, tab2 = st.tabs(["1) 上傳 PO", "2) 查詢 PO"])

with tab1:
    uploaded = st.file_uploader("上傳 PO Excel（.xlsx）", type=["xlsx"])
    if uploaded:
        try:
            with st.spinner("解析中..."):
                header, items_raw = parse_po_excel(uploaded)
                items = normalize_po_items(header, items_raw)

            st.success("解析成功 ✅")

            st.subheader("PO 抬頭（解析結果）")
            st.json(header)

            if not header.get("po_no"):
                st.error("我沒抓到 PO No（买方合同号）。我已把 header 全部印出來，請看哪個欄位是空的。")

            st.subheader("明細（原始）")
            st.dataframe(items_raw, use_container_width=True)

            st.subheader("明細（標準化）")
            st.dataframe(items, use_container_width=True)

            if st.button("💾 保存到資料庫", type="primary"):
                db = get_db()
                try:
                    po_no = (header.get("po_no") or "").strip()

                    if not po_no:
                        st.error("PO No 为空，不能保存。请确认 Excel 里有买方合同号（例如：PO-20260206-3）。")
                    else:
                        h = db.get(POHeader, po_no)
                        if not h:
                            h = POHeader(
                                po_no=po_no,
                                supplier_name=(header.get("supplier_name") or "").strip() or None,
                                order_date=header.get("order_date"),
                            )
                            db.add(h)
                        else:
                            h.supplier_name = (header.get("supplier_name") or "").strip() or None
                            h.order_date = header.get("order_date")

                        # 先清掉舊明細
                        db.query(POItem).filter(POItem.po_no == po_no).delete()

                        # 再寫入新明細
                        for _, r in items.iterrows():
                            db.add(POItem(
                                po_no=po_no,
                                seq=int(r["seq"]) if pd.notna(r["seq"]) and r["seq"] is not None else None,
                                product_code=str(r["product_code"]).strip() if pd.notna(r["product_code"]) and r["product_code"] is not None else None,
                                product_name_cn=str(r["product_name_cn"]).strip() if pd.notna(r["product_name_cn"]) and r["product_name_cn"] is not None else None,
                                product_name_pt=str(r["product_name_pt"]).strip() if pd.notna(r["product_name_pt"]) and r["product_name_pt"] is not None else None,
                                ncm=str(r["ncm"]).strip() if pd.notna(r["ncm"]) and r["ncm"] is not None else None,
                                qty=float(r["qty"]) if pd.notna(r["qty"]) and r["qty"] is not None else None,
                                unit_price_rmb=float(r["unit_price_rmb"]) if pd.notna(r["unit_price_rmb"]) and r["unit_price_rmb"] is not None else None,
                                line_total_rmb=float(r["line_total_rmb"]) if pd.notna(r["line_total_rmb"]) and r["line_total_rmb"] is not None else None,
                            ))

                        db.commit()
                        st.success(f"已保存 ✅ PO={po_no}（items={len(items)}）")

                except Exception as e:
                    db.rollback()
                    st.error("保存失败 ❌")
                    st.exception(e)
                finally:
                    db.close()

        except Exception as e:
            st.error("解析失败 ❌")
            st.exception(e)

with tab2:
    st.subheader("查詢 PO")
    q = st.text_input("輸入 PO No（例如 PO-20260206-3）")
    if st.button("🔎 查詢"):
        db = get_db()
        try:
            key = (q or "").strip()
            h = db.get(POHeader, key) if key else None
            if not h:
                st.warning("找不到该 PO")
            else:
                st.json({
                    "po_no": h.po_no,
                    "supplier_name": h.supplier_name,
                    "order_date": h.order_date,
                })
                rows = db.query(POItem).filter(POItem.po_no == h.po_no).order_by(POItem.seq.asc()).all()
                df = pd.DataFrame([{
                    "seq": r.seq,
                    "product_code": r.product_code,
                    "product_name_cn": r.product_name_cn,
                    "qty": r.qty,
                    "unit_price_rmb": r.unit_price_rmb,
                    "ncm": r.ncm,
                    "product_name_pt": r.product_name_pt,
                    "line_total_rmb": r.line_total_rmb,
                } for r in rows])
                st.dataframe(df, use_container_width=True)
        finally:
            db.close()
