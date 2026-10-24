// Абстрактная структура данных БИНАРНОЕ ДЕРЕВО.
//
//   Node<T>        - узел: информационная часть info и указатели left / right;
//   функции clear, copyTree, nodeCount, height, printTree - работают с любым
//                    бинарным деревом (поисковым, деревом решений, деревом выражения);
//   BinaryTree<T>  - бинарное ПОИСКОВОЕ дерево: слева меньшие элементы, справа большие.
//                    Порядок задаётся operator< типа T (по ключевому полю).
//
// Интерфейс повторяет пример из методички (Овсянников, ЛР №5) и поддерживает все
// перечисленные там операции: добавить, удалить элемент, удалить дерево, проверить
// на пустоту, найти данные, копировать дерево, три обхода, вывод дерева.

#pragma once

#include <iostream>
#include <string>

template<class T>
struct Node {
    T info;               // информационная часть
    Node<T>* left;        // левый «ребёнок»
    Node<T>* right;       // правый «ребёнок»

    explicit Node(const T& d, Node<T>* l = nullptr, Node<T>* r = nullptr)
        : info(d), left(l), right(r) {}

    bool isLeaf() const { return left == nullptr && right == nullptr; }
};

// ---------- общие функции для любого бинарного дерева ----------

// Удаляет все узлы поддерева (обход в обратном порядке: сначала дети, потом узел).
template<class T>
void clear(Node<T>*& tree) {
    if (tree == nullptr) return;
    clear(tree->left);
    clear(tree->right);
    delete tree;
    tree = nullptr;
}

// Возвращает полную копию поддерева (обход в прямом порядке).
template<class T>
Node<T>* copyTree(const Node<T>* tree) {
    if (tree == nullptr) return nullptr;
    return new Node<T>(tree->info, copyTree(tree->left), copyTree(tree->right));
}

template<class T>
int nodeCount(const Node<T>* tree) {
    if (tree == nullptr) return 0;
    return 1 + nodeCount(tree->left) + nodeCount(tree->right);
}

// Количество уровней: пустое дерево - 0, только корень - 1.
template<class T>
int height(const Node<T>* tree) {
    if (tree == nullptr) return 0;
    int hl = height(tree->left), hr = height(tree->right);
    return 1 + (hl > hr ? hl : hr);
}

// Выводит структуру дерева в виде «каталога»:
//
//   50
//   ├─Л─ 30
//   │    ├─Л─ 20
//   │    └─П─ 40
//   └─П─ 70
//
// label(info) возвращает строку для узла, leftTag / rightTag - подписи рёбер.
// Если у узла есть только один ребёнок, на месте второго выводится «∅».
template<class T, class Label>
void printSubtree(std::ostream& out, const Node<T>* node, Label& label, const std::string& prefix,
                  const std::string& leftTag, const std::string& rightTag) {
    if (node->isLeaf()) return;
    const Node<T>* children[2] = {node->left, node->right};
    const std::string* tags[2] = {&leftTag, &rightTag};
    for (int k = 0; k < 2; ++k) {
        bool last = (k == 1);
        out << prefix << (last ? "└─" : "├─") << *tags[k] << "─ ";
        if (children[k] == nullptr) {
            out << "∅\n";
            continue;
        }
        out << label(children[k]->info) << "\n";
        printSubtree(out, children[k], label, prefix + (last ? "     " : "│    "), leftTag, rightTag);
    }
}

template<class T, class Label>
void printTree(std::ostream& out, const Node<T>* root, Label label,
               const std::string& leftTag = "Л", const std::string& rightTag = "П") {
    if (root == nullptr) {
        out << "(дерево пусто)\n";
        return;
    }
    out << label(root->info) << "\n";
    printSubtree(out, root, label, "", leftTag, rightTag);
}

// ---------- бинарное поисковое дерево ----------

template<class T>
class BinaryTree {
public:
    BinaryTree() : root(nullptr) {}
    ~BinaryTree() { destroy(); }

    BinaryTree(const BinaryTree<T>& other) : root(copyTree(other.root)) {}

    BinaryTree<T>& operator=(const BinaryTree<T>& other) {
        if (this != &other) {
            destroy();
            root = copyTree(other.root);
        }
        return *this;
    }

    bool isEmpty() const { return root == nullptr; }
    int nodeCount() const { return ::nodeCount(root); }
    int height() const { return ::height(root); }
    void destroy() { clear(root); }

    // Добавляет элемент как новый лист. Возвращает false, если элемент
    // с таким ключом уже есть (ключи в поисковом дереве уникальны).
    bool insertItem(const T& item) { return insert(root, item); }

    // Удаляет элемент с ключом item. Возвращает false, если такого нет.
    bool deleteItem(const T& item) { return remove(root, item); }

    // Возвращает указатель на данные с ключом item или nullptr.
    T* retrieveItem(const T& item) const { return search(root, item); }

    // Обходы: visit(info) вызывается для каждого узла в порядке маршрута.
    template<class F> void inorderTree(F visit) const { inorder(root, visit); }
    template<class F> void preorderTree(F visit) const { preorder(root, visit); }
    template<class F> void postorderTree(F visit) const { postorder(root, visit); }

    template<class Label>
    void print(std::ostream& out, Label label) const { printTree(out, root, label); }

private:
    Node<T>* root;

    bool insert(Node<T>*& tree, const T& item) {
        if (tree == nullptr) {                      // base case: место найдено
            tree = new Node<T>(item);
            return true;
        }
        if (item < tree->info) return insert(tree->left, item);
        if (tree->info < item) return insert(tree->right, item);
        return false;                               // такой ключ уже есть
    }

    T* search(Node<T>* tree, const T& item) const {
        while (tree != nullptr) {
            if (item < tree->info) tree = tree->left;
            else if (tree->info < item) tree = tree->right;
            else return &tree->info;
        }
        return nullptr;
    }

    // Функция №2 из методички: находит узел с данными item и передаёт его deleteNode.
    bool remove(Node<T>*& tree, const T& item) {
        if (tree == nullptr) return false;
        if (item < tree->info) return remove(tree->left, item);
        if (tree->info < item) return remove(tree->right, item);
        deleteNode(tree);
        return true;
    }

    // Функция №1 из методички: удаляет данный узел в зависимости от числа детей.
    void deleteNode(Node<T>*& tree) {
        Node<T>* temp = tree;
        if (tree->left == nullptr) {                // лист или только правый ребёнок
            tree = tree->right;
            delete temp;
        } else if (tree->right == nullptr) {        // только левый ребёнок
            tree = tree->left;
            delete temp;
        } else {                                    // два ребёнка
            // Предшествующий элемент - самый правый в левом поддереве.
            // У него нет правого ребёнка, поэтому его удаление - случай 1 или 2.
            Node<T>** pred = &tree->left;
            while ((*pred)->right != nullptr) pred = &(*pred)->right;
            tree->info = (*pred)->info;             // перезаписываем данные
            deleteNode(*pred);                      // удаляем предшествующий узел
        }
    }

    template<class F> static void inorder(const Node<T>* tree, F& visit) {
        if (tree == nullptr) return;
        inorder(tree->left, visit);
        visit(tree->info);
        inorder(tree->right, visit);
    }

    template<class F> static void preorder(const Node<T>* tree, F& visit) {
        if (tree == nullptr) return;
        visit(tree->info);
        preorder(tree->left, visit);
        preorder(tree->right, visit);
    }

    template<class F> static void postorder(const Node<T>* tree, F& visit) {
        if (tree == nullptr) return;
        postorder(tree->left, visit);
        postorder(tree->right, visit);
        visit(tree->info);
    }
};
