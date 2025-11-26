import math
from PyQt6 import QtCore, QtGui, QtWidgets


class WheelWidget(QtWidgets.QWidget):

    spinFinished = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 固定分区（扇形本身不会转动）
        self.sectors = ["去", "不去"]
        
        # 指针默认指向的选项（按文字来找）
        # 比如想默认指向 "C"，就写 "C"
        # 想默认指向第 0 个，就写 self.target_label = self.sectors[0]
        self.target_label = "去"

        self.title_text = "去不去早八？"


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

            # ⭐ 在这里发出转动结束信号，当前指针指向的就是 target_label
            result_label = self.target_label
            self.spinFinished.emit(result_label)

            # 回到初始位置
            self.current_angle = 0.0
            self.update()
    
    def _best_text_color_for(self, color: QtGui.QColor) -> QtGui.QColor:
        """根据背景色亮度自动选择黑字或白字"""
        r, g, b, _ = color.getRgb()
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        return QtGui.QColor(0, 0, 0) if luma > 140 else QtGui.QColor(255, 255, 255)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        rect = self.rect()
        w = rect.width()
        h = rect.height()
        if w <= 0 or h <= 0:
            return

        # ---- 动态计算 radius + 标题区域 ----
        margin = 10
        avail_w = max(10, w - 2 * margin)
        avail_h = max(10, h - 2 * margin)

        # 垂直方向约为：标题高度 + 直径 ≈ 2.4 * radius
        radius = min(avail_w / 2.0, avail_h / 2.4)
        if radius <= 0:
            return

        # 标题字体大小与 radius 成比例
        title_font_size = max(10, int(radius * 0.15))
        title_box_height = title_font_size * 1.0

        # 轮盘中心：水平居中，竖直在标题下面
        cx = w / 2.0
        extra_gap = radius * 0.12
        cy = margin + title_box_height + radius + extra_gap

        # ---- 标题：自动颜色 + 缩放 ----
        painter.save()

        bg_color = self.palette().window().color()
        title_color = self._best_text_color_for(bg_color)

        font = painter.font()
        font.setPointSize(title_font_size)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtGui.QPen(title_color))

        title_rect = QtCore.QRectF(
            margin,
            margin,
            w - 2 * margin,
            title_box_height,
        )
        painter.drawText(
            title_rect,
            QtCore.Qt.AlignmentFlag.AlignCenter,
            self.title_text,
        )
        painter.restore()

        # 从这里开始画转盘（下面原来的代码保持不变）
        painter.translate(cx, cy)

        # ======================
        # 1. 画“静止”的扇形区域
        # ======================
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


        # ======== 打印所有颜色分区交界线角度（静态）========
        # 交界线在 base_angle + i * sector_angle 处
        # boundary_angles = [
        #     (base_angle + i * sector_angle) % 360.0
        #     for i in range(n)
        # ]
        # print("颜色分区交界线角度（度）:", [f"{a:.2f}" for a in boundary_angles])

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

        # ======================
        # 2. 画“旋转”的分割线
        # ======================
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

        # print(
        #     f"当前旋转角度 self.current_angle = {self.current_angle:.2f}°，"
        #     "每条分割线角度（度）:",
        #     [f"{a:.2f}" for a in line_angles]
        # )
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