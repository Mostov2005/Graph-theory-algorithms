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
            print("6. Выход")

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
