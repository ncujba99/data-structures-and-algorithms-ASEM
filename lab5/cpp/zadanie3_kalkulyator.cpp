// Задание 3: калькулятор арифметических выражений в постфиксной форме
// на основе бинарного дерева (дерева выражения).
//
//   лист            - операнд (число);
//   внутренний узел - бинарная операция + - * /, у него ровно 2 ребёнка.
//
// Построение: постфиксная запись читается слева направо со стеком поддеревьев.
// Вычисление: обход в обратном порядке (postorder) - сначала оба операнда, потом операция.
// Дополнительно: ввод в обычной (инфиксной) форме со скобками, которая переводится
// в постфиксную алгоритмом сортировочной станции (shunting-yard).

#include <cctype>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "binary_tree.h"
#include "console.h"

struct Token {
    bool isOp;
    char op;        // '+', '-', '*', '/'  (если isOp)
    double value;   // число               (если !isOp)
};

using ENode = Node<Token>;

const std::string BOOK_EXAMPLE = "3 1 + 3 * 9 5 - 2 + / 3 7 4 - * 6 + -";

bool isOperator(const std::string& s) {
    return s == "+" || s == "-" || s == "*" || s == "/";
}

int precedence(char op) { return (op == '+' || op == '-') ? 1 : 2; }

std::string formatNumber(double x) {
    std::ostringstream out;
    out << std::setprecision(10) << x;
    return out.str();
}

// Отрицательное число внутри выражения берётся в скобки: 2 - (-1), а не 2 - -1.
std::string operand(double x) {
    return x < 0 ? "(" + formatNumber(x) + ")" : formatNumber(x);
}

std::string label(const Token& t) {
    return t.isOp ? std::string(1, t.op) : formatNumber(t.value);
}

bool parseNumber(const std::string& s, double& value) {
    size_t pos = 0;
    try {
        value = std::stod(s, &pos);
    } catch (...) {
        return false;
    }
    return pos == s.size() && std::isfinite(value);
}

std::vector<std::string> splitBySpaces(const std::string& s) {
    std::istringstream in(s);
    std::vector<std::string> tokens;
    std::string t;
    while (in >> t) tokens.push_back(t);
    return tokens;
}

// ---------- построение дерева из постфиксной записи ----------
//
// число    -> новый лист кладётся в стек;
// операция -> из стека берутся правый, затем левый операнд, создаётся узел
//             с этими детьми, и он кладётся в стек.
// В конце в стеке должно остаться ровно одно дерево.

ENode* buildTree(const std::vector<std::string>& postfix) {
    std::vector<ENode*> stack;
    try {
        for (const std::string& s : postfix) {
            if (isOperator(s)) {
                if (stack.size() < 2)
                    throw std::runtime_error("операции «" + s + "» не хватает операндов");
                ENode* right = stack.back(); stack.pop_back();
                ENode* left = stack.back(); stack.pop_back();
                stack.push_back(new ENode({true, s[0], 0}, left, right));
            } else {
                double v;
                if (!parseNumber(s, v))
                    throw std::runtime_error("«" + s + "» - не число и не операция");
                stack.push_back(new ENode({false, 0, v}));
            }
        }
        if (stack.empty()) throw std::runtime_error("выражение пустое");
        if (stack.size() > 1)
            throw std::runtime_error("лишние операнды: в стеке осталось поддеревьев - " +
                                     std::to_string(stack.size()) + ", а должно быть 1");
    } catch (...) {
        for (ENode*& n : stack) clear(n);   // освобождаем уже построенные поддеревья
        throw;
    }
    return stack.back();
}

// ---------- перевод инфиксной записи в постфиксную (shunting-yard) ----------

std::vector<std::string> tokenizeInfix(const std::string& s) {
    std::vector<std::string> tokens;
    for (size_t i = 0; i < s.size();) {
        char c = s[i];
        if (std::isspace((unsigned char)c)) {
            ++i;
        } else if (std::isdigit((unsigned char)c) || c == '.') {
            size_t j = i;
            while (j < s.size() && (std::isdigit((unsigned char)s[j]) || s[j] == '.')) ++j;
            tokens.push_back(s.substr(i, j - i));
            i = j;
        } else if (std::string("+-*/()").find(c) != std::string::npos) {
            tokens.push_back(std::string(1, c));
            ++i;
        } else {
            throw std::runtime_error(std::string("недопустимый символ «") + c + "»");
        }
    }
    return tokens;
}

std::vector<std::string> infixToPostfix(const std::string& infix) {
    std::vector<std::string> output, ops;
    for (const std::string& t : tokenizeInfix(infix)) {
        if (t == "(") {
            ops.push_back(t);
        } else if (t == ")") {
            while (!ops.empty() && ops.back() != "(") {
                output.push_back(ops.back());
                ops.pop_back();
            }
            if (ops.empty()) throw std::runtime_error("лишняя закрывающая скобка");
            ops.pop_back();
        } else if (isOperator(t)) {
            // Все операции левоассоциативны: выталкиваем операции с приоритетом >= текущего.
            while (!ops.empty() && ops.back() != "(" &&
                   precedence(ops.back()[0]) >= precedence(t[0])) {
                output.push_back(ops.back());
                ops.pop_back();
            }
            ops.push_back(t);
        } else {
            output.push_back(t);
        }
    }
    while (!ops.empty()) {
        if (ops.back() == "(") throw std::runtime_error("не закрыта скобка");
        output.push_back(ops.back());
        ops.pop_back();
    }
    return output;
}

