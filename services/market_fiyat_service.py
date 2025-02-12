import os
import requests
from dotenv import load_dotenv


load_dotenv()

class MarketFiyatService():
    def __init__(self):
        self.url = os.getenv('MARKET_FIYAT_API_BASE_URL')

    def fetch_product_data(self, product_name, product_category = None):
        headers = {
            "Withcredentials": os.getenv("WITH_CREDENTIALS"),
            "Pragma": os.getenv("PRAGMA"),
            "Sec-Fetch": os.getenv("SEC_FETCH"),
            "Expires": os.getenv("EXPIRES"),
            "Accept-Language": os.getenv("ACCEPT_LANGUAGE"),
            "Cache-Control": os.getenv("CACHE_CONTROL"),
            "Sec-Fetch-Mode": os.getenv("SEC_FETCH_MODE"),
            "Origin": os.getenv("ORIGIN"),
            "User-Agent": os.getenv("USER_AGENT"),
            "Connection": os.getenv("CONNECTION"),
            "Host": os.getenv("HOST"),
            "Sec-Fetch-Dest": os.getenv("SEC_FETCH_DEST"),
            "Timeout": os.getenv("TIMEOUT"),
            "Content-Type": os.getenv("CONTENT_TYPE")
        }

        payload = {
            "keywords": product_name,
            "pages": 0,
            "size": 30
        }

        response = requests.post(self.url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()

            if not data.get("content"):
                if product_category:
                    print(f"⚠️ Ürün bulunamadı, kategori ({product_category}) ile tekrar arıyorum...")
                    return self.fetch_product_data(product_category)  # Rekürsif çağrı
                else:
                    print("❌ Ürün bulunamadı, alternatif arama da başarısız oldu.")
                    return []
            # Eğer `content` doluysa, gerekli bilgileri çıkar
            return self.__parse_response(data)

        else:
            print(f"❌ API isteği başarısız! HTTP Kodu: {response.status_code}")
            return []

    def __parse_response(self, data):
        """
        API yanıtındaki `content` listesinden istenen alanları filtreleyerek döndürür.
        """
        extracted_data = []

        for item in data["content"]:
            title = item.get("title", "Bilinmiyor")
            brand = item.get("brand", "Bilinmiyor")
            depot_info = []

            # `productDepotInfoList` içinden istenen bilgileri çek
            for depot in item.get("productDepotInfoList", []):
                depot_info.append({
                    "depotName": depot.get("depotName", "Bilinmiyor"),
                    "price": depot.get("price", 0),
                    "marketAdi": depot.get("marketAdi", "Bilinmiyor"),
                    "percentage": depot.get("percentage", 0),
                    "longitude": depot.get("longitude", 0),
                    "latitude": depot.get("latitude", 0),
                })

            # Sonuçları listeye ekle
            extracted_data.append({
                "title": title,
                "brand": brand,
                "depotInfo": depot_info
            })

        return extracted_data
