def tree_to_list(tree, list: list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


def cascade_priority(rule: tuple) -> int:
    selector, _ = rule
    return selector.priority


def print_tree(node, indent: int = 0) -> None:
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