// ---------- обходы ----------

// Обратный порядок (postorder): левое поддерево, правое поддерево, узел.
// Каждый шаг вычисления записывается в steps.
double evaluate(const ENode* node, std::vector<std::string>& steps) {
    if (!node->info.isOp) return node->info.value;
    double a = evaluate(node->left, steps);
    double b = evaluate(node->right, steps);
    double r = 0;
    switch (node->info.op) {
        case '+': r = a + b; break;
        case '-': r = a - b; break;
        case '*': r = a * b; break;
        case '/':
            if (b == 0) throw std::runtime_error("деление на ноль: " + formatNumber(a) + " / 0");
            r = a / b;
            break;
    }
    steps.push_back(operand(a) + " " + node->info.op + " " + operand(b) +
                    " = " + formatNumber(r));
    return r;
}

// Прямой порядок (preorder): узел, левое поддерево, правое поддерево.
void preorder(const ENode* node, std::vector<std::string>& out) {
    if (node == nullptr) return;
    out.push_back(label(node->info));
    preorder(node->left, out);
    preorder(node->right, out);
}

void postorder(const ENode* node, std::vector<std::string>& out) {
    if (node == nullptr) return;
    postorder(node->left, out);
    postorder(node->right, out);
    out.push_back(label(node->info));
}

std::string join(const std::vector<std::string>& items) {
    std::string s;
    for (size_t i = 0; i < items.size(); ++i) s += (i ? " " : "") + items[i];
    return s;
}

// Симметричный обход (inorder) с минимальным числом скобок:
// скобки нужны, если операция ребёнка слабее операции родителя, или если справа
// стоит операция того же приоритета после '-' или '/' (a - (b - c) != a - b - c).
std::string toInfix(const ENode* node) {
    if (!node->info.isOp) return operand(node->info.value);
    int p = precedence(node->info.op);

    std::string left = toInfix(node->left);
    if (node->left->info.isOp && precedence(node->left->info.op) < p)
        left = "(" + left + ")";

    std::string right = toInfix(node->right);
    if (node->right->info.isOp) {
        int pr = precedence(node->right->info.op);
        if (pr < p || (pr == p && (node->info.op == '-' || node->info.op == '/')))
            right = "(" + right + ")";
    }
    return left + " " + node->info.op + " " + right;
}

// ---------- обработка одного выражения ----------

void process(const std::vector<std::string>& postfix) {
    ENode* root = nullptr;
    try {
        root = buildTree(postfix);
    } catch (const std::exception& e) {
        std::cout << "Ошибка в выражении: " << e.what() << ".\n";
        return;
    }

    std::vector<std::string> preItems, postItems;
    preorder(root, preItems);
    postorder(root, postItems);
    std::string pre = join(preItems), post = join(postItems);

    std::cout << "\nДерево выражения (Л - левый операнд, П - правый):\n\n";
    printTree(std::cout, root, label);
    std::cout << "\n" << padRight("Префиксная запись  (preorder):", 32) << pre << "\n"
              << padRight("Инфиксная запись   (inorder):", 32) << toInfix(root) << "\n"
              << padRight("Постфиксная запись (postorder):", 32) << post << "\n";

    std::vector<std::string> steps;
    try {
        double result = evaluate(root, steps);
        std::cout << "\nВычисление (обход в обратном порядке):\n";
        for (size_t i = 0; i < steps.size(); ++i)
            std::cout << "  " << padLeft(std::to_string(i + 1), 2) << ") " << steps[i] << "\n";
        std::cout << "\nРезультат: " << formatNumber(result) << "\n";
    } catch (const std::exception& e) {
        std::cout << "\nОшибка вычисления: " << e.what() << ".\n";
    }
    clear(root);
}

int main() {
    setupConsole();
    while (true) {
        std::cout << "\n=== Калькулятор: дерево выражения ===\n"
                  << "1. Ввести выражение в постфиксной форме (например: 3 4 + 2 *)\n"
                  << "2. Ввести выражение в обычной форме со скобками (например: (3 + 4) * 2)\n"
                  << "3. Пример из методички\n"
                  << "0. Выход\n";
        int choice = readInt("Ваш выбор: ", 0, 3);
        if (choice == 0) break;

        if (choice == 1) {
            std::string s = readNonEmpty("Постфиксное выражение (элементы через пробел): ");
            process(splitBySpaces(s));
        } else if (choice == 2) {
            std::string s = readNonEmpty("Выражение: ");
            try {
                std::vector<std::string> postfix = infixToPostfix(s);
                std::cout << "Постфиксная форма: " << join(postfix) << "\n";
                process(postfix);
            } catch (const std::exception& e) {
                std::cout << "Ошибка в выражении: " << e.what() << ".\n";
            }
        } else {
            std::cout << "\n((3 + 1) * 3) / ((9 - 5) + 2) - (3 * (7 - 4) + 6)\n"
                      << "Постфиксная форма: " << BOOK_EXAMPLE << "\n";
            process(splitBySpaces(BOOK_EXAMPLE));
        }
    }
    return 0;
}
