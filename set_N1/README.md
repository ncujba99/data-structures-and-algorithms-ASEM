# Set de probleme N1 — Elemente de combinatorică și backtracking

Fiecare problemă este rezolvată de două ori, în Python și în C++, cu același algoritm și aceeași ieșire. Fiecare are propria documentație, care începe cu matematica (definiții, formule, demonstrații) și continuă cu algoritmul, diagramele și exemple de rulare.

```
set_N1/
├── README.md                       ← acest fișier (index)
├── docs/
│   ├── problema1.md                ← P(n), C(n,m), A(n,m): formule și calcul
│   ├── problema2.md                ← generarea pe vectori pentru A = {a1..a4}
│   ├── problema3a_permutari.md     ← toate permutările a n elemente
│   └── problema3b_ture.md          ← n ture neatacate pe tabla n × n
├── python/   problema1.py   problema2.py   problema3_permutari.py   problema3_ture.py
└── cpp/      problema1.cpp  problema2.cpp  problema3_permutari.cpp  problema3_ture.cpp
```

| Problema | Documentație | Ce face | Matematica de bază |
|---|---|---|---|
| 1 (obligatorie) | [docs/problema1.md](docs/problema1.md) | **numără** permutările, combinările și aranjamentele | $P(n)=n!$, $A(n,m)=\frac{n!}{(n-m)!}$, $C(n,m)=\frac{n!}{m!(n-m)!}$ |
| 2 (obligatorie) | [docs/problema2.md](docs/problema2.md) | **generează** permutările lui A = {a1..a4}, combinările și aranjamentele de 3 | 24 permutări, 4 combinări, 24 aranjamente |
| 3a (opțională) | [docs/problema3a_permutari.md](docs/problema3a_permutari.md) | generează toate permutările a $n$ elemente | $n!$, formula lui Stirling |
| 3b (opțională) | [docs/problema3b_ture.md](docs/problema3b_ture.md) | generează toate așezările a $n$ ture neatacate | soluții = permutări ale lui $\{1..n\}$, deci $n!$ |

> Formulele sunt scrise în LaTeX (`$...$`) și se afișează pe GitHub/GitLab și în preview-ul din VS Code. Schemele sunt desenate cu caractere de chenar (`┌─┐ │ ▼`), deci arată la fel în orice editor, fără extensii.
>
> **Vizualizare interactivă:** fiecare problemă are și o animație pas cu pas în [`../visualizer/`](../visualizer/index.html).

---

## Metoda backtracking

Problemele 2 și 3 cer **generarea** tuturor obiectelor, nu doar numărarea lor. Toate folosesc **backtracking** (căutare cu revenire).

Soluția se construiește **pas cu pas** într-un vector `sol[0..k-1]`. La pasul `pos` se încearcă, pe rând, fiecare valoare posibilă pentru `sol[pos]`:

- dacă valoarea e **validă** (respectă condițiile problemei), se pune și se trece la pasul `pos + 1`;
- când vectorul e complet (`pos == k`), s-a găsit o soluție;
- după explorarea unei variante, aceasta se **anulează** (revenire) și se încearcă următoarea.

```
              ╭────────────────────────╮
              │       back(pos)        │
              ╰────────────┬───────────╯
                           │
                           ▼
              ┌────────────────────────┐         ╔══════════════════╗
              │       pos == k ?       ├── da ──►║ afișează soluția ║
              │    (vector complet)    │         ║      return      ║
              └────────────┬───────────┘         ╚══════════════════╝
                           │ nu
                           ▼
              ┌────────────────────────┐         ╔════════════════════╗
    ┌────────►│     pentru fiecare     ├────────►║    nu mai sunt     ║
    │ i++     │       candidat i       │ gata    ║ candidați: return  ║
    │         └────────────┬───────────┘         ╚════════════════════╝
    │                      │
    │                      ▼
    │         ┌────────────────────────┐
    ├── nu ───┤      candidatul i      │
    │         │      este valid?       │
    │         └────────────┬───────────┘
    │                      │ da
    │                      ▼
    │         ┌────────────────────────┐
    │         │      sol[pos] = i      │
    │         │  marchează i folosit   │
    │         └────────────┬───────────┘
    │                      │
    │                      ▼
    │         ╭────────────────────────╮
    │         │     back(pos + 1)      │
    │         ╰────────────┬───────────╯
    │                      │
    │                      ▼
    │         ┌────────────────────────┐
    └─────────┤     demarchează i      │
              │       (revenire)       │
              └────────────────────────┘
```

Execuția este parcurgerea în adâncime (DFS) a unui **arbore de căutare**: nivelul = poziția completată, ramurile = candidații, frunzele = soluțiile. Arborii concreți sunt desenați în documentația fiecărei probleme.

| Problema | Vector soluție | Condiția de validitate | Vector de marcaje |
|---|---|---|---|
| 2, 3a — permutări / aranjamente | `sol[pos]` = indice în `a` | `a[i]` nefolosit | `used[i]` |
| 2 — combinări | `sol[pos]` = indice în `a` | `i > sol[pos-1]` (indici strict crescători) | — |
| 3b — ture | `c[i]` = coloana turei de pe linia `i` | coloana `j` liberă | `col_used[j]` |

---

## Compilare și rulare

### Python (3.8+)

```sh
cd python
python3 problema1.py
python3 problema2.py
python3 problema3_permutari.py
python3 problema3_ture.py
```

### C++ (C++17)

```sh
cd cpp
g++ -std=c++17 -O2 -Wall -o problema1 problema1.cpp && ./problema1
g++ -std=c++17 -O2 -Wall -o problema2 problema2.cpp && ./problema2
g++ -std=c++17 -O2 -Wall -o problema3_permutari problema3_permutari.cpp && ./problema3_permutari
g++ -std=c++17 -O2 -Wall -o problema3_ture problema3_ture.cpp && ./problema3_ture
```

### Diferențe între cele două implementări

| Aspect | Python | C++ |
|---|---|---|
| Tip pentru P, C, A | `int` (precizie nelimitată) | `unsigned long long` (64 biți, suficient pentru $n \le 20$) |
| Vectori | `list` | `std::vector` / tablou static (`c[]`, `colUsed[]` la ture) |
| Afișare rapidă | scriere directă în `sys.stdout` | `std::ios::sync_with_stdio(false)` |
| Validarea intrării | `try/except ValueError` | `cin.fail()` + `cin.clear()` / `cin.ignore()` |

Pentru aceleași date de intrare, cele două versiuni produc ieșire **identică** (verificat cu `diff`).
