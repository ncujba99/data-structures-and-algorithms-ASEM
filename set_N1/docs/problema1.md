# Problema 1 — Numărul de permutări, combinări și aranjamente

> Cod: [`python/problema1.py`](../python/problema1.py) · [`cpp/problema1.cpp`](../cpp/problema1.cpp) · [← înapoi la index](../README.md)

**Enunț.** Se citesc de la tastatură numerele naturale $n$ ($n \le 20$) și $m$ ($m \le n$). Se cere numărul de **permutări** ale unei mulțimi cu $n$ elemente, numărul de **combinări** de $m$ elemente și numărul de **aranjamente** de $m$ elemente.

Aici doar **numărăm**. Generarea efectivă este tema problemelor [2](problema2.md) și [3](problema3a_permutari.md).

---

## 1. Matematica

### 1.1 Cadrul

Fie $A$ o mulțime finită cu $|A| = n$ elemente **distincte**, de exemplu $A = \{1, 2, 3, 4\}$. Toate cele trei noțiuni răspund la întrebarea *„în câte moduri putem alege și/sau ordona elemente din $A$?”*. Ele diferă prin două criterii:

| Noțiune | Câte elemente se iau | Contează ordinea? | Exemplu pentru $A=\{1,2,3,4\}$, $m=3$ |
|---|:-:|:-:|---|
| **Permutare** | toate $n$ | da | $(3,1,4,2)$ |
| **Aranjament** | $m$ din $n$ | **da** | $(3,1,4) \ne (1,3,4)$ |
| **Combinare** | $m$ din $n$ | **nu** | $\{1,3,4\} = \{3,1,4\}$ |

```
                  ┌────────────────────────────┐
                  │ Iau toate cele n elemente? │
                  └─────┬────────────────┬─────┘
                        │ da             │ nu, doar m
                        ▼                ▼
            ╔═══════════════════════╗ ┌────────────────────┐
            ║       PERMUTARE       ║ │ Contează ordinea?  │
            ║       P(n) = n!       ║ └────┬──────────┬────┘
            ╚═══════════════════════╝      │ da       │ nu
                                           ▼          ▼
                          ╔════════════════════╗  ╔═════════════════════════╗
                          ║     ARANJAMENT     ║  ║        COMBINARE        ║
                          ║ A(n,m) = n!/(n−m)! ║  ║ C(n,m) = n!/(m!(n−m)!)  ║
                          ╚════════════════════╝  ╚═════════════════════════╝
```

### 1.2 Principiul multiplicării (regula produsului)

Toate formulele se deduc din această regulă:

> Dacă o alegere se face în $k$ etape succesive și la etapa $j$ există $x_j$ variante, **indiferent** de ce s-a ales la etapele anterioare, atunci numărul total de alegeri este
> $$x_1 \cdot x_2 \cdot \ldots \cdot x_k.$$

### 1.3 Permutări

**Definiție.** O *permutare* a lui $A$ este o așezare a tuturor celor $n$ elemente într-o ordine anume. Formal, este o funcție bijectivă $\sigma : \{1, \ldots, n\} \to A$.

**Formula.** Completăm pe rând pozițiile $1, 2, \ldots, n$: pe prima poziție avem $n$ variante, pe a doua $n-1$ (un element e deja folosit) și așa mai departe:

```
┌──────────┬───┬───────┬───────┬───┬───┐
│ poziția  │ 1 │   2   │   3   │ … │ n │
├──────────┼───┼───────┼───────┼───┼───┤
│ variante │ n │ n − 1 │ n − 2 │ … │ 1 │
└──────────┴───┴───────┴───────┴───┴───┘
          produs:  n · (n − 1) · (n − 2) · … · 1 = n!
```

$$\boxed{P(n) = n \cdot (n-1) \cdot \ldots \cdot 2 \cdot 1 = n!}$$

**Proprietăți:**

$$0! = 1 \qquad\text{(o singură așezare a mulțimii vide)}$$

$$n! = n \cdot (n-1)! \qquad\text{(relația de recurență)}$$

### 1.4 Aranjamente

