import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from image_processor import ImageProcessor
from config import Config
from statistics_tracker import StatisticsTracker
from typing import List
import requests
import time


class VkBot:
    def __init__(self, token: str, group_id: str):
        print("Инициализация бота...")
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.image_processor = ImageProcessor()
        self.stats_tracker = StatisticsTracker()
        self.bot_id = -int(group_id)

        # ИЗМЕНЕНИЕ 2: Загружаем историю из файла при старте
        self.history: List[int] = self._load_history()
        # Инициализируем счетчик на основе длины загруженной истории
        self.bandit_message_count = len(self.history)
        print(f"История успешно загружена. Всего записей: {len(self.history)}")


    # ИЗМЕНЕНИЕ 3: Новый метод для загрузки истории из файла
    def _load_history(self) -> List[int]:
        """Загружает историю чисел из файла. Если файла нет, возвращает пустой список."""
        try:
            with open(Config.HISTORY_FILE_PATH, 'r') as f:
                # Считываем строки, убираем пробелы/переносы и преобразуем в числа
                numbers = [int(line.strip()) for line in f if line.strip()]
                return numbers
        except FileNotFoundError:
            print("Файл истории не найден. Начинаем с пустой истории.")
            return []
        except Exception as e:
            print(f"Ошибка при загрузке истории: {e}. Начинаем с пустой истории.")
            return []

    # ИЗМЕНЕНИЕ 4: Новый метод для сохранения истории в файл
    def _save_history(self):
        """Сохраняет текущий список истории в файл."""
        try:
            with open(Config.HISTORY_FILE_PATH, 'w') as f:
                for number in self.history:
                    f.write(str(number) + '\n')
        except Exception as e:
            print(f"Критическая ошибка при сохранении истории в файл: {e}")


    def send_message(self, chat_id: int, message: str):
        try:
            self.vk.messages.send(
                chat_id=chat_id, message=message, random_id=random.randint(0, 2 ** 32 - 1)
            )
            print(f"Отправлен отчет в чат {chat_id}.")
        except vk_api.exceptions.ApiError as e:
            print(f"Ошибка отправки сообщения: {e}")

    def _handle_new_message(self, event):
        if not event.from_chat: return

        chat_id = event.chat_id
        message = event.object.message
        sender_id = message['from_id']

        print(f"Новое сообщение в чате {chat_id} от {sender_id}")

        if sender_id == self.bot_id: return

        if sender_id == Config.BANDIT_ID:
            number = self.image_processor.get_number_from_vk_message(message)
            if number is not None:
                # --- ИЗМЕНЕНИЕ 5: Обновленная логика обработки нового числа ---

                # 1. Добавляем новое число в конец списка
                self.history.append(number)

                # 2. Если история превысила лимит, удаляем самый старый элемент (первый)
                if len(self.history) > Config.MAX_HISTORY_SIZE:
                    self.history.pop(0)

                # 3. Сохраняем обновленную историю в файл
                self._save_history()

                # 4. Увеличиваем общий счетчик
                self.bandit_message_count += 1
                print(f"Распознано число: {number}. Сообщений от бандита: {self.bandit_message_count}. Записей в истории: {len(self.history)}")

                # 5. Отправляем отчет каждые 10 сообщений
                if self.bandit_message_count % 10 == 0:
                    print("Отправка статистики: количество сообщений достигло 10.")
                    report = self.stats_tracker.get_rarity_report(self.history, Config.POSSIBLE_NUMBERS)
                    self.send_message(chat_id, report)
            else:
                print("Не удалось распознать число из изображения.")

    def run(self):
        print("Бот запущен! Жду событий...")
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        try:
                            self._handle_new_message(event)
                        except Exception as e:
                            print(f"Критическая ошибка при обработке СОБЫТИЯ: {e}")
            except requests.exceptions.ReadTimeout:
                print("Переподключение к Long Poll серверу VK после тайм-аута...")
                time.sleep(1)
            except Exception as e:
                print(f"Произошла критическая ошибка в цикле longpoll: {e}")
                time.sleep(15)