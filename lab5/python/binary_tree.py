"""Абстрактная структура данных БИНАРНОЕ ДЕРЕВО.

  Node          - узел: информационная часть info и ссылки left / right;
  функции clear, copy_tree, node_count, height, print_tree - работают с любым
                  бинарным деревом (поисковым, деревом решений, деревом выражения);
  BinaryTree    - бинарное ПОИСКОВОЕ дерево: слева меньшие элементы, справа большие.
                  Порядок задаётся операцией < элементов (по ключевому полю).

Интерфейс повторяет пример из методички (Овсянников, ЛР №5) и поддерживает все
перечисленные там операции: добавить, удалить элемент, удалить дерево, проверить
на пустоту, найти данные, копировать дерево, три обхода, вывод дерева.
"""


class Node:
    __slots__ = ("info", "left", "right")

    def __init__(self, info, left=None, right=None):
        self.info = info        # информационная часть
        self.left = left        # левый «ребёнок»
        self.right = right      # правый «ребёнок»

    def is_leaf(self):
        return self.left is None and self.right is None


# ---------- общие функции для любого бинарного дерева ----------

def copy_tree(tree):
    """Полная копия поддерева (обход в прямом порядке)."""
    if tree is None:
        return None
    return Node(tree.info, copy_tree(tree.left), copy_tree(tree.right))


def node_count(tree):
    if tree is None:
        return 0
    return 1 + node_count(tree.left) + node_count(tree.right)


def height(tree):
    """Количество уровней: пустое дерево - 0, только корень - 1."""
    if tree is None:
        return 0
    return 1 + max(height(tree.left), height(tree.right))


def print_tree(root, label=str, left_tag="Л", right_tag="П"):
    """Выводит структуру дерева в виде «каталога»:

        50
        ├─Л─ 30
        │    ├─Л─ 20
        │    └─П─ 40
        └─П─ 70

    Если у узла есть только один ребёнок, на месте второго выводится «∅».
    """
    if root is None:
        print("(дерево пусто)")
        return
    print(label(root.info))
    _print_subtree(root, label, "", left_tag, right_tag)


def _print_subtree(node, label, prefix, left_tag, right_tag):
    if node.is_leaf():
        return
    for child, tag, last in ((node.left, left_tag, False), (node.right, right_tag, True)):
        connector = "└─" if last else "├─"
        if child is None:
            print(f"{prefix}{connector}{tag}─ ∅")
            continue
        print(f"{prefix}{connector}{tag}─ {label(child.info)}")
        _print_subtree(child, label, prefix + ("     " if last else "│    "), left_tag, right_tag)


# ---------- бинарное поисковое дерево ----------

class BinaryTree:
    def __init__(self):
        self._root = None

    def copy(self):
        """Копия дерева (аналог копирующего конструктора в C++)."""
        other = BinaryTree()
        other._root = copy_tree(self._root)
        return other

    def is_empty(self):
        return self._root is None

    def node_count(self):
        return node_count(self._root)

    def height(self):
        return height(self._root)

    def destroy(self):
        """Удаляет все узлы (память освобождает сборщик мусора)."""
        self._root = None

    def insert_item(self, item):
        """Добавляет элемент как новый лист. Возвращает False, если элемент
        с таким ключом уже есть (ключи в поисковом дереве уникальны)."""
        if self.retrieve_item(item) is not None:
            return False
        self._root = self._insert(self._root, item)
        return True

    def delete_item(self, item):
        """Удаляет элемент с ключом item. Возвращает False, если такого нет."""
        if self.retrieve_item(item) is None:
            return False
        self._root = self._delete(self._root, item)
        return True

    def retrieve_item(self, item):
        """Возвращает данные с ключом item или None."""
        tree = self._root
        while tree is not None:
            if item < tree.info:
                tree = tree.left
            elif tree.info < item:
                tree = tree.right
            else:
                return tree.info
        return None

    # Обходы: visit(info) вызывается для каждого узла в порядке маршрута.

    def inorder_tree(self, visit):
        self._inorder(self._root, visit)

    def preorder_tree(self, visit):
        self._preorder(self._root, visit)

    def postorder_tree(self, visit):
        self._postorder(self._root, visit)

    def print(self, label=str):
        print_tree(self._root, label)

    # Рекурсивные функции возвращают новый корень поддерева - так в Python
    # заменяется передача указателя по ссылке (Node<T>*&) из C++.

    def _insert(self, tree, item):
        if tree is None:                    # base case: место найдено
            return Node(item)
        if item < tree.info:
            tree.left = self._insert(tree.left, item)
        else:
            tree.right = self._insert(tree.right, item)
        return tree

    def _delete(self, tree, item):
        """Функция №2 из методички: находит узел с данными item и передаёт его _delete_node."""
        if item < tree.info:
            tree.left = self._delete(tree.left, item)
            return tree
        if tree.info < item:
            tree.right = self._delete(tree.right, item)
            return tree
        return self._delete_node(tree)

    def _delete_node(self, tree):
        """Функция №1 из методички: удаляет данный узел в зависимости от числа детей."""
        if tree.left is None:               # лист или только правый ребёнок
            return tree.right
        if tree.right is None:              # только левый ребёнок
            return tree.left
        # Два ребёнка: предшествующий элемент - самый правый в левом поддереве.
        # У него нет правого ребёнка, поэтому его удаление - случай 1 или 2.
        pred = tree.left
        while pred.right is not None:
            pred = pred.right
        tree.info = pred.info               # перезаписываем данные
        tree.left = self._delete(tree.left, pred.info)
        return tree

    @staticmethod
    def _inorder(tree, visit):
        if tree is None:
            return
        BinaryTree._inorder(tree.left, visit)
        visit(tree.info)
        BinaryTree._inorder(tree.right, visit)

    @staticmethod
    def _preorder(tree, visit):
        if tree is None:
            return
        visit(tree.info)
        BinaryTree._preorder(tree.left, visit)
        BinaryTree._preorder(tree.right, visit)

    @staticmethod
    def _postorder(tree, visit):
        if tree is None:
            return
        BinaryTree._postorder(tree.left, visit)
        BinaryTree._postorder(tree.right, visit)
        visit(tree.info)
