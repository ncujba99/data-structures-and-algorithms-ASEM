// Задание 1 (Вариант 10): информационная система железнодорожного вокзала
// на основе бинарного поискового дерева.
//
// Для каждого поезда хранятся: номер поезда, станция назначения, время отправления.
// КЛЮЧЕВОЕ ПОЛЕ - номер поезда: по нему упорядочено дерево и выполняется поиск.

#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "binary_tree.h"
#include "console.h"

const int MAX_TRAIN_NUMBER = 9999;

struct Train {
    int number = 0;            // ключевое поле
    std::string destination;   // станция назначения
    int departure = 0;         // время отправления, минуты от полуночи
};

// Порядок в дереве определяется только ключевым полем.
bool operator<(const Train& a, const Train& b) { return a.number < b.number; }

// «Образец» для поиска / удаления: заполнено только ключевое поле.
Train byNumber(int number) {
    Train t;
    t.number = number;
    return t;
}

std::string formatTime(int minutes) {
    std::ostringstream out;
    out << std::setw(2) << std::setfill('0') << minutes / 60 << ':'
        << std::setw(2) << std::setfill('0') << minutes % 60;
    return out.str();
}

// Разбирает время в формате ЧЧ:ММ (или Ч:ММ).
bool parseTime(const std::string& s, int& minutes) {
    size_t colon = s.find(':');
    if (colon == std::string::npos) return false;
    long long h, m;
    std::string hs = s.substr(0, colon), ms = s.substr(colon + 1);
    if (hs.empty() || hs.size() > 2 || ms.size() != 2) return false;
    if (!parseInt(hs, h) || !parseInt(ms, m)) return false;
    if (hs[0] == '-' || ms[0] == '-' || h > 23 || m > 59) return false;
    minutes = (int)(h * 60 + m);
    return true;
}

int readTime(const std::string& prompt) {
    while (true) {
        int minutes;
        if (parseTime(readLine(prompt), minutes)) return minutes;
        std::cout << "  Введите время в формате ЧЧ:ММ (00:00 - 23:59).\n";
    }
}

// ---------- вывод ----------

void printHeader() {
    std::cout << "  Номер | Станция назначения       | Отправление\n"
              << "  ------+--------------------------+------------\n";
}

void printRow(const Train& t) {
    std::cout << "  " << padLeft(std::to_string(t.number), 5) << " | "
              << padRight(t.destination, 24) << " | " << formatTime(t.departure) << "\n";
}

// ---------- пункты меню ----------

void addTrains(BinaryTree<Train>& tree) {
    int count = readInt("Сколько поездов добавить? (1..100): ", 1, 100);
    for (int i = 1; i <= count; ++i) {
        std::cout << "\nПоезд " << i << " из " << count << ":\n";
        Train t;
        while (true) {
            t.number = readInt("  номер поезда (1.." + std::to_string(MAX_TRAIN_NUMBER) + "): ",
                               1, MAX_TRAIN_NUMBER);
            if (tree.retrieveItem(t) == nullptr) break;
            std::cout << "  Поезд с таким номером уже есть, номер - ключевое поле и должен быть уникален.\n";
        }
        t.destination = readNonEmpty("  станция назначения: ");
        t.departure = readTime("  время отправления (ЧЧ:ММ): ");
        tree.insertItem(t);
    }
    std::cout << "\nДобавлено поездов: " << count << ". Всего в системе: " << tree.nodeCount() << ".\n";
}

void printAll(const BinaryTree<Train>& tree) {
    if (tree.isEmpty()) {
        std::cout << "Список поездов пуст.\n";
        return;
    }
    std::cout << "Все поезда (симметричный обход - по возрастанию номера):\n";
    printHeader();
    tree.inorderTree(printRow);
    std::cout << "Всего: " << tree.nodeCount() << "\n";
}

void findByNumber(const BinaryTree<Train>& tree) {
    int number = readInt("Номер поезда: ", 1, MAX_TRAIN_NUMBER);
    const Train* t = tree.retrieveItem(byNumber(number));
    if (t == nullptr) {
        std::cout << "Поезд № " << number << " не найден.\n";
        return;
    }
    printHeader();
    printRow(*t);
}

