// Problema 2: pentru A = {a1, a2, a3, a4} (citite de la tastatură) se afișează
// toate permutările, toate combinările și toate aranjamentele de m = 3 elemente.
//
// Generarea se face prin backtracking pe vectori:
//   sol[]  - vectorul soluției curente (indici în A);
//   used[] - vector de marcaje: used[i] == true dacă A[i] e deja în soluție.

#include <iostream>
#include <limits>
#include <string>
#include <vector>
#include <cstdlib>

using Solutions = std::vector<std::vector<int>>;

const int N = 4;
const int M = 3;

int readInt(const std::string& prompt) {
    int value;
    while (true) {
        std::cout << prompt;
        if (std::cin >> value) return value;
        if (std::cin.eof()) { std::cout << "\nIntrare încheiată.\n"; std::exit(1); }
        std::cout << "  Introduceți un număr întreg.\n";
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
}

// Citește n numere întregi distincte (o mulțime nu are elemente repetate).
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

// ---------- aranjamente (pentru k == n: permutări) ----------

void backAranj(const std::vector<int>& a, int k, int pos,
               std::vector<int>& sol, std::vector<bool>& used, Solutions& result) {
    if (pos == k) {
        std::vector<int> item;
        for (int i : sol) item.push_back(a[i]);
        result.push_back(item);
        return;
    }
    for (int i = 0; i < (int)a.size(); ++i) {
        if (!used[i]) {
            used[i] = true;
            sol[pos] = i;
            backAranj(a, k, pos + 1, sol, used, result);
            used[i] = false;
        }
    }
}

Solutions aranjamente(const std::vector<int>& a, int k) {
    std::vector<int> sol(k);
    std::vector<bool> used(a.size(), false);
    Solutions result;
    backAranj(a, k, 0, sol, used, result);
    return result;
}

// ---------- combinări ----------
// Indicii se aleg strict crescător, deci fiecare submulțime apare o singură dată.

void backComb(const std::vector<int>& a, int k, int pos, int start,
              std::vector<int>& sol, Solutions& result) {
    if (pos == k) {
        std::vector<int> item;
        for (int i : sol) item.push_back(a[i]);
        result.push_back(item);
        return;
    }
    int n = (int)a.size();
    // rămân k - pos poziții de completat, deci i nu poate depăși n - (k - pos)
    for (int i = start; i <= n - (k - pos); ++i) {
        sol[pos] = i;
        backComb(a, k, pos + 1, i + 1, sol, result);
    }
}

Solutions combinari(const std::vector<int>& a, int k) {
    std::vector<int> sol(k);
    Solutions result;
    backComb(a, k, 0, 0, sol, result);
    return result;
}

// ---------- afișare ----------

void show(const std::string& title, const Solutions& items) {
    std::cout << "\n" << title << " — " << items.size() << " în total:\n";
    size_t width = std::to_string(items.size()).size();
    int idx = 0;
    for (const auto& item : items) {
        std::string num = std::to_string(++idx);
        std::cout << "  " << std::string(width - num.size(), ' ') << num << ". (";
        for (size_t j = 0; j < item.size(); ++j)
            std::cout << (j ? ", " : "") << item[j];
        std::cout << ")\n";
    }
}

int main() {
    std::cout << "Introduceți cele " << N << " elemente ale mulțimii A:\n";
    std::vector<int> a = readSet(N);

    std::cout << "\nA = {";
    for (int i = 0; i < N; ++i) std::cout << (i ? ", " : "") << a[i];
    std::cout << "}\n";

    show("Permutări ale lui A", aranjamente(a, N));
    show("Combinări de " + std::to_string(M) + " elemente", combinari(a, M));
    show("Aranjamente de " + std::to_string(M) + " elemente", aranjamente(a, M));
    return 0;
}
