"""Problema 1: numărul de permutări, combinări și aranjamente.

P(n)    = n!
C(n, m) = n! / (m! * (n - m)!)
A(n, m) = n! / (n - m)!
"""


def read_int(prompt, lo, hi):
    """Citește un număr întreg din intervalul [lo, hi], repetând la input greșit."""
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


def permutari(n):
    """P(n) = 1 * 2 * ... * n"""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def aranjamente(n, m):
    """A(n, m) = (n - m + 1) * ... * n  (produsul ultimelor m numere)"""
    result = 1
    for i in range(n - m + 1, n + 1):
        result *= i
    return result


def combinari(n, m):
    """C(n, m) calculat iterativ; la fiecare pas rezultatul este întreg
    (C(n-k+i, i)), deci nu apar fracții și nici valori intermediare uriașe."""
    k = min(m, n - m)  # C(n, m) = C(n, n - m)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def main():
    n = read_int("n (1..20) = ", 1, 20)
    m = read_int(f"m (0..{n}) = ", 0, n)

    print()
    print(f"Permutări:    P({n}) = {n}! = {permutari(n)}")
    print(f"Combinări:    C({n}, {m}) = {combinari(n, m)}")
    print(f"Aranjamente:  A({n}, {m}) = {aranjamente(n, m)}")


if __name__ == "__main__":
    main()
