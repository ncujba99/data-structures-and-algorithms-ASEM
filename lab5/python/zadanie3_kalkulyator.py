"""Задание 3: калькулятор арифметических выражений в постфиксной форме
на основе бинарного дерева (дерева выражения).

  лист            - операнд (число);
  внутренний узел - бинарная операция + - * /, у него ровно 2 ребёнка.

Построение: постфиксная запись читается слева направо со стеком поддеревьев.
Вычисление: обход в обратном порядке (postorder) - сначала оба операнда, потом операция.
Дополнительно: ввод в обычной (инфиксной) форме со скобками, которая переводится
в постфиксную алгоритмом сортировочной станции (shunting-yard).
"""

import math
from dataclasses import dataclass

from binary_tree import Node, print_tree
from console import read_int, read_non_empty

OPERATORS = "+-*/"
BOOK_EXAMPLE = "3 1 + 3 * 9 5 - 2 + / 3 7 4 - * 6 + -"


class ExpressionError(Exception):
    pass


@dataclass
class Token:
    is_op: bool
    op: str = ""        # '+', '-', '*', '/'  (если is_op)
    value: float = 0.0  # число               (если не is_op)


def precedence(op):
    return 1 if op in "+-" else 2


def format_number(x):
    return format(x, ".10g")


def operand(x):
    """Отрицательное число внутри выражения берётся в скобки: 2 - (-1), а не 2 - -1."""
    return f"({format_number(x)})" if x < 0 else format_number(x)


def label(t):
    return t.op if t.is_op else format_number(t.value)


def parse_number(s):
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


# ---------- построение дерева из постфиксной записи ----------

def build_tree(postfix):
    """число    -> новый лист кладётся в стек;
    операция -> из стека берутся правый, затем левый операнд, создаётся узел
                с этими детьми, и он кладётся в стек.
    В конце в стеке должно остаться ровно одно дерево."""
    stack = []
    for s in postfix:
        if len(s) == 1 and s in OPERATORS:
            if len(stack) < 2:
                raise ExpressionError(f"операции «{s}» не хватает операндов")
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(Token(True, op=s), left, right))
        else:
            v = parse_number(s)
            if v is None:
                raise ExpressionError(f"«{s}» - не число и не операция")
            stack.append(Node(Token(False, value=v)))
    if not stack:
        raise ExpressionError("выражение пустое")
    if len(stack) > 1:
        raise ExpressionError(f"лишние операнды: в стеке осталось поддеревьев - "
                              f"{len(stack)}, а должно быть 1")
    return stack[0]


# ---------- перевод инфиксной записи в постфиксную (shunting-yard) ----------

def tokenize_infix(s):
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            while j < len(s) and (s[j].isdigit() or s[j] == "."):
                j += 1
            tokens.append(s[i:j])
            i = j
        elif c in "+-*/()":
            tokens.append(c)
            i += 1
        else:
            raise ExpressionError(f"недопустимый символ «{c}»")
    return tokens


def infix_to_postfix(infix):
    output, ops = [], []
    for t in tokenize_infix(infix):
        if t == "(":
            ops.append(t)
        elif t == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops:
                raise ExpressionError("лишняя закрывающая скобка")
            ops.pop()
        elif t in OPERATORS:
            # Все операции левоассоциативны: выталкиваем операции с приоритетом >= текущего.
            while ops and ops[-1] != "(" and precedence(ops[-1]) >= precedence(t):
                output.append(ops.pop())
            ops.append(t)
        else:
            output.append(t)
    while ops:
        if ops[-1] == "(":
            raise ExpressionError("не закрыта скобка")
        output.append(ops.pop())
    return output


# ---------- обходы ----------

def evaluate(node, steps):
    """Обратный порядок (postorder): левое поддерево, правое поддерево, узел.
    Каждый шаг вычисления записывается в steps."""
    if not node.info.is_op:
        return node.info.value
    a = evaluate(node.left, steps)
    b = evaluate(node.right, steps)
    op = node.info.op
    if op == "+":
        r = a + b
    elif op == "-":
        r = a - b
    elif op == "*":
        r = a * b
    else:
        if b == 0:
            raise ExpressionError(f"деление на ноль: {format_number(a)} / 0")
        r = a / b
    steps.append(f"{operand(a)} {op} {operand(b)} = {format_number(r)}")
    return r


def preorder(node, out):
    """Прямой порядок (preorder): узел, левое поддерево, правое поддерево."""
    if node is None:
        return
    out.append(label(node.info))
    preorder(node.left, out)
    preorder(node.right, out)


def postorder(node, out):
    if node is None:
        return
    postorder(node.left, out)
    postorder(node.right, out)
    out.append(label(node.info))


def to_infix(node):
    """Симметричный обход (inorder) с минимальным числом скобок:
    скобки нужны, если операция ребёнка слабее операции родителя, или если справа
    стоит операция того же приоритета после '-' или '/' (a - (b - c) != a - b - c)."""
    if not node.info.is_op:
        return operand(node.info.value)
    op = node.info.op
    p = precedence(op)

    left = to_infix(node.left)
    if node.left.info.is_op and precedence(node.left.info.op) < p:
        left = f"({left})"

    right = to_infix(node.right)
    if node.right.info.is_op:
        pr = precedence(node.right.info.op)
        if pr < p or (pr == p and op in "-/"):
            right = f"({right})"
    return f"{left} {op} {right}"


# ---------- обработка одного выражения ----------

def process(postfix):
    try:
        root = build_tree(postfix)
    except ExpressionError as e:
        print(f"Ошибка в выражении: {e}.")
        return

    pre, post = [], []
    preorder(root, pre)
    postorder(root, post)

    print("\nДерево выражения (Л - левый операнд, П - правый):\n")
    print_tree(root, label)
    print()
    print(f"{'Префиксная запись  (preorder):':<32}{' '.join(pre)}")
    print(f"{'Инфиксная запись   (inorder):':<32}{to_infix(root)}")
    print(f"{'Постфиксная запись (postorder):':<32}{' '.join(post)}")

    steps = []
    try:
        result = evaluate(root, steps)
    except ExpressionError as e:
        print(f"\nОшибка вычисления: {e}.")
        return
    print("\nВычисление (обход в обратном порядке):")
    for i, step in enumerate(steps, 1):
        print(f"  {i:>2}) {step}")
    print(f"\nРезультат: {format_number(result)}")


def main():
    while True:
        print("\n=== Калькулятор: дерево выражения ===")
        print("1. Ввести выражение в постфиксной форме (например: 3 4 + 2 *)")
        print("2. Ввести выражение в обычной форме со скобками (например: (3 + 4) * 2)")
        print("3. Пример из методички")
        print("0. Выход")
        choice = read_int("Ваш выбор: ", 0, 3)
        if choice == 0:
            break

        if choice == 1:
            s = read_non_empty("Постфиксное выражение (элементы через пробел): ")
            process(s.split())
        elif choice == 2:
            s = read_non_empty("Выражение: ")
            try:
                postfix = infix_to_postfix(s)
            except ExpressionError as e:
                print(f"Ошибка в выражении: {e}.")
                continue
            print(f"Постфиксная форма: {' '.join(postfix)}")
            process(postfix)
        else:
            print("\n((3 + 1) * 3) / ((9 - 5) + 2) - (3 * (7 - 4) + 6)")
            print(f"Постфиксная форма: {BOOK_EXAMPLE}")
            process(BOOK_EXAMPLE.split())


if __name__ == "__main__":
    main()
