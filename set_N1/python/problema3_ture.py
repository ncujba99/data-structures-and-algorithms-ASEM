"""Problema 3 (b): toate modurile de a așeza n ture pe o tablă n x n
astfel încât oricare două să nu se atace.

Pe fiecare linie i se pune exact o tură, în coloana c[i]. Două ture se atacă
doar dacă sunt pe aceeași linie (imposibil prin construcție) sau pe aceeași
coloană, deci c[1..n] trebuie să conțină coloane distincte: soluțiile sunt
exact permutările mulțimii {1, ..., n}, iar numărul lor este n!.

Backtracking: col_used[j] == True dacă pe coloana j se află deja o tură.
"""

import sys
from math import factorial

MAX_N = 20
CONFIRM_FROM = 9  # 9! = 362 880 soluții — cerem confirmare înainte de afișare


def read_int(prompt, lo, hi):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("  Introduceți un număr întreg.")
            continue
        except EOFError:
            raise SystemExit("\nIntrare încheiată.")
        if lo <= value <= hi:
            return value
        print(f"  Valoarea trebuie să fie în intervalul [{lo}, {hi}].")


def ture(n, out):
    """Scrie în `out` toate soluțiile în forma c1,c2,...,cn. Returnează numărul lor."""
    c = [0] * (n + 1)              # c[i] = coloana turei de pe linia i (indexare de la 1)
    col_used = [False] * (n + 1)
    count = 0

    def back(i):
        nonlocal count
        if i > n:
            count += 1
            out.write(",".join(map(str, c[1:])) + "\n")
            return
        for j in range(1, n + 1):
            if not col_used[j]:     # coloana j e liberă => tura (i, j) nu e atacată
                col_used[j] = True
                c[i] = j
                back(i + 1)
                col_used[j] = False

    back(1)
    return count


def main():
    n = read_int(f"n (1..{MAX_N}) = ", 1, MAX_N)
    total = factorial(n)
    print(f"Număr de soluții: {n}! = {total}")

    if n >= CONFIRM_FROM:
        try:
            answer = input("Sunt foarte multe soluții. Le afișăm pe toate? (d/n) ")
        except EOFError:
            answer = "n"
        if answer.strip().lower() not in ("d", "da", "y", "yes"):
            return

    print()
    ture(n, sys.stdout)


if __name__ == "__main__":
    main()
