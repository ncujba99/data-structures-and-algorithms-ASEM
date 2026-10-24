"""Задание 2: ДЕРЕВО РЕШЕНИЙ на основе бинарного дерева - выдача потребительского кредита.

  внутренний узел - вопрос; левый ребёнок - ответ ДА, правый - ответ НЕТ;
  лист            - решение.
Каждый вопрос имеет ровно два ответа, поэтому дерево полное:
у каждого узла либо 0, либо 2 ребёнка.
"""

from dataclasses import dataclass

from binary_tree import Node, height, node_count, print_tree
from console import read_int, read_yes_no


@dataclass
class Step:
    text: str
    is_decision: bool


def question(text, yes, no):
    """Вопрос с ветками ДА (yes) и НЕТ (no)."""
    return Node(Step(text, False), yes, no)


def decision(text):
    return Node(Step(text, True))


def build_loan_tree():
    """Дерево решений: 6 уровней, 9 вопросов, 10 решений."""
    return question(
        "Есть ли у вас постоянный официальный доход?",
        question(
            "Ваш ежемесячный доход больше 10 000 леев?",
            question(
                "Есть ли у вас сейчас просроченные кредиты?",
                decision("ОТКАЗ: сначала погасите текущую просроченную задолженность."),
                question(
                    "Запрашиваемая сумма меньше 12 ваших месячных доходов?",
                    decision("ОДОБРЕНО: кредит на стандартных условиях."),
                    question(
                        "Можете ли вы предоставить залог (недвижимость или автомобиль)?",
                        decision("ОДОБРЕНО: кредит под залог, сниженная процентная ставка."),
                        decision("ОДОБРЕНО ЧАСТИЧНО: сумма уменьшена до 12 месячных доходов.")))),
            question(
                "Есть ли у вас поручитель с официальным доходом?",
                question(
                    "Были ли все ваши прошлые кредиты погашены вовремя?",
                    decision("ОДОБРЕНО: кредит с поручителем."),
                    decision("ОТКАЗ: низкий доход и плохая кредитная история.")),
                decision("ОТКАЗ: недостаточный доход и нет поручителя."))),
        question(
            "Есть ли у вас другой стабильный доход (пенсия, аренда, бизнес)?",
            question(
                "Можете ли вы подтвердить этот доход документами?",
                decision("ОДОБРЕНО: кредит на ограниченную сумму (до 50 000 леев)."),
                decision("ОТКАЗ: доход не подтверждён документами.")),
            decision("ОТКАЗ: нет источника дохода для погашения кредита.")))


def label(step):
    return f"[РЕШЕНИЕ] {step.text}" if step.is_decision else step.text


def consult(root):
    print("Ответьте на вопросы: «да» или «нет».\n")
    answers = []
    node = root
    while not node.is_leaf():
        yes = read_yes_no(f"{len(answers) + 1}. {node.info.text} ")
        answers.append((node.info.text, yes))
        node = node.left if yes else node.right

    print("\n==================== РЕЗУЛЬТАТ ====================")
    print(node.info.text)
    print("\nВаши ответы:")
    for i, (text, yes) in enumerate(answers, 1):
        print(f"  {i}. {text} - {'ДА' if yes else 'НЕТ'}")
    print("===================================================")


def count_decisions(tree):
    if tree is None:
        return 0
    if tree.is_leaf():
        return 1
    return count_decisions(tree.left) + count_decisions(tree.right)


def show_tree(root):
    print("Дерево решений (ДА - левое поддерево, НЕТ - правое):\n")
    print_tree(root, label, "ДА", "НЕТ")
    decisions = count_decisions(root)
    print(f"\nУровней: {height(root)}, вопросов: {node_count(root) - decisions}, "
          f"решений: {decisions}")


def main():
    root = build_loan_tree()
    while True:
        print("\n=== Дерево решений: выдача кредита ===")
        print("1. Пройти опрос")
        print("2. Показать дерево решений")
        print("0. Выход")
        choice = read_int("Ваш выбор: ", 0, 2)
        print()
        if choice == 0:
            break
        if choice == 1:
            consult(root)
        else:
            show_tree(root)


if __name__ == "__main__":
    main()
