import sys
import math
from collections import deque

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QPolygonF
from PyQt6.QtCore import Qt, QPointF
from PyQt6.uic import loadUi
from graph import Graph
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import QTimer


class GraphCanvas(QWidget):
    def __init__(self, graph):
        super().__init__()
        self.graph = graph

        # позиции вершин
        self.positions = {}

        # параметры
        self.node_radius = 20

        # для перетаскивания
        self.dragged_node = None

        # включаем отслеживание мыши
        self.setMouseTracking(True)

        self.highlight_edges = set()
        self.highlight_color = Qt.GlobalColor.red

    def set_highlight_edges(self, edges):
        self.highlight_edges = set(edges)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.positions:
            self.auto_layout()

        self.draw_edges(painter)
        self.draw_nodes(painter)

    def auto_layout(self):
        nodes = list(self.graph.graph.keys())
        n = len(nodes)

        if n == 0:
            return

        w = self.width()
        h = self.height()

        cx, cy = w // 2, h // 2
        radius = min(w, h) // 3

        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            self.positions[node] = (x, y)

    def draw_edges(self, painter):
        for u in self.graph.graph:
            for v, w in self.graph.graph[u].items():

                # избегаем дублирования в неориентированном графе
                if not self.graph.directed and str(u) > str(v):
                    continue

                if u in self.positions and v in self.positions:
                    x1, y1 = self.positions[u]
                    x2, y2 = self.positions[v]

                    angle = math.atan2(y2 - y1, x2 - x1)

                    # чтобы линия не заходила в вершины
                    start_x = x1 + self.node_radius * math.cos(angle)
                    start_y = y1 + self.node_radius * math.sin(angle)

                    end_x = x2 - self.node_radius * math.cos(angle)
                    end_y = y2 - self.node_radius * math.sin(angle)

                    # ПОДСВЕТКА BFS/DFS
                    edge = (u, v)
                    rev_edge = (v, u)

                    if edge in self.highlight_edges or (
                            not self.graph.directed and rev_edge in self.highlight_edges
                    ):
                        painter.setPen(QPen(self.highlight_color, 4))
                    else:
                        painter.setPen(QPen(Qt.GlobalColor.black, 2))

                    painter.drawLine(
                        int(start_x),
                        int(start_y),
                        int(end_x),
                        int(end_y)
                    )

                    # стрелка для ориентированного графа
                    if self.graph.directed:
                        self.draw_arrow(painter, start_x, start_y, end_x, end_y)

                    # вес ребра
                    if self.graph.weighted:
                        mx = (x1 + x2) / 2 + 15
                        my = (y1 + y2) / 2 + 15

                        font = QFont()
                        font.setPointSize(16)
                        painter.setFont(font)
                        painter.drawText(int(mx), int(my), str(w))

    def draw_arrow(self, painter, x1, y1, x2, y2):
        angle = math.atan2(y2 - y1, x2 - x1)

        arrow_size = 10

        # конец линии перед вершиной
        x2_arrow = x2 - (self.node_radius - 18) * math.cos(angle)
        y2_arrow = y2 - (self.node_radius - 18) * math.sin(angle)

        # точки стрелки
        left_x = x2_arrow - arrow_size * math.cos(angle - math.pi / 6)
        left_y = y2_arrow - arrow_size * math.sin(angle - math.pi / 6)

        right_x = x2_arrow - arrow_size * math.cos(angle + math.pi / 6)
        right_y = y2_arrow - arrow_size * math.sin(angle + math.pi / 6)

        arrow_head = QPolygonF([
            QPointF(x2_arrow, y2_arrow),
            QPointF(left_x, left_y),
            QPointF(right_x, right_y)
        ])

        painter.setBrush(Qt.GlobalColor.black)
        painter.drawPolygon(arrow_head)

    def draw_nodes(self, painter):
        r = self.node_radius

        for node, (x, y) in self.positions.items():
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(QBrush(Qt.GlobalColor.white))

            painter.drawEllipse(int(x - r), int(y - r), 2 * r, 2 * r)

            painter.drawText(int(x - 10), int(y + 10), str(node))

    def mousePressEvent(self, event):
        x = event.position().x()
        y = event.position().y()

        for node, (nx, ny) in self.positions.items():
            dist = math.hypot(nx - x, ny - y)
            if dist <= self.node_radius:
                self.dragged_node = node
                break

    def mouseMoveEvent(self, event):
        if self.dragged_node is not None:
            x = event.position().x()
            y = event.position().y()

            self.positions[self.dragged_node] = (x, y)
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragged_node = None


