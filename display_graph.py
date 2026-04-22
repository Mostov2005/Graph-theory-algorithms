from graph import Graph


class DisplayGraph:
    def __init__(self, graph):
        self.graph = graph

    def run(self):
        while True:
            print("0. Информация о графе")
            print("1. Показать граф")
            print("2. Добавить вершину")
            print("3. Удалить вершину")
            print("4. Добавить ребро")
            print("5. Удалить ребро")
            print("6. Вывести  полустепень исхода данной вершины")
            print('7. Вывести все вершины, смежные с данной')
            print('8. Удалить висячие вершины')
            print("9. Определить, можно ли добиться того, чтобы" +
                  " из вершины u нельзя было попасть в вершину v, закрыв заданные k рёбер")
            print("10. Вывести кратчайший цикл орграфа, содержащий вершину u.")
            print('11. Вывести кратчайшие пути до вершины u из всех остальных вершин (Дейстра, задание 8)')
            print('12. Вывести кратчайший путь из вершины u до вершины v (Флойда, задание 9)')
            print("999. Выход")

            choice = input("Выберите действие: ")

            try:
                if choice == "0":
                    print('Ориентированный' if graph.directed else 'Неориентированный')
                    print('Взвешенный' if graph.weighted else 'Невзвешенный')
                    graph.print_graph()

                elif choice == "1":
                    self.graph.display_graph()

                elif choice == "2":
                    node = input("Введите имя вершины: ")
                    self.graph.add_node(node)

                elif choice == "3":
                    node = input("Введите имя вершины: ")
                    self.graph.remove_node(node)

                elif choice == "4":
                    node1 = input("Откуда: ")
                    node2 = input("Куда: ")

                    if self.graph.weighted:
                        weight = input("Вес: ")
                        weight = float(weight) if "." in weight else int(weight)
                        self.graph.add_arc(node1, node2, weight)
                    else:
                        self.graph.add_arc(node1, node2)

                elif choice == "5":
                    node1 = input("Откуда: ")
                    node2 = input("Куда: ")
                    self.graph.remove_arc(node1, node2)

                elif choice == "6":
                    node = input("Вершина: ")
                    print(f'полустепень исхода: {self.graph.out_degree(node)}')

                elif choice == "7":
                    node = input("Вершина: ")
                    print(f'Вершины смежные с {node}: {self.graph.neighbors(node)}')

                elif choice == "8":
                    self.graph = self.graph.remove_pendant_vertices()
                    print('Висячие вершины удалены!')

                elif choice == "9":
                    node1 = input("Откуда: ")
                    node2 = input("Куда: ")
                    self.graph = self.graph.remove_pendant_vertices()
                    can = self.graph.can_disconnect(node1, node2)
                    if can:
                        print('Достичь нельзя!')
                    else:
                        print('Достичь можно!')

                elif choice == "10":
                    node_u = input("Вершина u: ")
                    cycle = graph.short_cycle(node_u)
                    if cycle is not None:
                        print(" -> ".join(cycle))
                    else:
                        print("Нет цикла!")

                elif choice == "11":
                    node_u = input("Вершина u: ")
                    rev = self.graph.reverse()
                    dist = rev.dijkstra(node_u)
                    print(f"Кратчайшие пути до вершины {node_u}:")
                    for v, d in dist.items():
                        print(f"{v}: {d}")

                elif choice == "12":
                    node_u = input("Вершина u: ")
                    node_v = input("Вершина v: ")
                    vertices, dist, next_node = self.graph.floyd_warshall()
                    path = self.graph.get_path(node_u, node_v, vertices, next_node)
                    if path is not None:
                        print("Путь:", path)
                        print("Длина:", dist[vertices.index(node_u)][vertices.index(node_v)])
                    else:
                        print('Нет пути!')

                elif choice == "999":
                    print("Пока-Пока!")
                    break

                else:
                    print("Неверный выбор!")

                print()

            except Exception as e:
                print("Ошибка:", e)


if __name__ == '__main__':
    graph = Graph(filename='graph_4.txt')
    display_graph = DisplayGraph(graph)
    display_graph.run()
