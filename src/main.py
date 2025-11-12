from vk_bot import VkBot
from config import Config

def main():
    bot = VkBot(token=Config.TOKEN, group_id=Config.GROUP_ID)
    bot.run()

if __name__ == '__main__':
    main()

# 1. Вывод статистики по команде
# 2. Подсчет статистик по красное/черное чет/нечет малые/большие
# 3. Захостить
# 4. Смешные ответы