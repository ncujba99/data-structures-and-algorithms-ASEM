# Problema 3 (b) — n ture care nu se atacă

> Cod: [`python/problema3_ture.py`](../python/problema3_ture.py) · [`cpp/problema3_ture.cpp`](../cpp/problema3_ture.cpp) · [← înapoi la index](../README.md)

**Enunț (opțional).** Se consideră o tablă de șah de dimensiuni $n \times n$ ($n \le 20$, citit de la tastatură). Să se afișeze toate posibilitățile de a așeza $n$ ture pe tablă astfel încât oricare două să nu se atace. Două ture se atacă dacă se găsesc pe aceeași linie sau pe aceeași coloană. O soluție se afișează pe o linie ca secvența $c_1, c_2, \ldots, c_n$, unde $c_i$ este coloana turei de pe linia $i$.

> Varianta rusă a enunțului spune „двух ладей” („două ture”), dar formatul răspunsului (un vector $c_1 \ldots c_n$, câte o tură pe fiecare linie) și varianta română arată că se cer **$n$ ture**. Cazul cu două ture este tratat totuși în §1.6.

---

## 1. Matematica

### 1.1 Modelul

- **Tabla** este mulțimea celulelor $T = \{1, \ldots, n\} \times \{1, \ldots, n\}$; celula $(i, j)$ = linia $i$, coloana $j$.
- **Relația de atac.** Două ture distincte, în $(i_1, j_1)$ și $(i_2, j_2)$, se atacă dacă și numai dacă

$$i_1 = i_2 \quad\text{sau}\quad j_1 = j_2.$$

- **Soluția** este o mulțime de $n$ celule din care nicio pereche nu se atacă.

### 1.2 Cel mult $n$ ture

**Afirmație.** Pe o tablă $n \times n$ se pot așeza cel mult $n$ ture care nu se atacă.

**Demonstrație (principiul cutiei).** Fiecare tură stă pe una din cele $n$ linii. Dacă ar fi $n + 1$ ture, două ar ajunge pe aceeași linie și s-ar ataca. ∎

Deci cerința „$n$ ture” înseamnă *numărul maxim posibil*, iar într-o soluție fiecare linie și fiecare coloană conțin **exact o** tură.

### 1.3 Teorema: soluțiile sunt exact permutările lui $\{1, \ldots, n\}$

Reprezentăm o așezare prin vectorul $c = (c_1, \ldots, c_n)$, unde tura de pe linia $i$ stă în $(i, c_i)$.

1. **Liniile.** Reprezentarea pune *prin construcție* exact o tură pe fiecare linie, deci atacul pe linie e imposibil.
2. **Coloanele.** Turele $i \ne j$ nu se atacă pe coloană $\iff c_i \ne c_j$.
3. Deci așezarea e validă $\iff$ valorile $c_1, \ldots, c_n \in \{1, \ldots, n\}$ sunt **toate distincte** $\iff$ $c$ este o **permutare** a lui $\{1, \ldots, n\}$.

$$\boxed{\text{numărul de soluții} = P(n) = n!}$$

Problema este deci un caz particular al [problemei 3 (a)](problema3a_permutari.md), cu $A = \{1, 2, \ldots, n\}$.

### 1.4 Matricea de permutare

Echivalent, o soluție este o **matrice de permutare**: o matrice $n \times n$ cu elemente 0/1, cu exact un 1 pe fiecare linie și pe fiecare coloană. Pentru $c = (2, 4, 1, 3)$:

$$
M_c = \begin{pmatrix}
0 & 1 & 0 & 0 \\
0 & 0 & 0 & 1 \\
1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0
\end{pmatrix},
\qquad M_{i,j} = 1 \iff j = c_i
$$

```
         1   2   3   4
       ┌───┬───┬───┬───┐
     1 │   │ T │   │   │   c1 = 2
       ├───┼───┼───┼───┤
     2 │   │   │   │ T │   c2 = 4
       ├───┼───┼───┼───┤
     3 │ T │   │   │   │   c3 = 1
       ├───┼───┼───┼───┤
     4 │   │   │ T │   │   c4 = 3
       └───┴───┴───┴───┘
```

