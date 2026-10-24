"""Problema 3 (a): toate permutările mulțimii A = {a1, ..., an},
n și elementele citite de la tastatură.

Backtracking pe vectori: sol[] este permutarea curentă (indici în A),
used[] marchează elementele deja folosite.
"""

import sys

MAX_N = 10  # 10! = 3 628 800 linii; peste atât afișarea devine nerealistă


def read_int(prompt, lo=None, hi=None):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("  Introduceți un număr întreg.")
            continue
        except EOFError:
            raise SystemExit("\nIntrare încheiată.")
        if (lo is None or value >= lo) and (hi is None or value <= hi):
            return value
        print(f"  Valoarea trebuie să fie în intervalul [{lo}, {hi}].")


def read_set(n):
    a = []
    while len(a) < n:
        x = read_int(f"a{len(a) + 1} = ")
        if x in a:
            print("  Elementul există deja în mulțime, introduceți altul.")
            continue
        a.append(x)
    return a


def permutari(a, out):
    """Scrie în `out` toate permutările lui a, câte una pe linie. Returnează numărul lor."""
    n = len(a)
    sol = [0] * n
    used = [False] * n
    count = 0

    def back(pos):
        nonlocal count
        if pos == n:
            count += 1
            out.write(f"{count}. ({', '.join(str(a[i]) for i in sol)})\n")
            return
        for i in range(n):
            if not used[i]:
                used[i] = True
                sol[pos] = i
                back(pos + 1)
                used[i] = False

    back(0)
    return count


def main():
    n = read_int(f"n (1..{MAX_N}) = ", 1, MAX_N)
    print(f"Introduceți cele {n} elemente ale mulțimii A:")
    a = read_set(n)

    print(f"\nPermutările mulțimii A = {{{', '.join(map(str, a))}}}:")
    total = permutari(a, sys.stdout)
    print(f"Total: {total} permutări ({n}! = {total})")


if __name__ == "__main__":
    main()
