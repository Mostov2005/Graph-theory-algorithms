from typing import Dict, Optional, TypeVar, Generic

# Формат файлов
# type - directed|undirected - Ориентированный/Неориентированный
# weighted: yes|no
# vertices: перечисление вершин через пробел
# <список рёбер>

V = TypeVar("V")
W = TypeVar("W", int, float, None)


class Graph(Generic[V, W]):
    def __init__(self, directed: bool = False, weighted: bool = False):
        self.directed = directed
        self.weighted = weighted
        self.graph: Dict[V, Dict[V, Optional[W]]] = {}

    def add_node(self, node: V):
        if node in self.graph:
            raise ValueError(f"Вершина {node} уже существует!")
        else:
            self.graph[node] = {}

    def add_arc(self, node_1: V, node_2: V, weight: Optional[W] = None):
        if node_1 not in self.graph:
            raise ValueError(f"Вершины {node_1} нет в графе!")
        if node_2 not in self.graph:
            raise ValueError(f"Вершины {node_2} нет в графе!")

        if self.weighted:
            if weight is None:
                raise ValueError("Для взвешенного графа нужно указать вес!")
            self.graph[node_1][node_2] = weight
        else:
            self.graph[node_1][node_2] = 1  # невзвешенный граф — просто ставим 1
        if self.directed:
            self.graph[node_2][node_1] = self.graph[node_1][node_2]

    def print_graph(self):
        print(self.graph)


if __name__ == '__main__':
    graph = Graph[str, int](directed=True, weighted=True)
    graph.add_node(1)
    try:
        graph.add_node(1)
    except Exception as e:
        print("ИСКЛЮЧЕНИЕ:", e)

    graph.add_node(3)
    graph.add_arc(1, 3, weight=5)

    graph.print_graph()
