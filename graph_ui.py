import sys
import math

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QPolygonF
from PyQt6.QtCore import Qt, QPointF
from PyQt6.uic import loadUi
from graph import Graph
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QTableWidgetItem

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
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        for u in self.graph.graph:
            for v, w in self.graph.graph[u].items():

                # избегаем дублирования
                if not self.graph.directed and str(u) > str(v):
                    continue

                if u in self.positions and v in self.positions:
                    x1, y1 = self.positions[u]
                    x2, y2 = self.positions[v]

                    # painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                    # направление линии
                    angle = math.atan2(y2 - y1, x2 - x1)

                    # чтобы линия не заходила внутрь круга
                    start_x = x1 + self.node_radius * math.cos(angle)
                    start_y = y1 + self.node_radius * math.sin(angle)

                    end_x = x2 - self.node_radius * math.cos(angle)
                    end_y = y2 - self.node_radius * math.sin(angle)

                    painter.drawLine(
                        int(start_x),
                        int(start_y),
                        int(end_x),
                        int(end_y)
                    )

                    # стрелка для ориентированного графа
                    if self.graph.directed:
                        self.draw_arrow(painter, start_x, start_y, end_x, end_y)

                    # вес
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

        layout.addWidget(self.canvas)

        self.add_node_btn.clicked.connect(self.add_node)
        self.update_table()

    def update_table(self):
        edges = []

        for u in self.graph.graph:
            for v, w in self.graph.graph[u].items():

                # избегаем дублей
                if not self.graph.directed and str(u) > str(v):
                    continue

                edges.append((u, v, w))

        self.tableWidget.setRowCount(len(edges))
        self.tableWidget.setColumnCount(3)

        self.tableWidget.setHorizontalHeaderLabels(
            ["From", "To", "Weight"]
        )

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

        except Exception as e:
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    graph = Graph(filename='graph_9.txt')

    window = GraphVisualizer(graph)
    window.showMaximized()

    sys.exit(app.exec())
