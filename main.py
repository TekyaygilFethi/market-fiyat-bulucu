import os
import folium
from streamlit_folium import folium_static
import pandas as pd
import streamlit as st
from services.open_ai_service import OpenAIService
from services.market_fiyat_service import MarketFiyatService
import base64
import json
from dotenv import load_dotenv

load_dotenv()

def display_map(df):
    if not df.empty:
        m = folium.Map(location=[41.01, 29.01], zoom_start=10)  # İstanbul'a yakın başlat
        for _, row in df.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"{row['title']} - {row['marketAdi']} - {row['price']}₺",
                tooltip=row["depotName"]
            ).add_to(m)
        folium_static(m)

def display_products_with_details(response):
    for item in response:
        title = item["title"]
        brand = item["brand"]
        st.subheader(f"📌 {title} ({brand})")

        with st.expander("📦 Ürün Detayları: "):
            depot_info = pd.DataFrame(item.get("depotInfo", []))

            st.dataframe(depot_info)

            for _, row in depot_info.iterrows():
                link = f"https://www.google.com/maps?q={row['latitude']},{row['longitude']}"
                st.markdown(f"📍 [{row['depotName']} - {row['price']}₺]({link})", unsafe_allow_html=True)


st.title("Ölücü Market Ürün Arama")


tab1, tab2 = st.tabs(["📝 Yazı ile Ara", "🖼️ Resim ile Ara"])

ai_service = OpenAIService(os.getenv('OPEN_AI_KEY'))
market_service = MarketFiyatService()

with tab1:
    st.subheader("🔍 Metin ile Ürün Arama")
    search_text = st.text_input("Aramak istediğiniz ürünü yazın:", "")

    if st.button("Ara"):
        if search_text.strip():
            with st.spinner("Ürün aranıyor..."):
                response = market_service.fetch_product_data(search_text, search_text)

                if len(response) == 0:
                    st.warning("❌ Ürün bulunamadı.")
                else:
                    display_products_with_details(response)
                    # df = pd.DataFrame(response)
                    # st.dataframe(df[["title","brand"]])

                    # display_map(df)
        else:
            st.warning("Lütfen bir ürün adı girin.")


with tab2:
    st.subheader("📸 Resim Yükleyerek Ürün Arama")

    password = st.text_input("🔑 Şifre Giriniz:", type="password")
    uploaded_file = st.file_uploader("Lütfen bir ürün resmi yükleyin:", type=["png", "jpg", "jpeg"])

    if uploaded_file and st.button("Resimle Ara"):
        if password == os.getenv('OPEN_AI_PASSWORD'):
            with st.spinner("Resim işleniyor..."):
                image_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                response = ai_service.generate_response(image_data)
                print(response)
                # data_dict = json.loads(response)
            try:
                is_product_found = True

                result = eval(response["response"])  # JSON string'i dict'e çevir
                product_name = result["Ürün"]
                if not product_name or product_name == "":
                    product_name = result["Kategori"]
                    if not product_name or product_name == "":
                        st.warning("❌ Ürün bulunamadı.")
                        is_product_found = False

                if is_product_found:

                    st.success(f"✅ Algılanan Ürün: {product_name}")

                    with st.spinner(f"{product_name} için arama yapılıyor..."):
                        response = market_service.fetch_product_data(product_name, product_name)

                        if len(response) == 0:
                            st.warning("❌ Ürün bulunamadı.")
                        else:
                            display_products_with_details(response)
            except Exception as e:
                st.error(f"❌ Hata oluştu: {e}")