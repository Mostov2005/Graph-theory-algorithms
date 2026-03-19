import copy
from typing import Dict, Optional, TypeVar, Generic, List, Tuple
from collections import deque
from itertools import combinations

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
                 other_graph: 'Graph[V, W]' = None):

        if other_graph is not None:
            self.directed = other_graph.directed
            self.weighted = other_graph.weighted
            self.graph = copy.deepcopy(other_graph.graph)
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

            # print(node1, node2)
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
        if node_1 not in self.graph:
            raise ValueError("Нет вершины 1!")

        if node_2 not in self.graph[node_1]:
            raise ValueError("Нет ребра!")

        if node_1 in self.graph and node_2 in self.graph[node_1]:
            del self.graph[node_1][node_2]

        if not self.directed and node_2 in self.graph and node_1 in self.graph[node_2]:
            del self.graph[node_2][node_1]

    def print_graph(self):
        print("Список смежности: ")
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
        """Вывод в файл графа
        # Формат файлов
        # type - directed|undirected - Ориентированный/Неориентированный
        # weighted: yes|no
        # vertices: перечисление вершин через пробел
        # <список рёбер>
        """
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

    def out_degree(self, node: V) -> int:  # la Вывести полустепень исхода данной вершины орграфа
        if node not in self.graph:
            raise ValueError("Вершины нет в графе!")
        return len(self.graph[node])

    def neighbors(self, node: V):
        if node not in self.graph:
            raise ValueError("Вершины нет в графе!")
        # В ориентированном графе вершина у смежна с вершиной х, если существует дуга (x, y)
        return list(self.graph[node].keys())

    def remove_pendant_vertices(self):  # lb 12 Удаление висячих вершин
        new_graph = Graph(other_graph=self)

        if not self.directed:
            pendant = [
                v for v in self.graph
                if len(self.graph[v]) == 1 and v not in self.graph[v]
            ]
        else:
            indeg = {v: 0 for v in self.graph}

            for u in self.graph:
                for v in self.graph[u]:
                    indeg[v] += 1

            pendant = [
                v for v in self.graph
                if indeg[v] + len(self.graph[v]) == 1
            ]
        for v in pendant:
            new_graph.remove_node(v)

        return new_graph

    def dfs(self, start: V, visited=None):  # Обход в глубину
        if visited is None:
            visited = set()
        print(start)
        visited.add(start)

        for neighbor in self.graph[start]:
            if neighbor not in visited:
                self.dfs(neighbor, visited)
        return visited

    def bfs(self, start: V):  # Обход в ширину
        visited = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            print(node)
            visited.add(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited and neighbor not in queue:
                    queue.append(neighbor)
        return visited

    from itertools import combinations
    from typing import List, Tuple

    def can_disconnect(self, u: V, v: V) -> bool:
        """
        Проверяет, можно ли закрыть k рёбер,
        чтобы из u нельзя было попасть в v - Задача 5
        """
        if u not in self.graph or v not in self.graph:
            raise ValueError("u или v нет в графе")

        temp_graph = Graph(other_graph=self)
        while True:
            print("0. Хватит удалять")
            print("1. Удалить ребро")
            choice = input("Выберите действие: ")
            try:
                if choice == "0":
                    break
                elif choice == "1":
                    node1 = input("Откуда: ")
                    node2 = input("Куда: ")
                    temp_graph.remove_arc(node1, node2)
                else:
                    print("Неверный выбор!")

                print()
            except Exception as e:
                print("Ошибка:", e)

        visited = temp_graph.dfs(u)

        if v not in visited:
            return True

        return False





if __name__ == '__main__':
    graph_5 = Graph(filename='graph_5.txt')
    graph_5.display_graph()
    print('Обход в глубину:')
    a = graph_5.dfs("A")
    print(a)
    # print('\nОбход в глубину:')
    # b = graph_5.bfs("A")
    # print(b)

    can = graph_5.can_disconnect("A", "E")
    print(can)
