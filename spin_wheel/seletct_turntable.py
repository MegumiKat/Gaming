# spin_lines_only.py
# 需要: pip install PyQt6
from ctypes import pointer
import sys
import math
from PyQt6 import QtCore, QtGui, QtWidgets


class WheelWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # fixed sectors
        self.sectors = ["A", "B"]
        
        # 指针默认指向的选项（按文字来找）
        # defualt point lable
        # 想默认指向第 0 个，就写 self.target_label = self.sectors[0]
        self.target_label = "A"


        # 当前“分割线”的旋转角度（度）
        self.current_angle = 0.0
        self.spinning = False

        # 动画相关
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.duration = 5000      # 动画总时长 ms
        self.elapsed = 0
        self.rotations = 3        # 分割线总共转多少圈（整数保证回到原位置）

        self.setMinimumSize(400, 400)

    def start_spin(self):
        """开始转动分割线"""
        if self.spinning:
            return
        self.spinning = True
        self.elapsed = 0
        self.current_angle = 0.0
        self.timer.start(33)  # ~60 FPS

    def on_timeout(self):
        self.elapsed += self.timer.interval()
        t = max(0.0, min(1.0, self.elapsed / self.duration))

        # 缓出：先快后慢
        ease = 1 - (1 - t) ** 3
        total_angle = 360.0 * self.rotations
        self.current_angle = total_angle * ease

        self.update()

        if t >= 1.0:
            self.timer.stop()
            self.spinning = False
            # 回到初始位置
            self.current_angle = 0.0
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        rect = self.rect()
        size = min(rect.width(), rect.height())
        radius = size * 0.4
        cx = rect.center().x()
        cy = rect.center().y()

        painter.translate(cx, cy)


        # 画“静止”的扇形区域
        n = len(self.sectors)
        if n == 0:
            return

        sector_angle = 360.0 / n

        #计算目标是第几个
        try:
            target_index = self.sectors.index(self.target_label)
        except ValueError :
            target_index = 0
        
        #正上方，对应我们极坐标里的 90 度
        pointer_angle = 90.0

        # 计算一个固定偏移角：让 target_index 的扇形中心对准 90 度
        # 中心角 = base_angle + target_index * sector_angle + sector_angle/2 = pointer_angle
        base_angle = pointer_angle - sector_angle / 2.0 - target_index * sector_angle


        # 交界线在 base_angle + i * sector_angle 处
        boundary_angles = [
            (base_angle + i * sector_angle) % 360.0
            for i in range(n)
        ]
        print("颜色分区交界线角度（度）:", [f"{a:.2f}" for a in boundary_angles])

        for i, label in enumerate(self.sectors):
            # 扇形填充（固定不转）
            path = QtGui.QPainterPath()
            path.moveTo(0, 0)
            start_angle = base_angle + i * sector_angle
            path.arcTo(
                -radius, -radius, 2 * radius, 2 * radius,
                -start_angle, -sector_angle
            )
            path.closeSubpath()

            # 
            # hue: 0 ~ 359 之间平均分布
            hue = int(360 * i / n)   # 第 i 个扇区的色相
            # sat / val 越大颜色越鲜艳，这里设置成比较柔和的值
            sat = 180   # 0~255，越大越纯
            val = 180   # 0~255，越大越亮
            color = QtGui.QColor.fromHsv(hue, sat, val)

            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawPath(path)


        # 外圈
        pen_circle = QtGui.QPen(QtGui.QColor(0, 0, 0), 5)
        painter.setPen(pen_circle)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QtCore.QPointF(0, 0), radius, radius)


        # 2. 画“旋转”的分割线
        painter.save()

        # 统一旋转坐标系，让所有线整体转动
        # painter.rotate(self.current_angle)

        pen_line = QtGui.QPen(QtGui.QColor(0, 0, 0), 3)
        painter.setPen(pen_line)

        line_angles = []

        for i in range(len(self.sectors)):
            angle_deg = base_angle + i * sector_angle + self.current_angle

            line_angles.append(angle_deg % 360.0)

            angle_rad = math.radians(angle_deg)
            x = radius * math.cos(-angle_rad)
            y = radius * math.sin(-angle_rad)
            painter.drawLine(
                QtCore.QPointF(0, 0),
                QtCore.QPointF(x, y)
            )

        print(
            f"当前旋转角度 self.current_angle = {self.current_angle:.2f}°，"
            "每条分割线角度（度）:",
            [f"{a:.2f}" for a in line_angles]
        )
        painter.restore()


        for i, label in enumerate(self.sectors):
            start_angle = base_angle + i * sector_angle
            mid_angle = start_angle + sector_angle / 2.0
            mid_angle_rad = math.radians(mid_angle)

            text_radius = radius * 0.6
            tx = text_radius * math.cos(-mid_angle_rad)
            ty = text_radius * math.sin(-mid_angle_rad)

            painter.save()
            painter.translate(tx, ty)

            # 调试：画一个小圆点，确认位置
            # painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            # painter.setPen(QtCore.Qt.PenStyle.NoPen)
            # painter.drawEllipse(QtCore.QPointF(0, 0), 3, 3)

            # 设置文字样式
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 5))  # 白字更明显
            font = painter.font()
            font.setPointSize(16)
            font.setBold(True)
            painter.setFont(font)

            painter.drawText(
                -20, -10, 40, 20,
                QtCore.Qt.AlignmentFlag.AlignCenter,
                label,
            )

            painter.restore()

        # ======================
        # 3. 指针（完全静止）
        # ======================
        painter.save()

        pointer_height = radius * 0.25
        pointer_width = radius * 0.15

        path = QtGui.QPainterPath()
        path.moveTo(0, -radius - pointer_height * 0.2)
        path.lineTo(-pointer_width / 2, -radius + pointer_height)
        path.lineTo(pointer_width / 2, -radius + pointer_height)
        path.closeSubpath()

        painter.setBrush(QtGui.QBrush(QtGui.QColor(200, 80, 80, 200)))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawPath(path)

        # 中心小圆点
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.drawEllipse(QtCore.QPointF(0, 0), radius * 0.03, radius * 0.03)

        painter.restore()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("不上早八")

        self.wheel = WheelWidget(self)

        btn = QtWidgets.QPushButton("开始转动")
        btn.setFixedHeight(40)
        btn.clicked.connect(self.wheel.start_spin)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addWidget(self.wheel, 1)
        layout.addWidget(btn, 0, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(central)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.resize(500, 550)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()