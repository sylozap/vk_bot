from typing import Optional
import requests
import numpy as np
import cv2
import pytesseract
from PIL import Image


class ImageProcessor:
    @staticmethod
    def _download_image(url: str) -> Optional[np.ndarray]:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_array = np.frombuffer(response.content, dtype=np.uint8)
            cv2_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if cv2_image is not None:
                print(f"Изображение успешно скачано. Размер: {cv2_image.shape}")
                return cv2_image
            return None
        except requests.RequestException as e:
            print(f"Ошибка при скачивании изображения: {e}")
            return None

    @staticmethod
    def _recognize_number(image: np.ndarray) -> Optional[int]:
        try:
            height, width, _ = image.shape
            roi = image[int(height * 0.825):int(height * 0.925), int(width * 0.45):int(width * 0.55)]
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, binary_roi = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY_INV)
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
            recognized_text = pytesseract.image_to_string(Image.fromarray(binary_roi), config=custom_config)
            number_str = recognized_text.strip()
            if number_str:
                return int(number_str)
            return None
        except Exception as e:
            print(f"Ошибка при распознавании числа: {e}")
            return None

    def get_number_from_vk_message(self, message: dict) -> Optional[int]:
        image_url = None
        if message.get('attachments'):
            for attach in message['attachments']:
                if attach['type'] == 'photo':
                    photo = attach['photo']
                    max_size = max(photo['sizes'], key=lambda size: size['width'])
                    image_url = max_size['url']
                    break
        if not image_url: return None
        cv2_image = self._download_image(image_url)
        if cv2_image is None: return None
        return self._recognize_number(cv2_image)