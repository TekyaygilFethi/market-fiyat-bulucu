import openai

class OpenAIService():
    def __init__(self, api_key):
        self.api_key = api_key
        self.system_prompt = {
            "role": "system",
            "content": 'Sana bir resim göndereceğim. Bu resim bir ürünün resmi. '
               'Bu ürünün ne olduğunu ve markasını bana JSON formatında çıkarmanı istiyorum. '
               'Kolay parse edebilmem için senden istediğim bana sadece ama sadece bu şekilde bir sonuç çıkarman: '
               '{"Ürün":"Mis Peynir Çubukları","Kategori":"Peynir"}'
        }


    def generate_response(self, image):
        client = openai.OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                self.system_prompt,
                # {"role": "user", "content": f"![image](data:image/png;base64,{image_data})"}
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}",
                            "detail": "low"
                        },
                    },
                ]}
            ],
            # max_tokens=300
        )

        return {"response": response.choices[0].message.content}