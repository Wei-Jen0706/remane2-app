import io
import os
import re
import zipfile
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PDF 批次檔名裁切工具", layout="wide")

st.title("✂️ PDF 檔名裁切工具 (保留 1234_5678 格式)")
st.write("自動識別檔名開頭的 **4位數字_4位數字**，並將後面的文字與數字全部刪除。")

# 1. 批次選擇上傳 PDF 檔案
uploaded_files = st.file_uploader(
    "請選擇並上傳要處理的 PDF 檔案（可多選）：",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"📂 成功讀取到 {len(uploaded_files)} 個 PDF 檔案。")

    rename_map = {}
    # 正則表達式：匹配開頭的 4位數字 + 底線 + 4位數字
    pattern = re.compile(r"^(\d{4}_\d{4})")

    # 建立檔案名稱與物件對照表
    file_dict = {file.name: file for file in uploaded_files}

    for filename in file_dict.keys():
        name, ext = os.path.splitext(filename)
        match = pattern.match(name)

        if match:
            # 抓取第一組 1234_5678 格式並加上副檔名
            new_filename = match.group(1) + ext
            rename_map[filename] = new_filename
        else:
            # 若檔名不符合 1234_5678 格式，則保持原樣
            rename_map[filename] = filename

    # 2. 顯示對照預覽
    st.subheader("👁️ 改名預覽")
    df_preview = pd.DataFrame([
        {
            "原始檔名": old_f,
            "修改後檔名": new_f,
            "狀態": "✨ 將進行修改" if old_f != new_f else "⚠️ 未匹配格式（不變）"
        }
        for old_f, new_f in rename_map.items()
    ])

    st.dataframe(df_preview, use_container_width=True)

    changable_count = sum(1 for k, v in rename_map.items() if k != v)

    if changable_count > 0:
        st.info(f"💡 共有 {changable_count} 個檔案符合修改條件。")

        # 建立在記憶體中的 ZIP 壓縮檔
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for old_f, new_f in rename_map.items():
                file_obj = file_dict[old_f]
                # 將改名後的內容寫入 ZIP 檔中
                zip_file.writestr(new_f, file_obj.getvalue())

        zip_buffer.seek(0)

        # 一鍵打包下載按鈕
        st.download_button(
            label=f"🚀 一鍵打包下載修改檔名的 PDF ({len(uploaded_files)} 個檔案)",
            data=zip_buffer,
            file_name="renamed_pdf_files.zip",
            mime="application/zip",
            type="primary"
        )
    else:
        st.info("沒有需要修改的檔案名稱。")