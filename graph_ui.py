import sys
import math

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

from graph import Graph


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

    # -------------------------
    # 🎨 ОТРИСОВКА
    # -------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.positions:
            self.auto_layout()

        self.draw_edges(painter)
        self.draw_nodes(painter)

    # -------------------------
    # 📍 АВТО-РАСКЛАДКА
    # -------------------------
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

    # -------------------------
    # 🔗 РЁБРА
    # -------------------------
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

                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))

                    # вес
                    if self.graph.weighted:
                        mx = (x1 + x2) / 2
                        my = (y1 + y2) / 2
                        painter.drawText(int(mx), int(my), str(w))

    # -------------------------
    # 🔵 ВЕРШИНЫ
    # -------------------------
    def draw_nodes(self, painter):
        r = self.node_radius

        for node, (x, y) in self.positions.items():
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(QBrush(Qt.GlobalColor.white))

            painter.drawEllipse(int(x - r), int(y - r), 2 * r, 2 * r)

            painter.drawText(int(x - 5), int(y + 5), str(node))

    # -------------------------
    # 🖱 НАЖАТИЕ МЫШИ
    # -------------------------
    def mousePressEvent(self, event):
        x = event.position().x()
        y = event.position().y()

        for node, (nx, ny) in self.positions.items():
            dist = math.hypot(nx - x, ny - y)
            if dist <= self.node_radius:
                self.dragged_node = node
                break

    # -------------------------
    # 🖱 ДВИЖЕНИЕ МЫШИ
    # -------------------------
    def mouseMoveEvent(self, event):
        if self.dragged_node is not None:
            x = event.position().x()
            y = event.position().y()

            self.positions[self.dragged_node] = (x, y)
            self.update()

    # -------------------------
    # 🖱 ОТПУСКАНИЕ МЫШИ
    # -------------------------
    def mouseReleaseEvent(self, event):
        self.dragged_node = None


class GraphVisualizer(QMainWindow):
    def __init__(self, graph):
        super().__init__()

        loadUi('mainwindow.ui', self)
        self.graph = graph

        # создаём canvas
        self.canvas = GraphCanvas(self.graph)

        # вставляем его ВНУТРЬ graphWidget
        # (важно: у graphWidget должен быть layout!)
        self.graphWidget.layout().addWidget(self.canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    graph = Graph(filename='graph_8.txt')

    window = GraphVisualizer(graph)
    window.showMaximized()

    sys.exit(app.exec())