void findByDestination(const BinaryTree<Train>& tree) {
    std::string station = readNonEmpty("Станция назначения: ");
    // Станция не является ключом, поэтому нужен полный обход дерева.
    std::vector<Train> found;
    tree.inorderTree([&](const Train& t) {
        if (t.destination == station) found.push_back(t);
    });
    if (found.empty()) {
        std::cout << "Поездов до станции «" << station << "» нет.\n";
        return;
    }
    std::cout << "Поезда до станции «" << station << "»:\n";
    printHeader();
    for (const Train& t : found) printRow(t);
}

void deleteTrain(BinaryTree<Train>& tree, BinaryTree<Train>& backup, bool& hasBackup) {
    int number = readInt("Номер удаляемого поезда: ", 1, MAX_TRAIN_NUMBER);
    if (tree.retrieveItem(byNumber(number)) == nullptr) {
        std::cout << "Поезд № " << number << " не найден.\n";
        return;
    }
    backup = tree;               // копия дерева (operator=) для отмены удаления
    hasBackup = true;
    tree.deleteItem(byNumber(number));
    std::cout << "Поезд № " << number << " удалён. (Пункт 7 - отменить удаление.)\n";
}

void undoDelete(BinaryTree<Train>& tree, BinaryTree<Train>& backup, bool& hasBackup) {
    if (!hasBackup) {
        std::cout << "Нет удаления, которое можно отменить.\n";
        return;
    }
    tree = backup;
    hasBackup = false;
    std::cout << "Последнее удаление отменено.\n";
}

void showStructure(const BinaryTree<Train>& tree) {
    if (tree.isEmpty()) {
        std::cout << "Дерево пусто.\n";
        return;
    }
    std::cout << "Структура дерева (ключ - номер поезда; Л - левое, П - правое поддерево):\n\n";
    tree.print(std::cout, [](const Train& t) {
        return std::to_string(t.number) + "  (" + t.destination + ")";
    });

    auto printKey = [](const Train& t) { std::cout << ' ' << t.number; };
    std::cout << "\n" << padRight("Симметричный обход (inorder):", 38);
    tree.inorderTree(printKey);
    std::cout << "\n" << padRight("Обход в прямом порядке (preorder):", 38);
    tree.preorderTree(printKey);
    std::cout << "\n" << padRight("Обход в обратном порядке (postorder):", 38);
    tree.postorderTree(printKey);
    std::cout << "\n\nУзлов: " << tree.nodeCount() << ", уровней (высота): " << tree.height() << "\n";
}

void loadDemo(BinaryTree<Train>& tree) {
    const Train demo[] = {
        {50, "Москва", 8 * 60 + 15},     {30, "Бухарест", 21 * 60 + 40},
        {70, "Одесса", 6 * 60 + 5},      {20, "Яссы", 13 * 60},
        {40, "Киев", 17 * 60 + 30},      {60, "Москва", 22 * 60 + 50},
        {80, "Унгены", 10 * 60 + 20},    {35, "Бухарест", 9 * 60 + 45},
        {65, "Одесса", 15 * 60 + 10},
    };
    int added = 0;
    for (const Train& t : demo)
        if (tree.insertItem(t)) ++added;
    std::cout << "Загружено демонстрационных поездов: " << added
              << " (уже существующие номера пропущены).\n";
}

int main() {
    setupConsole();
    BinaryTree<Train> tree, backup;
    bool hasBackup = false;

    while (true) {
        std::cout << "\n=== Вокзал: поезда дальнего следования (бинарное дерево) ===\n"
                  << "1. Ввести данные о поездах\n"
                  << "2. Вывести все поезда\n"
                  << "3. Найти поезд по номеру\n"
                  << "4. Найти поезда по станции назначения\n"
                  << "5. Удалить поезд\n"
                  << "6. Показать структуру дерева и обходы\n"
                  << "7. Отменить последнее удаление\n"
                  << "8. Загрузить демонстрационные данные\n"
                  << "9. Очистить все данные\n"
                  << "0. Выход\n";
        int choice = readInt("Ваш выбор: ", 0, 9);
        std::cout << "\n";
        switch (choice) {
            case 1: addTrains(tree); break;
            case 2: printAll(tree); break;
            case 3: findByNumber(tree); break;
            case 4: findByDestination(tree); break;
            case 5: deleteTrain(tree, backup, hasBackup); break;
            case 6: showStructure(tree); break;
            case 7: undoDelete(tree, backup, hasBackup); break;
            case 8: loadDemo(tree); break;
            case 9:
                tree.destroy();
                hasBackup = false;
                std::cout << "Все данные удалены.\n";
                break;
            case 0: return 0;
        }
    }
}