**Contraexemplu:** $c = (2, 4, 2, 3)$ nu e permutare ($c_1 = c_3 = 2$), deci turele de pe liniile 1 și 3 se atacă pe coloana 2:

```
         1   2   3   4
       ┌───┬───┬───┬───┐
     1 │   │ T │   │   │
       ├───┼───┼───┼───┤
     2 │   │ ↓ │   │ T │
       ├───┼───┼───┼───┤
     3 │   │ T │   │   │   ← atacată de tura de pe linia 1
       ├───┼───┼───┼───┤
     4 │   │   │ T │   │
       └───┴───┴───┴───┘
```

### 1.5 Comparație cu problema celor $n$ regine

Regina atacă și pe **diagonale**, deci condiției $c_i \ne c_j$ i se adaugă

$$|c_i - c_j| \ne |i - j| \quad \text{pentru orice } i \ne j.$$

Numărul de soluții scade drastic:

| $n$ | 4 | 5 | 6 | 8 | 10 |
|---|---|---|---|---|---|
| ture ($n!$) | 24 | 120 | 720 | 40 320 | 3 628 800 |
| regine | 2 | 10 | 4 | 92 | 724 |

Pentru regine nu există o formulă închisă, ele se pot doar număra prin căutare. Pentru ture răspunsul este simplu: $n!$.

### 1.6 Generalizare: $k$ ture ($k \le n$) și cazul a două ture

Pentru a așeza $k$ ture neatacate: alegem cele $k$ linii folosite, $C(n,k)$ moduri; cele $k$ coloane folosite, tot $C(n,k)$; apoi le asociem bijectiv, $k!$ moduri:

$$R(n, k) = C(n, k)^2 \cdot k!$$

| Caz | Formula | Verificare |
|---|---|---|
| $k = n$ | $1^2 \cdot n! = n!$ | coincide cu §1.3 ✓ |
| $k = 1$ | $n^2$ | orice celulă ✓ |
| $k = 2$ (varianta rusă) | $C(n,2)^2 \cdot 2 = \dfrac{n^2 (n-1)^2}{2}$ | prima tură: $n^2$ celule; a doua: $(n-1)^2$ celule neatacate; împărțim la 2 pentru că turele sunt identice ✓ |

De exemplu, pe tabla clasică $8 \times 8$ două ture neatacate se pot pune în $\dfrac{64 \cdot 49}{2} = 1568$ moduri.

---

## 2. Algoritmul — backtracking pe linii

La pasul $i$ se pune tura de pe linia $i$, încercând pe rând coloanele $j = 1, \ldots, n$. Vectorul `col_used[j]` (`colUsed[j]` în C++) reține dacă pe coloana $j$ se află deja o tură. Condiția de validitate este „coloana $j$ e liberă”.

```
back(i):
    dacă i > n:  afișează c[1], ..., c[n];  return
    pentru j = 1..n:
        dacă nu col_used[j]:              ← tura (i, j) nu e atacată
            col_used[j] = true;  c[i] = j
            back(i + 1)
            col_used[j] = false
```

| Concept din backtracking | Semnificația la ture |
|---|---|
| nivelul $i$ din arbore | linia tablei |
| candidatul $j$ | coloana în care încercăm tura |
| `col_used[j]` | coloana $j$ e deja ocupată |
| frunza | tablă completă, fără atacuri |

Liniile nu au nevoie de vector de marcaje: fiecare nivel al recursiei corespunde altei linii.

**Arborele pentru $n = 3$.** Un nod $c_i = j$ înseamnă „tura de pe linia $i$ stă pe coloana $j$”. Casetele punctate (✗) sunt coloanele deja ocupate: acolo nu se coboară. Casetele duble sunt soluțiile:

