"""Problema 2: pentru A = {a1, a2, a3, a4} (citite de la tastatură) se afișează
toate permutările, toate combinările și toate aranjamentele de m = 3 elemente.

Generarea se face prin backtracking pe vectori (liste):
  - sol[]  - vectorul soluției curente (indici în A);
  - used[] - vector de marcaje: used[i] == True dacă A[i] e deja în soluție.
"""

N = 4
M = 3


def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  Introduceți un număr întreg.")
        except EOFError:
            raise SystemExit("\nIntrare încheiată.")


def read_set(n):
    """Citește n numere întregi distincte (o mulțime nu are elemente repetate)."""
    a = []
    while len(a) < n:
        x = read_int(f"a{len(a) + 1} = ")
        if x in a:
            print("  Elementul există deja în mulțime, introduceți altul.")
            continue
        a.append(x)
    return a


def aranjamente(a, k):
    """Toate aranjamentele de k elemente din a (ordinea contează).
    Pentru k == len(a) se obțin permutările."""
    n = len(a)
    sol = [0] * k
    used = [False] * n
    result = []

    def back(pos):
        if pos == k:
            result.append([a[i] for i in sol])
            return
        for i in range(n):
            if not used[i]:
                used[i] = True
                sol[pos] = i
                back(pos + 1)
                used[i] = False

    back(0)
    return result


def combinari(a, k):
    """Toate combinările de k elemente din a (ordinea nu contează):
    indicii se aleg strict crescător, deci fiecare submulțime apare o singură dată."""
    n = len(a)
    sol = [0] * k
    result = []

    def back(pos, start):
        if pos == k:
            result.append([a[i] for i in sol])
            return
        # rămân k - pos poziții de completat, deci i nu poate depăși n - (k - pos)
        for i in range(start, n - (k - pos) + 1):
            sol[pos] = i
            back(pos + 1, i + 1)

    back(0, 0)
    return result


def show(title, items):
    print(f"\n{title} — {len(items)} în total:")
    width = len(str(len(items)))
    for idx, item in enumerate(items, 1):
        print(f"  {idx:>{width}}. ({', '.join(map(str, item))})")


def main():
    print(f"Introduceți cele {N} elemente ale mulțimii A:")
    a = read_set(N)
    print(f"\nA = {{{', '.join(map(str, a))}}}")

    show("Permutări ale lui A", aranjamente(a, N))
    show(f"Combinări de {M} elemente", combinari(a, M))
    show(f"Aranjamente de {M} elemente", aranjamente(a, M))


if __name__ == "__main__":
    main()