**Definiție.** Un *aranjament* de $n$ luate câte $m$ este un șir ordonat de $m$ elemente **distincte** din $A$. Formal, este o funcție injectivă $f : \{1, \ldots, m\} \to A$.

**Formula.** Același raționament, dar ne oprim după $m$ poziții:

```
┌──────────┬───┬───────┬───┬───────────┐
│ poziția  │ 1 │   2   │ … │     m     │
├──────────┼───┼───────┼───┼───────────┤
│ variante │ n │ n − 1 │ … │ n − m + 1 │
└──────────┴───┴───────┴───┴───────────┘
          produs:  n · (n − 1) · … · (n − m + 1) = n! / (n − m)!
```

$$\boxed{A(n, m) = n \cdot (n-1) \cdot \ldots \cdot (n-m+1) = \frac{n!}{(n-m)!}}$$

Produsul are exact $m$ factori, „ultimii $m$” din $n!$.

**Proprietăți:**

$$A(n, 0) = 1, \qquad A(n, 1) = n, \qquad A(n, n) = A(n, n-1) = n! = P(n)$$

$$A(n, m) = n \cdot A(n-1, m-1) \qquad\text{(recurență)}$$

### 1.5 Combinări

**Definiție.** O *combinare* de $n$ luate câte $m$ este o **submulțime** de $m$ elemente a lui $A$. Ordinea nu contează.

**Formula.** Fiecare submulțime de $m$ elemente poate fi ordonată în $m!$ feluri, iar fiecare ordonare este un aranjament diferit. Deci fiecare combinare corespunde exact la $m!$ aranjamente:

$$A(n, m) = C(n, m) \cdot m!$$

$$\boxed{C(n, m) = \frac{A(n,m)}{m!} = \frac{n!}{m!\,(n-m)!}}$$

Pentru $A=\{1,2,3,4\}$ și $m=3$: $\;C(4,3)\cdot 3! = 4 \cdot 6 = 24 = A(4,3)$.

```
                        ┌────────────────────┐
                        │ combinarea {1,2,3} │
                        └──────────┬─────────┘
     ┌───────────┬───────────┬─────┴─────┬───────────┬───────────┐
     ▼           ▼           ▼           ▼           ▼           ▼
╭─────────╮ ╭─────────╮ ╭─────────╮ ╭─────────╮ ╭─────────╮ ╭─────────╮
│ (1,2,3) │ │ (1,3,2) │ │ (2,1,3) │ │ (2,3,1) │ │ (3,1,2) │ │ (3,2,1) │
╰─────────╯ ╰─────────╯ ╰─────────╯ ╰─────────╯ ╰─────────╯ ╰─────────╯
```

**Proprietăți:**

| Proprietate | Formula | Semnificație |
|---|---|---|
| Cazuri limită | $C(n,0) = C(n,n) = 1$ | mulțimea vidă / toată mulțimea |
| Simetrie | $C(n,m) = C(n, n-m)$ | a alege $m$ elemente = a alege cele $n-m$ lăsate deoparte |
| Formula lui Pascal | $C(n,m) = C(n-1,m-1) + C(n-1,m)$ | un element fixat este sau nu este în submulțime |
| Suma pe rând | $\sum_{k=0}^{n} C(n,k) = 2^n$ | numărul tuturor submulțimilor |
| Forma multiplicativă | $C(n,m) = \dfrac{n}{m}\, C(n-1, m-1)$ | stă la baza algoritmului din program |

**Triunghiul lui Pascal.** Fiecare număr este suma celor două de deasupra lui (formula lui Pascal):

```
n = 0                    1
n = 1                  1   1
n = 2                1   2   1
n = 3              1   3   3   1
n = 4            1   4   6   4   1          ← C(4,0..4); suma = 16 = 2⁴
n = 5          1   5  10  10   5   1        ← C(5,3) = 10
n = 6        1   6  15  20  15   6   1
```

Valoarea maximă de pe rândul $n$ este la mijloc: $C(n, \lfloor n/2 \rfloor)$. Pentru $n = 20$ aceasta este $C(20,10) = 184\,756$.

### 1.6 Tabel de control pentru $n = 4$

