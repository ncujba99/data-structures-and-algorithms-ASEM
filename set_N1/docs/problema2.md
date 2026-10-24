# Problema 2 — Generarea permutărilor, combinărilor și aranjamentelor pe vectori

> Cod: [`python/problema2.py`](../python/problema2.py) · [`cpp/problema2.cpp`](../cpp/problema2.cpp) · [← înapoi la index](../README.md)

**Enunț.** Folosind structuri vectoriale, să se găsească toate permutările mulțimii $A = \{a_1, a_2, a_3, a_4\}$ de tip întreg, elementele căreia se introduc de la tastatură. Să se afișeze toate combinările și aranjamentele posibile formate din $m = 3$ elemente.

Spre deosebire de [problema 1](problema1.md), aici nu ajunge să **numărăm**: trebuie să **generăm** (să afișăm) fiecare obiect.

---

## 1. Matematica

### 1.1 Obiectele generate

Fie $A = \{a_1, a_2, a_3, a_4\}$, cu elemente **distincte** ($n = 4$), și $m = 3$.

| Obiect | Definiție formală | Formula | Câte sunt |
|---|---|---|---|
| Permutare | bijecție $\sigma : \{1,2,3,4\} \to A$, adică un șir $(x_1,x_2,x_3,x_4)$ cu toți $x_i$ distincți | $P(4) = 4!$ | **24** |
| Aranjament de 3 | injecție $f : \{1,2,3\} \to A$, adică un șir $(x_1,x_2,x_3)$ cu $x_i$ distincți | $A(4,3) = \dfrac{4!}{1!}$ | **24** |
| Combinare de 3 | submulțime $S \subseteq A$ cu $\lvert S \rvert = 3$ | $C(4,3) = \dfrac{4!}{3!\,1!}$ | **4** |

