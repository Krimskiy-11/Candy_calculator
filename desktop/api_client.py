import requests

BASE_URL = 'http://127.0.0.1:8000/api'


class ApiClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base = base_url.rstrip('/')

    def list_ingredients(self):
        return requests.get(f'{self.base}/ingredients/').json()

    # def create_ingredient(self, data: dict):
    #     return requests.post(f'{self.base}/ingredients/', json=data).json()

    def create_ingredient(self, data):
        url = f"{self.base}/ingredients/"  # ОБЯЗАТЕЛЬНО со слэшем на конце!
        response = self.session.post(url, json=data) if hasattr(self, 'session') else requests.post(url, json=data)

        # Если статус не 200 и не 201 — показываем точную причину от бэкенда
        if response.status_code not in (200, 201):
            raise Exception(f"Ошибка сервера [HTTP {response.status_code}]:\n{response.text[:400]}")

        return response.json()

    def list_cakes(self):
        return requests.get(f'{self.base}/cakes/').json()

    def create_cake(self, data: dict):
        return requests.post(f'{self.base}/cakes/', json=data).json()

    def delete_cake(self, cake_id: int):
        requests.delete(f'{self.base}/cakes/{cake_id}/')

    def calculate(self, cake_id: int, diameter: int) -> dict:
        r = requests.get(
            f'{self.base}/cakes/{cake_id}/calculate/',
            params={'diameter': diameter},
        )
        r.raise_for_status()
        return r.json()

    def update_ingredient(self, ingredient_id: int, data: dict):
        r = requests.put(f'{self.base}/ingredients/{ingredient_id}/', json=data)
        r.raise_for_status()
        return r.json()

    def delete_ingredient(self, ingredient_id: int):
        r = requests.delete(f'{self.base}/ingredients/{ingredient_id}/')
        r.raise_for_status()
        return True

    def _handle_response(self, response):
        # Если статус не 200/201/204
        if not response.ok:
            # Показываем код ошибки и первые 200 символов ответа сервера
            raise Exception(f"HTTP {response.status_code}: {response.text[:250]}")

        # Если ответ успешный, но пустой (например, 204 No Content)
        if not response.content:
            return {}

        try:
            return response.json()
        except Exception:
            raise Exception(f"Ответ не в формате JSON: {response.text[:250]}")