| $m$ | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| $C(4, m)$ | 1 | 4 | 6 | 4 | 1 |
| $A(4, m)$ | 1 | 4 | 12 | 24 | 24 |
| $A(4,m) / C(4,m) = m!$ | 1 | 1 | 2 | 6 | 24 |

---

## 2. Algoritmii

| Funcție | Ce calculează | Nr. de înmulțiri |
|---|---|---|
| `permutari(n)` | $1 \cdot 2 \cdot \ldots \cdot n$ | $n - 1$ |
| `aranjamente(n, m)` | $(n-m+1) \cdot \ldots \cdot n$ — doar ultimii $m$ factori | $m$ |
| `combinari(n, m)` | iterativ, vezi mai jos | $\min(m, n-m)$ |

Toți algoritmii sunt **liniari**: $O(n)$ timp și $O(1)$ memorie.

### 2.1 De ce nu calculăm direct $\dfrac{n!}{m!(n-m)!}$?

Formula e corectă, dar face calcule inutile (trei factoriale) și, pentru $n$ mai mare, $n!$ depășește tipul de date chiar dacă rezultatul final e mic. De exemplu, $C(25, 2) = 300$, dar $25! \approx 1.55 \cdot 10^{25}$ nu încape în 64 de biți.

### 2.2 Calculul iterativ al combinărilor

```
k = min(m, n - m)              // simetria: C(n, m) = C(n, n - m) → mai puțini pași
r = 1
pentru i = 1..k:
    r = r * (n - k + i) / i
```

**De ce împărțirea e întotdeauna exactă?** Notăm cu $r_i$ valoarea lui `r` după pasul $i$. Prin inducție:

$$r_0 = 1 = C(n-k, 0)$$

$$r_i = r_{i-1} \cdot \frac{n-k+i}{i} = C(n-k+i-1,\, i-1) \cdot \frac{n-k+i}{i} = C(n-k+i,\, i)$$

(ultima egalitate este forma multiplicativă din tabelul de proprietăți). Deci după fiecare pas $r_i$ este un coeficient binomial, adică un **număr întreg**, iar la final $r_k = C(n, k) = C(n, m)$. Înmulțim **înainte** de a împărți, deci nu apar fracții.

**Exemplu: $C(5, 3)$**, unde $k = \min(3, 2) = 2$:

| $i$ | $r_{i-1} \cdot (n-k+i) \;/\; i$ | $r_i$ |
|---|---|---|
| 1 | $1 \cdot 4 \,/\, 1$ | $4 = C(4,1)$ |
| 2 | $4 \cdot 5 \,/\, 2$ | $\mathbf{10} = C(5,2) = C(5,3)$ |

---

## 3. De ce limita $n \le 20$?

În C++ rezultatele sunt de tip `unsigned long long` (64 biți), cu maximul $2^{64} - 1 \approx 1.84 \cdot 10^{19}$:

$$20! = 2\,432\,902\,008\,176\,640\,000 \approx 2.43 \cdot 10^{18} \quad \checkmark \text{ încape}$$

$$21! = 51\,090\,942\,171\,709\,440\,000 \approx 5.11 \cdot 10^{19} \quad \times \text{ depășire (overflow)}$$

Deci $n \le 20$ este exact limita până la care $P(n)$ încape în 64 de biți. Cum $A(n,m) \le n!$ și $C(n,m) \le A(n,m)$, încap și celelalte. Valorile intermediare din calculul combinărilor sunt cel mult $C(19,9) \cdot 20 = 1\,847\,560$, deci nu e niciun risc. În Python întregii nu au limită, dar respectăm același enunț.

---

## 4. Exemplu de rulare

```
n (1..20) = 5
m (0..5) = 3

Permutări:    P(5) = 5! = 120
Combinări:    C(5, 3) = 10
Aranjamente:  A(5, 3) = 60
```

Cazul extrem:

```
n (1..20) = 20
m (0..20) = 10

Permutări:    P(20) = 20! = 2432902008176640000
Combinări:    C(20, 10) = 184756
Aranjamente:  A(20, 10) = 670442572800
```

Programul recitește valoarea dacă nu este un număr întreg sau dacă iese din interval ($1 \le n \le 20$, $0 \le m \le n$).
