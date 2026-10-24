// Problema 3 (b): toate modurile de a așeza n ture pe o tablă n x n
// astfel încât oricare două să nu se atace.
//
// Pe fiecare linie i se pune exact o tură, în coloana c[i]. Două ture se atacă
// doar dacă sunt pe aceeași linie (imposibil prin construcție) sau pe aceeași
// coloană, deci c[1..n] trebuie să conțină coloane distincte: soluțiile sunt
// exact permutările mulțimii {1, ..., n}, iar numărul lor este n!.
//
// Backtracking: colUsed[j] == true dacă pe coloana j se află deja o tură.

#include <iostream>
#include <limits>
#include <string>
#include <cstdlib>

const int MAX_N = 20;
const int CONFIRM_FROM = 9;  // 9! = 362 880 soluții — cerem confirmare înainte de afișare

int n;
int c[MAX_N + 1];            // c[i] = coloana turei de pe linia i (indexare de la 1)
bool colUsed[MAX_N + 1];

int readInt(const std::string& prompt, int lo, int hi) {
    int value;
    while (true) {
        std::cout << prompt;
        if (std::cin >> value) {
            if (value >= lo && value <= hi) return value;
            std::cout << "  Valoarea trebuie să fie în intervalul [" << lo << ", " << hi << "].\n";
        } else {
            if (std::cin.eof()) { std::cout << "\nIntrare încheiată.\n"; std::exit(1); }
            std::cout << "  Introduceți un număr întreg.\n";
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        }
    }
}

void back(int i) {
    if (i > n) {
        for (int k = 1; k <= n; ++k) std::cout << c[k] << (k < n ? ',' : '\n');
        return;
    }
    for (int j = 1; j <= n; ++j) {
        if (!colUsed[j]) {          // coloana j e liberă => tura (i, j) nu e atacată
            colUsed[j] = true;
            c[i] = j;
            back(i + 1);
            colUsed[j] = false;
        }
    }
}

int main() {
    std::ios::sync_with_stdio(false);  // afișare rapidă (cin rămâne legat de cout)

    n = readInt("n (1.." + std::to_string(MAX_N) + ") = ", 1, MAX_N);

    unsigned long long total = 1;
    for (int i = 2; i <= n; ++i) total *= i;
    std::cout << "Număr de soluții: " << n << "! = " << total << "\n";

    if (n >= CONFIRM_FROM) {
        std::string answer;
        std::cout << "Sunt foarte multe soluții. Le afișăm pe toate? (d/n) ";
        if (!(std::cin >> answer) || (answer != "d" && answer != "da" && answer != "y" && answer != "yes"))
            return 0;
    }

    std::cout << "\n";
    back(1);
    return 0;
}
