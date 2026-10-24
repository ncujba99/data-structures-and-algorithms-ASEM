"""Ввод с клавиатуры с контролем ошибок."""


def read_line(prompt):
    """Читает строку; при конце ввода (Ctrl+D / Ctrl+Z) завершает программу."""
    try:
        return input(prompt).strip()
    except EOFError:
        print("\nВвод завершён.")
        raise SystemExit(0)


def read_non_empty(prompt):
    while True:
        s = read_line(prompt)
        if s:
            return s
        print("  Строка не должна быть пустой.")


def read_int(prompt, lo, hi):
    while True:
        try:
            value = int(read_line(prompt))
        except ValueError:
            print("  Введите целое число.")
            continue
        if lo <= value <= hi:
            return value
        print(f"  Число должно быть в диапазоне [{lo}, {hi}].")


def read_yes_no(prompt):
    """Принимает: да / д / yes / y  и  нет / н / no / n  (в любом регистре)."""
    while True:
        s = read_line(prompt).lower()
        if s in ("да", "д", "yes", "y"):
            return True
        if s in ("нет", "н", "no", "n"):
            return False
        print("  Ответьте «да» или «нет».")

