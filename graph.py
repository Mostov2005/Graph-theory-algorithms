import copy
import heapq
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
                    # print(neighbor)
                    queue.append(neighbor)
        return visited

    def can_disconnect(self, u: V, v: V) -> bool:
        """
        Проверяет, можно ли закрыть k рёбер,
        чтобы из u нельзя было попасть в v - Задача 5
        Использует обход в глубину
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

    def short_cycle(self, node_u):
        """
        Вывести кратчайший (по числу дуг) цикл орграфа
        содержащий вершину u.
        Использует обход в ширину
        """

        def bfs_with_parent(start: V):
            visited = {start}
            parent = {start: None}
            queue = deque([start])

            while queue:
                node = queue.popleft()
                for neighbor in self.graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parent[neighbor] = node
                        queue.append(neighbor)

            return parent

        if node_u not in self.graph:
            raise ValueError("Вершины нет в графе!")

        parent = bfs_with_parent(node_u)
        print(parent)

        for v in parent:
            if v != node_u and node_u in self.graph[v]:  # Если указывает на u
                path = []
                node = v
                while node is not None:
                    path.append(node)
                    node = parent[node]

                path.reverse()
                path.append(node_u)
                return path

        return None

    def find_skeleton_krascal(self):
        """
        Возвращает минимальный каркас графа c помощью алгоритма Краскала
        """
        if not self.graph:
            return [], 0

        # Собираем все рёбра с весами
        edges = []
        for u in self.graph:
            for v, w in self.graph[u].items():
                if not self.directed:
                    if (v, u, w) in edges:  # чтобы не дублировать ребра
                        continue
                edges.append((u, v, w))

        edges.sort(key=lambda x: x[2])
        print(edges)

        # DSU для проверки циклов
        parent = {v: v for v in self.graph}

        def find(u):  # Поиск корня
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u

        def union(u, v):
            pu, pv = find(u), find(v)
            if pu == pv:
                return False  # уже соединены => будет цикл
            parent[pu] = pv
            return True

        # Построение MST
        mst_edges = []
        total_weight = 0

        for u, v, w in edges:
            if union(u, v):
                mst_edges.append((u, v, w))
                total_weight += w
            if len(mst_edges) == len(self.graph) - 1:
                break

        return mst_edges, total_weight

    def reverse(self):
        new_graph = Graph(directed=self.directed, weighted=self.weighted)

        for v in self.graph:
            new_graph.add_node(v)

        for u in self.graph:
            for v, w in self.graph[u].items():
                new_graph.add_arc(v, u, w)

        return new_graph

    def dijkstra(self, start: V) -> Dict[V, float]:
        """
        Алгоритм Дейкстры: кратчайшие пути от вершины start до всех остальных
        Работает только для взвешенного графа с неотрицательными весами
        """

        if start not in self.graph:
            raise ValueError("Стартовой вершины нет в графе!")

        # Проверка на отрицательные веса
        for u in self.graph:
            for v in self.graph[u]:
                if self.graph[u][v] < 0:
                    raise ValueError("Граф содержит отрицательные веса!")

        # Инициализация
        dist = {v: float('inf') for v in self.graph}
        dist[start] = 0

        priority_queue = [(0, start)]  # (расстояние, вершина)

        while priority_queue:
            current_dist, u = heapq.heappop(priority_queue)

            # Если уже нашли лучше — пропускаем
            if current_dist > dist[u]:
                continue

            for v, weight in self.graph[u].items():
                new_dist = dist[u] + weight

                # relax(u, v)
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    heapq.heappush(priority_queue, (new_dist, v))

        return dist

    def get_path(self, u, v, vertices, next_node):
        if u not in vertices or v not in vertices:
            raise ValueError("Нет вершины")

        index = {v: i for i, v in enumerate(vertices)}

        i, j = index[u], index[v]

        if next_node[i][j] is None:
            return None  # пути нет

        path = [u]
        while u != v:
            u = next_node[index[u]][j]
            path.append(u)

        return path

    def floyd_warshall(self):
        """
        Алгоритм Флойда–Уоршелла
        Возвращает:
        dist[i][j] — кратчайшие расстояния
        next[i][j] — для восстановления пути
        """

        vertices = list(self.graph.keys())
        n = len(vertices)

        # Индексы вершин
        index = {v: i for i, v in enumerate(vertices)}

        # Матрицы
        dist = [[float('inf')] * n for _ in range(n)]
        next_node = [[None] * n for _ in range(n)]

        # Инициализация
        for v in vertices:
            dist[index[v]][index[v]] = 0

        # Заполнение ребёр
        for u in self.graph:
            for v, w in self.graph[u].items():
                i, j = index[u], index[v]
                dist[i][j] = w
                next_node[i][j] = v

        # Основной алгоритм
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]

        return vertices, dist, next_node

    def bellman_ford_negative_cycle(self):
        """
        Находит отрицательный цикл, если он есть.
        Возвращает список вершин цикла или None.
        """

        vertices = list(self.graph.keys())
        dist = {v: 0 for v in vertices}  # 0, а не inf
        parent = {v: None for v in vertices}

        edges = []
        for u in self.graph:
            for v, w in self.graph[u].items():
                edges.append((u, v, w))  # Список ребёр

        # |V| - 1 релаксаций
        for _ in range(len(vertices) - 1):
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u

        # Проверка на цикл (Если послер релаксаций можно уменьшить => есть отрицательный цикл
        cycle_vertex = None

        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                cycle_vertex = v
                break

        if cycle_vertex is None:
            return None  # цикла нет

        # Восстановление цикла
        for _ in range(len(vertices)):
            cycle_vertex = parent[cycle_vertex]

        # теперь точно внутри цикла
        cycle = []
        cur = cycle_vertex

        while True:
            cycle.append(cur)
            cur = parent[cur]
            if cur == cycle_vertex and len(cycle) > 1:
                break

        cycle.reverse()
        return cycle


if __name__ == '__main__':
    graph_8 = Graph(filename='graph_8.txt')
    d8 = graph_8.dijkstra("A")
    print(d8)

    graph_4 = Graph(filename='graph_4.txt')
    d = graph_4.dijkstra('V2')
    res = graph_4.reverse()
    print(d)

    dr = res.dijkstra('V2')
    print(dr)

    # graph_floyd = Graph(filename='graph_8.txt')
    # vertices, dist, next_node = graph_floyd.floyd_warshall()
    # print(vertices)
    # print(dist)
    # print(next_node)
    #
    # u = "A"
    # v = "E"
    #
    # path = graph_floyd.get_path(u, v, vertices, next_node)
    #
    # print("Путь:", path)
    # print("Длина:", dist[vertices.index(u)][vertices.index(v)])

    # graph_negative = Graph(filename='graph_9.txt')
    # cycle = graph_negative.bellman_ford_negative_cycle()
    # print(cycle)
