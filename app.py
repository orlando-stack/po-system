import streamlit as st
from utils.po_parser import parse_po_excel
from utils.normalizer import normalize_po_items

st.set_page_config(page_title="PO 解析工具", layout="wide")
st.title("📦 PO 解析工具（內部用）")

uploaded = st.file_uploader("上傳 PO Excel（.xlsx）", type=["xlsx"])

if uploaded:
    try:
        with st.spinner("解析中..."):
            header, items_raw = parse_po_excel(uploaded)
            items = normalize_po_items(header, items_raw)

        st.success("解析成功 ✅")

        st.subheader("PO 抬頭")
        st.json(header)

        st.subheader("明細（原始）")
        st.dataframe(items_raw, use_container_width=True)

        st.subheader("明細（標準化）")
        st.dataframe(items, use_container_width=True)

        csv = items.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ 下載標準化明細（CSV）",
            data=csv,
            file_name=f"{header.get('po_no','PO')}_items.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error("解析失敗 ❌")
        st.exception(e)
else:
    st.info("請先上傳 PO Excel。")
