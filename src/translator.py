import requests
import json

class Translator:
    def __init__(self, api_key, folder_id):
        self.api_key = api_key
        self.folder_id = folder_id

    def translate(self, target_language, texts):
        body = {
            "targetLanguageCode": target_language,
            "texts": texts,
            "folderId": self.folder_id,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {0}".format(self.api_key)
        }

        response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
            json = body,
            headers = headers
        )
        json_response = json.loads(response.text)
        return json_response