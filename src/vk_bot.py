import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from image_processor import ImageProcessor
from config import Config
from statistics_tracker import StatisticsTracker
from typing import List


class VkBot:
    def __init__(self, token: str, group_id: str):
        print("Инициализация бота...")
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.image_processor = ImageProcessor()
        self.stats_tracker = StatisticsTracker()
        self.bot_id = -int(group_id)
        self.history: List[int] = []
        # ИЗМЕНЕНИЕ 1: Добавляем счетчик сообщений от бандита
        self.bandit_message_count = 0

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
                # 1. Добавляем новое число в историю
                self.history.append(number)

                # ИЗМЕНЕНИЕ 2: Увеличиваем счетчик на 1 после каждого распознанного числа
                self.bandit_message_count += 1
                print(f"Распознано число: {number}. Сообщений от бандита: {self.bandit_message_count}.")

                # ИЗМЕНЕНИЕ 3: Проверяем, кратно ли число сообщений 10
                if self.bandit_message_count % 10 == 0:
                    print("Отправка статистики: количество сообщений достигло 10.")
                    # 2. Получаем аналитический отчет
                    report = self.stats_tracker.get_rarity_report(self.history, Config.POSSIBLE_NUMBERS)

                    # 3. Отправляем отчет в чат
                    self.send_message(chat_id, report)
            else:
                print("Не удалось распознать число из изображения.")

    def run(self):
        print("Бот запущен! Жду событий...")
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    self._handle_new_message(event)
                except Exception as e:
                    print(f"Критическая ошибка при обработке события: {e}")