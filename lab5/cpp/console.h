// Ввод с клавиатуры с контролем ошибок. Всё читается построчно (std::getline),
// поэтому некорректный ввод не «ломает» поток и не оставляет мусор в буфере.

#pragma once

#include <cstdlib>
#include <iostream>
#include <string>

#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#endif

// В консоли Windows включает UTF-8, чтобы кириллица выводилась корректно.
inline void setupConsole() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
#endif
}

inline std::string trim(const std::string& s) {
    const char* ws = " \t\r\n";
    size_t b = s.find_first_not_of(ws);
    if (b == std::string::npos) return "";
    size_t e = s.find_last_not_of(ws);
    return s.substr(b, e - b + 1);
}

// Читает строку; при конце ввода (Ctrl+D / Ctrl+Z) завершает программу.
inline std::string readLine(const std::string& prompt) {
    std::cout << prompt;
    std::string line;
    if (!std::getline(std::cin, line)) {
        std::cout << "\nВвод завершён.\n";
        std::exit(0);
    }
    return trim(line);
}

inline std::string readNonEmpty(const std::string& prompt) {
    while (true) {
        std::string s = readLine(prompt);
        if (!s.empty()) return s;
        std::cout << "  Строка не должна быть пустой.\n";
    }
}

// Пытается разобрать целое число; вся строка должна быть числом.
inline bool parseInt(const std::string& s, long long& value) {
    if (s.empty()) return false;
    size_t pos = 0;
    try {
        value = std::stoll(s, &pos);
    } catch (...) {
        return false;
    }
    return pos == s.size();
}

inline int readInt(const std::string& prompt, int lo, int hi) {
    while (true) {
        long long v;
        if (!parseInt(readLine(prompt), v)) {
            std::cout << "  Введите целое число.\n";
        } else if (v < lo || v > hi) {
            std::cout << "  Число должно быть в диапазоне [" << lo << ", " << hi << "].\n";
        } else {
            return (int)v;
        }
    }
}

// Принимает: да / д / yes / y  и  нет / н / no / n  (в любом регистре для латиницы).
inline bool readYesNo(const std::string& prompt) {
    while (true) {
        std::string s = readLine(prompt);
        for (char& c : s) c = (char)std::tolower((unsigned char)c);
        if (s == "да" || s == "Да" || s == "ДА" || s == "д" || s == "Д" || s == "yes" || s == "y")
            return true;
        if (s == "нет" || s == "Нет" || s == "НЕТ" || s == "н" || s == "Н" || s == "no" || s == "n")
            return false;
        std::cout << "  Ответьте «да» или «нет».\n";
    }
}

// Ширина строки UTF-8 в символах (байты продолжения 10xxxxxx не считаются).
inline size_t displayWidth(const std::string& s) {
    size_t w = 0;
    for (unsigned char c : s)
        if ((c & 0xC0) != 0x80) ++w;
    return w;
}

// Дополняет строку пробелами до ширины width (std::setw считает байты, а не символы).
inline std::string padRight(const std::string& s, size_t width) {
    size_t w = displayWidth(s);
    return w >= width ? s : s + std::string(width - w, ' ');
}

inline std::string padLeft(const std::string& s, size_t width) {
    size_t w = displayWidth(s);
    return w >= width ? s : std::string(width - w, ' ') + s;
}