class GraphVisualizer(QMainWindow):
    def __init__(self, graph):
        super().__init__()

        loadUi('mainwindow.ui', self)
        self.graph = graph

        # создаём canvas
        self.canvas = GraphCanvas(self.graph)
        # self.graphWidget.layout().addWidget(self.canvas)

        layout = QVBoxLayout(self.graphWidget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_step)

        self.anim_edges = []
        self.anim_index = 0
        self.anim_color = Qt.GlobalColor.red

        layout.addWidget(self.canvas)

        self.add_node_btn.clicked.connect(self.add_node)
        self.delete_node_btn.clicked.connect(self.delete_node)
        self.delete_edge_btn.clicked.connect(self.delete_edge)
        self.add_edge_btn.clicked.connect(self.add_edge)
        self.bfs_btn.clicked.connect(self.run_bfs)
        self.dfs_btn.clicked.connect(self.run_dfs)
        self.refresh_btn.clicked.connect(self.refresh_graph)
        self.download_btn.clicked.connect(self.load_graph_from_file)
        self.update_table()

    def update_table(self):
        self.tableWidget.clearContents()

        edges = []
        used_vertices = set()

        for u in self.graph.graph:
            for v, w in self.graph.graph[u].items():

                if not self.graph.directed and str(u) > str(v):
                    continue

                edges.append((u, v, w))
                used_vertices.add(u)
                used_vertices.add(v)

        for v in self.graph.graph:
            if v not in used_vertices:
                edges.append((v, "", ""))

        self.tableWidget.setRowCount(len(edges))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["From", "To", "Weight"])

        for row, (u, v, w) in enumerate(edges):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(u)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(v)))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(w)))

    def add_node(self):
        node_name = self.lineEdit_add_node.text().strip()

        if not node_name:
            return

        try:
            self.graph.add_node(node_name)

            # пересчитать позиции
            self.canvas.auto_layout()

            # перерисовать
            self.canvas.update()

            # очистить поле
            self.lineEdit_add_node.clear()
            self.update_table()

        except Exception as e:
            print(e)

    def add_edge(self):
        u = self.lineEdit_add_edge_from.text().strip()
        v = self.lineEdit_add_edge_to.text().strip()

        if not u or not v:
            return

        try:
            if not self.graph.weighted:
                self.graph.add_arc(u, v)

            else:
                w_text = self.lineEdit_add_edge_weight.text().strip()

                # если ничего не введено
                if not w_text:
                    w = 1
                else:
                    try:
                        w = float(w_text) if '.' in w_text else int(w_text)
                    except ValueError:
                        w = 1

                self.graph.add_arc(u, v, w)

            # обновление UI
            self.canvas.auto_layout()
            self.canvas.update()
            self.update_table()

            # очистка полей (удобство)
            self.lineEdit_add_edge_from.clear()
            self.lineEdit_add_edge_to.clear()
            self.lineEdit_add_edge_weight.clear()

        except Exception as e:
            print("Ошибка добавления ребра:", e)

    def delete_edge(self):
        u = self.lineEdit_delete_edge_from.text().strip()
        v = self.lineEdit_delete_edge_to.text().strip()

        if not u or not v:
            return

        try:
            self.graph.remove_arc(u, v)

            self.canvas.update()
            self.update_table()

        except Exception as e:
            print("Ошибка удаления ребра:", e)

    def delete_node(self):
        node = self.lineEdit_delete_node.text().strip()

        if not node:
            return

        try:
            self.graph.remove_node(node)

            # убрать из позиций canvas
            if node in self.canvas.positions:
                del self.canvas.positions[node]

            self.canvas.auto_layout()
            self.canvas.update()
            self.update_table()

        except Exception as e:
            print("Ошибка удаления вершины:", e)

    def run_bfs(self):
        start = self.lineEdit_bfs.text().strip()
        if not start:
            return

        self.anim_edges = self.graph.bfs_edges(start)
        self.anim_index = 0
        self.anim_color = Qt.GlobalColor.red

        self.canvas.highlight_edges = set()
        self.canvas.highlight_color = self.anim_color

        self.timer.start(400)  # скорость анимации (мс)

    def run_dfs(self):
        start = self.lineEdit_dfs.text().strip()
        if not start:
            return

        self.anim_edges = self.graph.dfs_edges(start)
        self.anim_index = 0
        self.anim_color = Qt.GlobalColor.blue

        self.canvas.highlight_edges = set()
        self.canvas.highlight_color = self.anim_color

        self.timer.start(400)

    def animate_step(self):
        if self.anim_index >= len(self.anim_edges):
            self.timer.stop()
            return

        edge = self.anim_edges[self.anim_index]
        self.canvas.highlight_edges.add(edge)

        self.canvas.update()
        self.anim_index += 1

    def refresh_graph(self):
        if hasattr(self, "timer"):
            self.timer.stop()

        self.canvas.highlight_edges = set()
        self.canvas.highlight_color = Qt.GlobalColor.black

        self.canvas.positions.clear()
        self.canvas.auto_layout()

        self.canvas.update()
        self.update_table()

    def load_graph_from_file(self):
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл графа",
            "",
            "Text files (*.txt)"
        )

        if not file_path:
            return

        try:
            self.graph = Graph(filename=file_path)

            self.canvas.graph = self.graph
            self.canvas.positions.clear()
            self.canvas.auto_layout()

            self.canvas.highlight_edges = set()
            self.canvas.update()

            self.update_table()

        except Exception as e:
            print("Ошибка загрузки графа:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    graph = Graph(filename='graph_9.txt')

    window = GraphVisualizer(graph)
    window.showMaximized()

    sys.exit(app.exec())
