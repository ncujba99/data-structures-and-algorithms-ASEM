# Problema 3 (a) — Toate permutările unei mulțimi cu n elemente

> Cod: [`python/problema3_permutari.py`](../python/problema3_permutari.py) · [`cpp/problema3_permutari.cpp`](../cpp/problema3_permutari.cpp) · [← înapoi la index](../README.md)

**Enunț (opțional).** Să se găsească toate permutările mulțimii $A = \{a_1, a_2, \ldots, a_n\}$ de tip întreg, unde numărul $n$ și elementele se introduc de la tastatură. Să se afișeze toate permutările posibile.

Este generalizarea [problemei 2](problema2.md) de la $n = 4$ la $n$ oarecare.

---

## 1. Matematica

### 1.1 Definiție și număr

O **permutare** a mulțimii $A$ (cu $|A| = n$, elemente distincte) este o funcție bijectivă $\sigma : \{1, \ldots, n\} \to A$, adică un șir $(a_{\sigma(1)}, \ldots, a_{\sigma(n)})$ în care fiecare element apare exact o dată. Numărul lor (demonstrat în [problema 1](problema1.md#13-permutări)):

$$\boxed{P(n) = n! = \prod_{k=1}^{n} k}$$

### 1.2 Construcția recursivă

Permutările se pot construi recursiv: alegem primul element ($n$ variante), apoi orice permutare a celor $n-1$ rămase.

$$P(n) = n \cdot P(n-1), \qquad P(0) = 1$$

Algoritmul face exact asta: fiecare nivel al recursiei fixează o poziție.

### 1.3 Cât de repede crește $n!$

$n!$ crește mai repede decât orice exponențială $c^n$. **Formula lui Stirling** dă o aproximare foarte bună:

$$n! \approx \sqrt{2\pi n}\,\left(\frac{n}{e}\right)^n$$

| $n$ | $n!$ | Stirling | eroare |
|---|---|---|---|
| 5 | 120 | 118.0 | 1.6 % |
| 10 | 3 628 800 | 3 598 696 | 0.8 % |
| 20 | $2.433 \cdot 10^{18}$ | $2.423 \cdot 10^{18}$ | 0.4 % |

Comparație:

| $n$ | $n^2$ | $2^n$ | $n!$ |
|---|---|---|---|
| 5 | 25 | 32 | 120 |
| 10 | 100 | 1 024 | 3 628 800 |
| 15 | 225 | 32 768 | 1 307 674 368 000 |
| 20 | 400 | 1 048 576 | 2 432 902 008 176 640 000 |

### 1.4 Dimensiunea arborelui de căutare

Pe nivelul $p$ al arborelui (după ce s-au completat $p$ poziții) se află câte un nod pentru fiecare aranjament de $p$ elemente, deci $A(n, p) = \dfrac{n!}{(n-p)!}$ noduri. Numărul total de noduri este:

$$\sum_{p=0}^{n} \frac{n!}{(n-p)!} \;=\; n! \sum_{j=0}^{n} \frac{1}{j!} \;\approx\; e \cdot n! \approx 2.718 \cdot n!$$

(pentru că $\sum_{j \ge 0} 1/j! = e$). Concluzie: backtracking-ul vizitează doar de **circa 2.7 ori** mai multe noduri decât numărul soluțiilor, deci este **optimal** până la un factor constant. Orice algoritm care afișează toate permutările face cel puțin $n!$ pași.

### 1.5 Ordinea lexicografică

Permutările (ca vectori de indici) se generează în **ordine lexicografică**: $(1,2,3) < (1,3,2) < (2,1,3) < (2,3,1) < (3,1,2) < (3,2,1)$. Prima permutare este cea identică, ultima este cea inversată.

---

## 2. Algoritmul

Este backtracking-ul de aranjamente din [problema 2](problema2.md#22-aranjamente-și-permutări), cu $k = n$:

```
back(pos):
    dacă pos == n:  afișează a[sol[0]], ..., a[sol[n-1]];  return
    pentru i = 0..n-1:
        dacă nu used[i]:
            used[i] = true;  sol[pos] = i
            back(pos + 1)
            used[i] = false
```

**Arborele de căutare** pentru $n = 3$, $A = \{1, 2, 3\}$:

```
                           ╭───────╮
                           │ start │
                           ╰───┬───╯
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
       ┌───┐                 ┌───┐                 ┌───┐
       │ 1 │                 │ 2 │                 │ 3 │
       └─┬─┘                 └─┬─┘                 └─┬─┘
    ┌────┴─────┐          ┌────┴─────┐          ┌────┴─────┐
    ▼          ▼          ▼          ▼          ▼          ▼
 ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
 │ 1,2 │    │ 1,3 │    │ 2,1 │    │ 2,3 │    │ 3,1 │    │ 3,2 │
 └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘
    │          │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼          ▼
╔═══════╗  ╔═══════╗  ╔═══════╗  ╔═══════╗  ╔═══════╗  ╔═══════╗
║ 1,2,3 ║  ║ 1,3,2 ║  ║ 2,1,3 ║  ║ 2,3,1 ║  ║ 3,1,2 ║  ║ 3,2,1 ║
╚═══════╝  ╚═══════╝  ╚═══════╝  ╚═══════╝  ╚═══════╝  ╚═══════╝
```

| Nivel $p$ | Ramuri pe nod | Noduri $= A(3,p)$ |
|---|---|---|
| 0 | 3 | 1 |
| 1 | 2 | 3 |
| 2 | 1 | 6 |
| 3 (frunze) | — | **6 = 3!** |

Total: $1 + 3 + 6 + 6 = 16 \approx e \cdot 3! = 16.3$, conform §1.4.

### Diferență față de problema 2

La problema 2 soluțiile se păstrează într-o listă și se afișează la final (sunt doar 24). Aici pot fi milioane, așa că fiecare permutare se **afișează imediat** ce e găsită și nu se stochează nimic:

- **Timp:** $O(n \cdot n!)$ — $n!$ soluții, fiecare afișată în $O(n)$;
- **Memorie suplimentară:** $O(n)$ — vectorii `sol`, `used` și stiva recursivă de adâncime $n$.

---

## 3. De ce $n \le 10$?

| $n$ | $n!$ linii | volum de text |
|---|---|---|
| 5 | 120 | < 3 KB |
| 8 | 40 320 | ~1.3 MB |
| 10 | 3 628 800 | ~150 MB |
| 12 | 479 001 600 | ~23 GB |
| 15 | $1.3 \cdot 10^{12}$ | imposibil practic |

Programul limitează $n$ la 10, ultima valoare pentru care afișarea completă mai are sens.

---

## 4. Exemplu de rulare

```
n (1..10) = 3
Introduceți cele 3 elemente ale mulțimii A:
a1 = 5
a2 = -2
a3 = 7

Permutările mulțimii A = {5, -2, 7}:
1. (5, -2, 7)
2. (5, 7, -2)
3. (-2, 5, 7)
4. (-2, 7, 5)
5. (7, 5, -2)
6. (7, -2, 5)
Total: 6 permutări (3! = 6)
```

Ordinea urmează ordinea în care au fost introduse elementele (lexicografică după indici), nu valoarea lor numerică.
