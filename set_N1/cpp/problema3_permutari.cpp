// Problema 3 (a): toate permutările mulțimii A = {a1, ..., an},
// n și elementele citite de la tastatură.
//
// Backtracking pe vectori: sol[] este permutarea curentă (indici în A),
// used[] marchează elementele deja folosite.

#include <iostream>
#include <limits>
#include <string>
#include <vector>
#include <cstdlib>

const int MAX_N = 10;  // 10! = 3 628 800 linii; peste atât afișarea devine nerealistă

int readInt(const std::string& prompt, int lo = std::numeric_limits<int>::min(),
            int hi = std::numeric_limits<int>::max()) {
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

std::vector<int> readSet(int n) {
    std::vector<int> a;
    while ((int)a.size() < n) {
        int x = readInt("a" + std::to_string(a.size() + 1) + " = ");
        bool exists = false;
        for (int v : a) if (v == x) exists = true;
        if (exists) {
            std::cout << "  Elementul există deja în mulțime, introduceți altul.\n";
            continue;
        }
        a.push_back(x);
    }
    return a;
}

int n;
std::vector<int> a, sol;
std::vector<bool> used;
long long countSol = 0;

void back(int pos) {
    if (pos == n) {
        std::cout << ++countSol << ". (";
        for (int i = 0; i < n; ++i) std::cout << (i ? ", " : "") << a[sol[i]];
        std::cout << ")\n";
        return;
    }
    for (int i = 0; i < n; ++i) {
        if (!used[i]) {
            used[i] = true;
            sol[pos] = i;
            back(pos + 1);
            used[i] = false;
        }
    }
}

int main() {
    std::ios::sync_with_stdio(false);  // afișare rapidă (cin rămâne legat de cout)

    n = readInt("n (1.." + std::to_string(MAX_N) + ") = ", 1, MAX_N);
    std::cout << "Introduceți cele " << n << " elemente ale mulțimii A:\n";
    a = readSet(n);
    sol.assign(n, 0);
    used.assign(n, false);

    std::cout << "\nPermutările mulțimii A = {";
    for (int i = 0; i < n; ++i) std::cout << (i ? ", " : "") << a[i];
    std::cout << "}:\n";

    back(0);
    std::cout << "Total: " << countSol << " permutări (" << n << "! = " << countSol << ")\n";
    return 0;
}