Demonstrația formulelor se găsește în [problema 1](problema1.md#1-matematica).

### 1.2 O observație: de ce $A(4,3) = P(4)$?

$$A(n, n-1) = \frac{n!}{1!} = n! = P(n)$$

Explicație: un aranjament de $n-1$ elemente lasă deoparte **exact un** element. Adăugându-l la final se obține o permutare unică, iar invers, ștergând ultimul element al unei permutări se obține un aranjament unic. Este o bijecție:

```
aranjament (3, 1, 4)   ⟷   permutare (3, 1, 4, 2)      (2 este singurul rămas)
```

### 1.3 Legătura combinări ↔ aranjamente

$$A(4,3) = C(4,3) \cdot 3! \qquad\Longleftrightarrow\qquad 24 = 4 \cdot 6$$

Fiecare dintre cele 4 combinări generează, prin toate cele $3! = 6$ ordonări ale sale, 6 aranjamente distincte.

### 1.4 Reprezentarea prin indici

În program un obiect nu se reține prin valori, ci prin **indicii** elementelor în $A$, adică un vector $sol = (i_1, \ldots, i_k)$ cu $i_j \in \{0, \ldots, n-1\}$:

| Obiect | Condiția asupra vectorului de indici |
|---|---|
| Aranjament / permutare | $i_1, \ldots, i_k$ sunt **distincte** |
| Combinare | $0 \le i_1 < i_2 < \ldots < i_k \le n-1$ (**strict crescători**) |

**De ce strict crescători la combinări?** O submulțime are o singură listare în ordine crescătoare. Impunând $i_1 < i_2 < i_3$, fiecare submulțime este generată **exact o dată**, iar $\{1,2,3\}$, $\{2,1,3\}$, … nu mai apar ca duplicate.

**Limita superioară a indicilor.** Dacă indicii sunt strict crescători și mai avem de ales încă $k - p$ indici după poziția $p$ (numerotând de la 0), atunci:

$$i_p \le n - (k - p)$$

Altfel nu mai rămân destui indici mai mari. Pentru $n = 4$, $k = 3$: $i_0 \le 1$, $i_1 \le 2$, $i_2 \le 3$.

### 1.5 Ordinea lexicografică

Soluțiile se afișează în **ordine lexicografică** a vectorului de indici: $(i_1, \ldots, i_k) < (j_1, \ldots, j_k)$ dacă la prima poziție $p$ unde diferă avem $i_p < j_p$, adică ordinea „din dicționar”. Este o consecință directă a faptului că algoritmul încearcă candidații de la indicele mic la cel mare.

---

## 2. Algoritmul — backtracking pe vectori

(Metoda generală este descrisă în [README](../README.md#metoda-backtracking).)

### 2.1 Structurile de date

| Vector | Rol |
|---|---|
| `a[0..3]` | elementele mulțimii, citite de la tastatură |
| `sol[0..k-1]` | soluția curentă — **indici** în `a` |
| `used[0..3]` | `used[i] == true` dacă `a[i]` e deja în soluție — test în $O(1)$ |

### 2.2 Aranjamente (și permutări)

```
back(pos):
    dacă pos == k:  afișează a[sol[0]], ..., a[sol[k-1]];  return
    pentru i = 0..n-1:
        dacă nu used[i]:
            used[i] = true;  sol[pos] = i
            back(pos + 1)
            used[i] = false                 ← revenire (backtrack)
```

Aceeași funcție dă permutările (`aranjamente(a, 4)`) și aranjamentele de 3 (`aranjamente(a, 3)`).

**Arborele de căutare** pentru aranjamentele de 3 din $\{1,2,3,4\}$. Este desenată doar ramura care începe cu 1; ramurile 2, 3 și 4 (punctate) sunt analoge. Casetele duble sunt frunzele, adică soluțiile:

```
                                                  ╭───────╮
                                                  │ start │
                                                  ╰───┬───╯
                             ┌────────────────────────┴────────┬───────┬───────┐
                             ▼                                 ▼       ▼       ▼
                           ┌───┐                            ┌┄┄┄┄┄┐ ┌┄┄┄┄┄┐ ┌┄┄┄┄┄┐
                           │ 1 │                            ┆ 2 … ┆ ┆ 3 … ┆ ┆ 4 … ┆
                           └─┬─┘                            └┄┄┄┄┄┘ └┄┄┄┄┄┘ └┄┄┄┄┄┘
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
      ┌─────┐             ┌─────┐             ┌─────┐
      │ 1,2 │             │ 1,3 │             │ 1,4 │
      └──┬──┘             └──┬──┘             └──┬──┘
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    ▼         ▼         ▼         ▼         ▼         ▼
╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗
║ 1,2,3 ║ ║ 1,2,4 ║ ║ 1,3,2 ║ ║ 1,3,4 ║ ║ 1,4,2 ║ ║ 1,4,3 ║
╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝
```

Număr de frunze: $4 \cdot 3 \cdot 2 = 24 = A(4,3)$. Pe nivelul $p$ se află $A(4, p)$ noduri.

**Urmărirea vectorilor** ($A = \{1,2,3,4\}$, $k = 3$; `_` = poziție necompletată):

```
pas                          sol        used (a1 a2 a3 a4)    acțiune
---------------------------------------------------------------------------
back(0)  i=0                 [0 _ _]    T  F  F  F            pune a1
 back(1) i=0                                                  a1 folosit → sare
 back(1) i=1                 [0 1 _]    T  T  F  F            pune a2
  back(2) i=0, i=1                                            folosiți → sare
  back(2) i=2                [0 1 2]    T  T  T  F            pune a3
   back(3)                                                    pos == 3 → afișează (1, 2, 3)
  back(2) revenire           [0 1 _]    T  T  F  F            scoate a3
  back(2) i=3                [0 1 3]    T  T  F  T            pune a4
   back(3)                                                    afișează (1, 2, 4)
  back(2) revenire           [0 1 _]    T  T  F  F            scoate a4
 back(1) revenire            [0 _ _]    T  F  F  F            scoate a2
 back(1) i=2                 [0 2 _]    T  F  T  F            pune a3
 ...
```

### 2.3 Combinări

```
back(pos, start):
    dacă pos == k:  afișează soluția;  return
    pentru i = start .. n - (k - pos):        ← limita din §1.4
        sol[pos] = i
        back(pos + 1, i + 1)                  ← următorul indice e strict mai mare
```

Nu mai e nevoie de `used[]`: condiția $i_{p+1} > i_p$ garantează singură că indicii sunt distincți.

| `pos` | interval pentru `i` ($n=4$, $k=3$) | motiv |
|---|---|---|
| 0 | 0 … 1 | după el mai trebuie 2 indici |
| 1 | start … 2 | după el mai trebuie 1 indice |
| 2 | start … 3 | ultimul |

**Arborele complet** pentru combinările de 3 din $\{1,2,3,4\}$:

```
                            ╭───────╮
                            │ start │
                            ╰───┬───╯
                     ┌──────────┴───────────┐
                     ▼                      ▼
                   ┌───┐                  ┌───┐
                   │ 1 │                  │ 2 │
                   └─┬─┘                  └─┬─┘
           ┌─────────┴─────────┐            │
           ▼                   ▼            ▼
        ┌─────┐             ┌─────┐      ┌─────┐
        │ 1,2 │             │ 1,3 │      │ 2,3 │
        └──┬──┘             └──┬──┘      └──┬──┘
     ┌─────┴──────┐            │            │
     ▼            ▼            ▼            ▼
╔═════════╗  ╔═════════╗  ╔═════════╗  ╔═════════╗
║ {1,2,3} ║  ║ {1,2,4} ║  ║ {1,3,4} ║  ║ {2,3,4} ║
╚═════════╝  ╚═════════╝  ╚═════════╝  ╚═════════╝
```

Ramurile „3 …” și „4 …” de pe primul nivel nu sunt încercate deloc: după 3 rămâne un singur element, iar e nevoie de încă două. Această **tăiere a ramurilor sterile** face ca fiecare nod vizitat să ducă la cel puțin o soluție.

### 2.4 Complexitate

| Generare | Soluții | Timp | Memorie suplimentară |
|---|---|---|---|
| Aranjamente de $k$ din $n$ | $A(n,k)$ | $O(k \cdot A(n,k))$ | $O(n)$ + lista rezultatelor |
| Combinări de $k$ din $n$ | $C(n,k)$ | $O(k \cdot C(n,k))$ | $O(k)$ + lista rezultatelor |

Pentru $n = 4$ totul este instantaneu.

---

## 3. Validarea datelor

- Se citesc **exact 4** numere întregi. O valoare care nu e număr se recitește.
- Elementele trebuie să fie **distincte**, pentru că o mulțime nu are repetiții. Altfel, de exemplu pentru $\{1, 1, 2, 3\}$, s-ar afișa „permutări” identice. Un element repetat se cere din nou.
- Pot fi negative sau mari; algoritmul lucrează cu indici, deci valorile nu contează.

---

## 4. Exemplu de rulare (prescurtat)

```
Introduceți cele 4 elemente ale mulțimii A:
a1 = 1
a2 = 2
a3 = 3
a4 = 4

A = {1, 2, 3, 4}

Permutări ale lui A — 24 în total:
   1. (1, 2, 3, 4)
   2. (1, 2, 4, 3)
   ...
  24. (4, 3, 2, 1)

Combinări de 3 elemente — 4 în total:
  1. (1, 2, 3)
  2. (1, 2, 4)
  3. (1, 3, 4)
  4. (2, 3, 4)

Aranjamente de 3 elemente — 24 în total:
   1. (1, 2, 3)
   2. (1, 2, 4)
   ...
  24. (4, 3, 2)
```
