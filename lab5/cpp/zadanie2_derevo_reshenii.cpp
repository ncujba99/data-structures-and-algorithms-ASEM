// Задание 2: ДЕРЕВО РЕШЕНИЙ на основе бинарного дерева - выдача потребительского кредита.
//
//   внутренний узел - вопрос; левый ребёнок - ответ ДА, правый - ответ НЕТ;
//   лист            - решение.
// Каждый вопрос имеет ровно два ответа, поэтому дерево полное:
// у каждого узла либо 0, либо 2 ребёнка.

#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "binary_tree.h"
#include "console.h"

struct Step {
    std::string text;
    bool isDecision;
};

using DNode = Node<Step>;

// Вопрос с ветками ДА (yes) и НЕТ (no).
DNode* question(const std::string& text, DNode* yes, DNode* no) {
    return new DNode({text, false}, yes, no);
}

DNode* decision(const std::string& text) { return new DNode({text, true}); }

// Дерево решений: 6 уровней, 9 вопросов, 10 решений.
DNode* buildLoanTree() {
    return question(
        "Есть ли у вас постоянный официальный доход?",
        question(
            "Ваш ежемесячный доход больше 10 000 леев?",
            question(
                "Есть ли у вас сейчас просроченные кредиты?",
                decision("ОТКАЗ: сначала погасите текущую просроченную задолженность."),
                question(
                    "Запрашиваемая сумма меньше 12 ваших месячных доходов?",
                    decision("ОДОБРЕНО: кредит на стандартных условиях."),
                    question(
                        "Можете ли вы предоставить залог (недвижимость или автомобиль)?",
                        decision("ОДОБРЕНО: кредит под залог, сниженная процентная ставка."),
                        decision("ОДОБРЕНО ЧАСТИЧНО: сумма уменьшена до 12 месячных доходов.")))),
            question(
                "Есть ли у вас поручитель с официальным доходом?",
                question(
                    "Были ли все ваши прошлые кредиты погашены вовремя?",
                    decision("ОДОБРЕНО: кредит с поручителем."),
                    decision("ОТКАЗ: низкий доход и плохая кредитная история.")),
                decision("ОТКАЗ: недостаточный доход и нет поручителя."))),
        question(
            "Есть ли у вас другой стабильный доход (пенсия, аренда, бизнес)?",
            question(
                "Можете ли вы подтвердить этот доход документами?",
                decision("ОДОБРЕНО: кредит на ограниченную сумму (до 50 000 леев)."),
                decision("ОТКАЗ: доход не подтверждён документами.")),
            decision("ОТКАЗ: нет источника дохода для погашения кредита.")));
}

std::string label(const Step& s) {
    return s.isDecision ? "[РЕШЕНИЕ] " + s.text : s.text;
}

void consult(const DNode* root) {
    std::cout << "Ответьте на вопросы: «да» или «нет».\n\n";
    std::vector<std::pair<std::string, bool>> answers;
    const DNode* node = root;
    while (!node->isLeaf()) {
        bool yes = readYesNo(std::to_string(answers.size() + 1) + ". " + node->info.text + " ");
        answers.push_back({node->info.text, yes});
        node = yes ? node->left : node->right;
    }

    std::cout << "\n==================== РЕЗУЛЬТАТ ====================\n"
              << node->info.text << "\n"
              << "\nВаши ответы:\n";
    for (size_t i = 0; i < answers.size(); ++i)
        std::cout << "  " << i + 1 << ". " << answers[i].first << " - "
                  << (answers[i].second ? "ДА" : "НЕТ") << "\n";
    std::cout << "===================================================\n";
}

int countDecisions(const DNode* tree) {
    if (tree == nullptr) return 0;
    if (tree->isLeaf()) return 1;
    return countDecisions(tree->left) + countDecisions(tree->right);
}

void showTree(const DNode* root) {
    std::cout << "Дерево решений (ДА - левое поддерево, НЕТ - правое):\n\n";
    printTree(std::cout, root, label, "ДА", "НЕТ");
    int decisions = countDecisions(root);
    std::cout << "\nУровней: " << height(root)
              << ", вопросов: " << nodeCount(root) - decisions
              << ", решений: " << decisions << "\n";
}

int main() {
    setupConsole();
    DNode* root = buildLoanTree();

    while (true) {
        std::cout << "\n=== Дерево решений: выдача кредита ===\n"
                  << "1. Пройти опрос\n"
                  << "2. Показать дерево решений\n"
                  << "0. Выход\n";
        int choice = readInt("Ваш выбор: ", 0, 2);
        std::cout << "\n";
        if (choice == 0) break;
        if (choice == 1) consult(root);
        else showTree(root);
    }

    clear(root);
    return 0;
}
