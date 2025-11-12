from typing import List, Set, Tuple


class StatisticsTracker:
    @staticmethod
    def _get_plural(n: int, titles: Tuple[str, str, str]) -> str:
        """Возвращает правильное склонение для числа (1 ход, 2 хода, 5 ходов)."""
        if 10 <= n % 100 <= 20:
            return titles[2]
        if n % 10 == 1:
            return titles[0]
        if 2 <= n % 10 <= 4:
            return titles[1]
        return titles[2]

    def get_rarity_report(self, history: List[int], possible_numbers: Set[int]) -> str:
        """Анализирует историю и возвращает топ-10 редких чисел в нужном формате."""
        if not history:
            return "История чисел пока пуста. Жду первое число."

        total_rolls = len(history)
        last_number = history[-1]

        # Словарь для хранения "возраста" (сколько ходов не выпадало)
        recency: Dict[int, int] = {}

        # Для удобства поиска переворачиваем историю (индекс = сколько ходов назад)
        reversed_history = list(reversed(history))

        for num in possible_numbers:
            try:
                # Находим индекс первого вхождения числа. +1 т.к. индекс с 0
                age = reversed_history.index(num) + 1
                # Возраст (сколько ходов не выпадало) = текущий ход - индекс последнего выпадения
                recency[num] = age - 1
            except ValueError:
                # Если числа нет в истории, его "возраст" - вся длина истории
                recency[num] = total_rolls

        # Сортируем числа по возрасту (от самых больших к самым маленьким)
        # item[1] - это возраст (сколько ходов не выпадало)
        sorted_rarity = sorted(recency.items(), key=lambda item: item[1], reverse=True)

        # Формируем отчет
        report_lines = [f"Выпало число: {last_number}. Всего ходов: {total_rolls}.\n"]
        report_lines.append("Топ 10 самых редких чисел:")

        # Выводим топ 10 самых редких
        for number, age in sorted_rarity[:10]:
            titles = ("раз", "раза", "раз")  # Новое склонение для "раз"

            if number not in history:
                # Если число никогда не выпадало
                # В этом случае age = total_rolls, но логичнее написать "ни разу"
                line = f"число {number} не выпадало ни разу (всего ходов {total_rolls})"
            else:
                # Если число выпадало, age = сколько ходов назад
                age_str = self._get_plural(age, titles)
                line = f"число {number} не выпадало {age} {age_str}"

            report_lines.append(line)

        return "\n".join(report_lines)