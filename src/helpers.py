from block_layout import BlockLayout
from document_layout import DocumentLayout
from draw import DrawRect, DrawText
from typedclasses import DisplayListItem


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


def paint_tree(
    layout_object: BlockLayout | DocumentLayout,
    display_list: list[DisplayListItem | DrawRect | DrawText],
):
    if layout_object.should_paint():
        display_list.extend(layout_object.paint())

        for child in layout_object.children:
            paint_tree(child, display_list)
