import copy
from typing import Dict, Optional, TypeVar, Generic

# Формат файлов
# type - directed|undirected - Ориентированный/Неориентированный
# weighted: yes|no
# vertices: перечисление вершин через пробел
# <список рёбер>

V = TypeVar("V")
W = TypeVar("W", int, float, None)


class Graph(Generic[V, W]):
    graph: Dict[V, Dict[V, Optional[W]]]
    def __init__(self, directed: bool = False,
                 weighted: bool = False,
                 filename: str = None,
                 other: 'Graph[V, W]' = None):

        if other is not None:
            self.directed = other.directed
            self.weighted = other.weighted
            self.graph = copy.deepcopy(other.graph)
            return

        self.directed = directed
        self.weighted = weighted
        self.graph: Dict[V, Dict[V, Optional[W]]] = {}

        if filename:
            self._load_from_file(filename)

    def _load_from_file(self, filename: str):
        """Считывание графа из файла"""
        with open(filename, "r") as f:
            lines = f.read().splitlines()

        type_line = lines[0].split(":")[1].strip()
        self.directed = type_line.lower() == "directed"

        weighted_line = lines[1].split(":")[1].strip()
        self.weighted = weighted_line.lower() == "yes"

        vertices_line = lines[2].split(":")[1].strip()
        vertices = vertices_line.split()

        for v in vertices:
            self.add_node(v)

        # Парсим рёбра
        for line in lines[4:]:
            parts = line.split()
            if not parts:
                continue

            node1 = parts[0]
            node2 = parts[1]
            weight: W = None

            if self.weighted and len(parts) > 2:
                weight = float(parts[2]) if "." in parts[2] else int(parts[2])

            self.add_arc(node1, node2, weight)

    def add_node(self, node: V):
        """Добавление вершины"""
        if node in self.graph:
            raise ValueError(f"Вершина {node} уже существует!")
        else:
            self.graph[node] = {}

    def add_arc(self, node_1: V, node_2: V, weight: Optional[W] = None):
        """Добавление ребра"""
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

        if not self.directed:
            self.graph[node_2][node_1] = self.graph[node_1][node_2]

    def remove_node(self, node: V):
        """Удаление вершины"""
        if node not in self.graph:
            raise ValueError(f"Вершины {node} нет в графе!")

        # Удаляем все ребра, связанные с вершиной
        del self.graph[node]
        for u in self.graph:
            if node in self.graph[u]:
                del self.graph[u][node]

    def remove_arc(self, node_1: V, node_2: V):
        """Удаление ребра"""
        if node_1 in self.graph and node_2 in self.graph[node_1]:
            del self.graph[node_1][node_2]
        if not self.directed and node_2 in self.graph and node_1 in self.graph[node_2]:
            del self.graph[node_2][node_1]

    def print_graph(self):
        print(self.graph)

    def display_graph(self):
        """Вывод в консоль графа"""
        for node, arc in self.graph.items():
            line = f"{node}: " + ", ".join(
                f"{neighbor}({weight})" if self.weighted else str(neighbor)
                for neighbor, weight in arc.items()
            )
            print(line)

    def write_on_file(self, filename: str):
        """Вывод в файл графа"""
        directed = 'directed' if self.directed else 'undirected'
        weighted = 'yes' if self.weighted else 'no'
        vertices = ' '.join(self.graph.keys())

        with open(filename, "w") as f:
            f.write(f'# type: {directed}\n# weighted: {weighted}\n# vertices: {vertices}\n\n')

            written_arc = set()  # чтобы не дублировать рёбра
            for node, neighbors in self.graph.items():
                for neighbor, weight in neighbors.items():
                    if not self.directed:
                        edge = tuple(sorted((node, neighbor)))
                        if edge in written_arc:
                            continue
                        written_arc.add(edge)

                    if self.weighted:
                        f.write(f"{node} {neighbor} {weight}\n")
                    else:
                        f.write(f"{node} {neighbor}\n")


if __name__ == '__main__':
    graph = Graph[int, int](directed=True, weighted=True)
    graph.add_node(1)
    try:
        graph.add_node(1)
    except Exception as e:
        print("ИСКЛЮЧЕНИЕ:", e)

    graph.add_node(3)
    graph.add_arc(1, 3, weight=5)

    graph.print_graph()

    graph = Graph[str, int](directed=True, weighted=True)

    # добавляем вершины
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")

    # добавляем дуги с весами
    graph.add_arc("A", "B", weight=3)
    graph.add_arc("B", "C", weight=5)
    graph.add_arc("A", "C", weight=10)

    # вывод графа
    graph.print_graph()
    graph.display_graph()

    graph_2 = Graph(filename='graph_3.txt')
    graph_2.display_graph()
    graph_2.write_on_file('graph_write.txt')

    graph_3_new = Graph(filename='graph_write.txt')
    graph_3_new.display_graph()