```
                                                           ╭─────────────╮
                                                           │ tablă goală │
                                                           ╰──────┬──────╯
                   ┌──────────────────────────────────────────────┼──────────┐
                   ▼                                              ▼          ▼
              ┌────────┐                                      ┌────────┐ ┌────────┐
              │ c1 = 1 │                                      │ c1 = 2 │ │ c1 = 3 │
              └────┬───┘                                      └───┬────┘ └───┬────┘
   ┌───────────────┼────────────────────────────┐                 │          │
   ▼               ▼                            ▼                 ▼          ▼
┌┄┄┄┄┄┐       ┌────────┐                   ┌────────┐         ┌┄┄┄┄┄┄┄┐  ┌┄┄┄┄┄┄┄┐
┆ 1 ✗ ┆       │ c2 = 2 │                   │ c2 = 3 │         ┆   …   ┆  ┆   …   ┆
└┄┄┄┄┄┘       └────┬───┘                   └────┬───┘         ┆ 2,1,3 ┆  ┆ 3,1,2 ┆
                   │                            │             ┆ 2,3,1 ┆  ┆ 3,2,1 ┆
                   │                            │             └┄┄┄┄┄┄┄┘  └┄┄┄┄┄┄┄┘
           ┌───────┼─────────┐        ┌─────────┼────────┐
           ▼       ▼         ▼        ▼         ▼        ▼
        ┌┄┄┄┄┄┐ ┌┄┄┄┄┄┐ ╔════════╗ ┌┄┄┄┄┄┐ ╔════════╗ ┌┄┄┄┄┄┐
        ┆ 1 ✗ ┆ ┆ 2 ✗ ┆ ║ c3 = 3 ║ ┆ 1 ✗ ┆ ║ c3 = 2 ║ ┆ 3 ✗ ┆
        └┄┄┄┄┄┘ └┄┄┄┄┄┘ ║ 1,2,3  ║ └┄┄┄┄┄┘ ║ 1,3,2  ║ └┄┄┄┄┄┘
                        ╚════════╝         ╚════════╝
```

**Complexitate:** $O(n \cdot n!)$ timp (§1.4 din [problema 3 (a)](problema3a_permutari.md#14-dimensiunea-arborelui-de-căutare)), $O(n)$ memorie.

---

## 3. Limita practică — de ce programul cere confirmare

| $n$ | soluții ($n!$) | volum de text afișat |
|---|---|---|
| 4 | 24 | < 1 KB |
| 8 | 40 320 | ~640 KB |
| 9 | 362 880 | ~6.5 MB |
| 10 | 3 628 800 | ~76 MB |
| 12 | 479 001 600 | ~13 GB |
| 15 | $1.3 \cdot 10^{12}$ | ~47 TB |
| 20 | $2.43 \cdot 10^{18}$ | ~$10^{20}$ octeți — imposibil |

Chiar la un miliard de soluții pe secundă, pentru $n = 20$:

$$\frac{2.43 \cdot 10^{18}}{10^9 \ \text{sol/s}} \approx 2.43 \cdot 10^{9}\ \text{s} \approx 77\ \text{ani}.$$

De aceea programul:

1. afișează întâi **numărul** de soluții, $n!$, calculat instantaneu cu formula din §1.3;
2. pentru $n \ge 9$ întreabă `Le afișăm pe toate? (d/n)` înainte de listare.

Ieșirea se poate redirecționa și într-un fișier: `./problema3_ture > solutii.txt`.

---

## 4. Exemplu de rulare

```
n (1..20) = 3
Număr de soluții: 3! = 6

1,2,3
1,3,2
2,1,3
2,3,1
3,1,2
3,2,1
```

Așezările corespunzătoare pe tablă:

```
    1,2,3          1,3,2          2,1,3          2,3,1          3,1,2          3,2,1
┌───┬───┬───┐  ┌───┬───┬───┐  ┌───┬───┬───┐  ┌───┬───┬───┐  ┌───┬───┬───┐  ┌───┬───┬───┐
│ T │   │   │  │ T │   │   │  │   │ T │   │  │   │ T │   │  │   │   │ T │  │   │   │ T │
├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤
│   │ T │   │  │   │   │ T │  │ T │   │   │  │   │   │ T │  │ T │   │   │  │   │ T │   │
├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤  ├───┼───┼───┤
│   │   │ T │  │   │ T │   │  │   │   │ T │  │ T │   │   │  │   │ T │   │  │ T │   │   │
└───┴───┴───┘  └───┴───┴───┘  └───┴───┴───┘  └───┴───┴───┘  └───┴───┴───┘  └───┴───┴───┘
```
