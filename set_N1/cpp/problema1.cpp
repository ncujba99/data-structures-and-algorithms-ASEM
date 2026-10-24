// Problema 1: numărul de permutări, combinări și aranjamente.
//
//   P(n)    = n!
//   C(n, m) = n! / (m! * (n - m)!)
//   A(n, m) = n! / (n - m)!
//
// Pentru n <= 20 toate valorile încap în unsigned long long (20! ≈ 2.43e18 < 1.8e19).

#include <iostream>
#include <limits>
#include <string>
#include <cstdlib>

using u64 = unsigned long long;

int readInt(const char* prompt, int lo, int hi) {
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

// P(n) = 1 * 2 * ... * n
u64 permutari(int n) {
    u64 result = 1;
    for (int i = 2; i <= n; ++i) result *= i;
    return result;
}

// A(n, m) = (n - m + 1) * ... * n  (produsul ultimelor m numere)
u64 aranjamente(int n, int m) {
    u64 result = 1;
    for (int i = n - m + 1; i <= n; ++i) result *= i;
    return result;
}

// C(n, m) calculat iterativ: după pasul i rezultatul este C(n-k+i, i), deci
// împărțirea este mereu exactă și nu se calculează factoriale uriașe.
u64 combinari(int n, int m) {
    int k = (m < n - m) ? m : n - m;  // C(n, m) = C(n, n - m)
    u64 result = 1;
    for (int i = 1; i <= k; ++i) result = result * (n - k + i) / i;
    return result;
}

int main() {
    int n = readInt("n (1..20) = ", 1, 20);
    std::string promptM = "m (0.." + std::to_string(n) + ") = ";
    int m = readInt(promptM.c_str(), 0, n);

    std::cout << "\n"
              << "Permutări:    P(" << n << ") = " << n << "! = " << permutari(n) << "\n"
              << "Combinări:    C(" << n << ", " << m << ") = " << combinari(n, m) << "\n"
              << "Aranjamente:  A(" << n << ", " << m << ") = " << aranjamente(n, m) << "\n";
    return 0;
}
