"""Задание 1 (Вариант 10): информационная система железнодорожного вокзала
на основе бинарного поискового дерева.

Для каждого поезда хранятся: номер поезда, станция назначения, время отправления.
КЛЮЧЕВОЕ ПОЛЕ - номер поезда: по нему упорядочено дерево и выполняется поиск.
"""

from dataclasses import dataclass

from binary_tree import BinaryTree
from console import read_int, read_line, read_non_empty

MAX_TRAIN_NUMBER = 9999


@dataclass
class Train:
    number: int                 # ключевое поле
    destination: str = ""       # станция назначения
    departure: int = 0          # время отправления, минуты от полуночи

    def __lt__(self, other):
        """Порядок в дереве определяется только ключевым полем."""
        return self.number < other.number


def by_number(number):
    """«Образец» для поиска / удаления: заполнено только ключевое поле."""
    return Train(number)


def format_time(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def parse_time(s):
    """Разбирает время в формате ЧЧ:ММ (или Ч:ММ). Возвращает минуты или None."""
    hs, colon, ms = s.partition(":")
    if not colon or not (1 <= len(hs) <= 2) or len(ms) != 2:
        return None
    if not (hs.isdigit() and ms.isdigit()):
        return None
    h, m = int(hs), int(ms)
    if h > 23 or m > 59:
        return None
    return h * 60 + m


def read_time(prompt):
    while True:
        minutes = parse_time(read_line(prompt))
        if minutes is not None:
            return minutes
        print("  Введите время в формате ЧЧ:ММ (00:00 - 23:59).")


# ---------- вывод ----------

def print_header():
    print("  Номер | Станция назначения       | Отправление")
    print("  ------+--------------------------+------------")


def print_row(t):
    print(f"  {t.number:>5} | {t.destination:<24} | {format_time(t.departure)}")


# ---------- пункты меню ----------

def add_trains(tree):
    count = read_int("Сколько поездов добавить? (1..100): ", 1, 100)
    for i in range(1, count + 1):
        print(f"\nПоезд {i} из {count}:")
        while True:
            number = read_int(f"  номер поезда (1..{MAX_TRAIN_NUMBER}): ", 1, MAX_TRAIN_NUMBER)
            if tree.retrieve_item(by_number(number)) is None:
                break
            print("  Поезд с таким номером уже есть, номер - ключевое поле и должен быть уникален.")
        destination = read_non_empty("  станция назначения: ")
        departure = read_time("  время отправления (ЧЧ:ММ): ")
        tree.insert_item(Train(number, destination, departure))
    print(f"\nДобавлено поездов: {count}. Всего в системе: {tree.node_count()}.")


def print_all(tree):
    if tree.is_empty():
        print("Список поездов пуст.")
        return
    print("Все поезда (симметричный обход - по возрастанию номера):")
    print_header()
    tree.inorder_tree(print_row)
    print(f"Всего: {tree.node_count()}")


def find_by_number(tree):
    number = read_int("Номер поезда: ", 1, MAX_TRAIN_NUMBER)
    t = tree.retrieve_item(by_number(number))
    if t is None:
        print(f"Поезд № {number} не найден.")
        return
    print_header()
    print_row(t)


def find_by_destination(tree):
    station = read_non_empty("Станция назначения: ")
    # Станция не является ключом, поэтому нужен полный обход дерева.
    found = []
    tree.inorder_tree(lambda t: found.append(t) if t.destination == station else None)
    if not found:
        print(f"Поездов до станции «{station}» нет.")
        return
    print(f"Поезда до станции «{station}»:")
    print_header()
    for t in found:
        print_row(t)


def show_structure(tree):
    if tree.is_empty():
        print("Дерево пусто.")
        return
    print("Структура дерева (ключ - номер поезда; Л - левое, П - правое поддерево):\n")
    tree.print(lambda t: f"{t.number}  ({t.destination})")

    for title, traverse in (("Симметричный обход (inorder):", tree.inorder_tree),
                            ("Обход в прямом порядке (preorder):", tree.preorder_tree),
                            ("Обход в обратном порядке (postorder):", tree.postorder_tree)):
        keys = []
        traverse(lambda t: keys.append(str(t.number)))
        print(f"\n{title:<38} {' '.join(keys)}", end="")
    print(f"\n\nУзлов: {tree.node_count()}, уровней (высота): {tree.height()}")


DEMO = [
    Train(50, "Москва", 8 * 60 + 15),   Train(30, "Бухарест", 21 * 60 + 40),
    Train(70, "Одесса", 6 * 60 + 5),    Train(20, "Яссы", 13 * 60),
    Train(40, "Киев", 17 * 60 + 30),    Train(60, "Москва", 22 * 60 + 50),
    Train(80, "Унгены", 10 * 60 + 20),  Train(35, "Бухарест", 9 * 60 + 45),
    Train(65, "Одесса", 15 * 60 + 10),
]


def load_demo(tree):
    added = sum(tree.insert_item(Train(t.number, t.destination, t.departure)) for t in DEMO)
    print(f"Загружено демонстрационных поездов: {added} (уже существующие номера пропущены).")


def main():
    tree = BinaryTree()
    backup = None               # копия дерева для отмены последнего удаления

    while True:
        print("\n=== Вокзал: поезда дальнего следования (бинарное дерево) ===")
        print("1. Ввести данные о поездах")
        print("2. Вывести все поезда")
        print("3. Найти поезд по номеру")
        print("4. Найти поезда по станции назначения")
        print("5. Удалить поезд")
        print("6. Показать структуру дерева и обходы")
        print("7. Отменить последнее удаление")
        print("8. Загрузить демонстрационные данные")
        print("9. Очистить все данные")
        print("0. Выход")
        choice = read_int("Ваш выбор: ", 0, 9)
        print()

        if choice == 0:
            break
        elif choice == 1:
            add_trains(tree)
        elif choice == 2:
            print_all(tree)
        elif choice == 3:
            find_by_number(tree)
        elif choice == 4:
            find_by_destination(tree)
        elif choice == 5:
            number = read_int("Номер удаляемого поезда: ", 1, MAX_TRAIN_NUMBER)
            if tree.retrieve_item(by_number(number)) is None:
                print(f"Поезд № {number} не найден.")
            else:
                backup = tree.copy()
                tree.delete_item(by_number(number))
                print(f"Поезд № {number} удалён. (Пункт 7 - отменить удаление.)")
        elif choice == 6:
            show_structure(tree)
        elif choice == 7:
            if backup is None:
                print("Нет удаления, которое можно отменить.")
            else:
                tree, backup = backup, None
                print("Последнее удаление отменено.")
        elif choice == 8:
            load_demo(tree)
        elif choice == 9:
            tree.destroy()
            backup = None
            print("Все данные удалены.")


if __name__ == "__main__":
    main()
