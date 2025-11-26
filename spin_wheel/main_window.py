# main_window.py
from PyQt6 import QtWidgets, QtCore
from wheel_widget import WheelWidget
from sidebar_widget import SidebarWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("不上早八")

        # ---- wheel ----
        self.wheel = WheelWidget(self)

        self.wheel.spinFinished.connect(self.on_spin_finished)

        # ---- side bar (as the main part in window )----
        # 注意这里不再传 parent，让它之后挂在 QDialog 上
        self.sidebar = SidebarWidget(
            self.wheel.sectors,
            self.wheel.target_label,
            self.windowTitle(),
            self.wheel.title_text,
            self,
        )
        self.sidebar.settingsApplied.connect(self.apply_sidebar_settings)

        # ---- 设置弹窗 ----
        self.sidebar_dialog = QtWidgets.QDialog(self)
        self.sidebar_dialog.setWindowTitle("转盘设置")
        dlg_layout = QtWidgets.QVBoxLayout(self.sidebar_dialog)
        dlg_layout.setContentsMargins(8, 8, 8, 8)
        dlg_layout.addWidget(self.sidebar)
        self.sidebar_dialog.resize(300, 400)

        # ---- wheel + button ----
        btn_start = QtWidgets.QPushButton("开始转动")
        btn_start.setFixedHeight(40)
        btn_start.clicked.connect(self.wheel.start_spin)

        btn_settings = QtWidgets.QPushButton("打开设置")
        btn_settings.setFixedHeight(40)
        btn_settings.clicked.connect(self.open_sidebar_dialog)

        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.addWidget(self.wheel, 1)

        # button : horizontal + middle
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_start)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_settings)
        buttons_layout.addStretch()

        right_layout.addLayout(buttons_layout)

        # use right side as central widget（dont use QSplitter）
        self.setCentralWidget(right)

    def apply_sidebar_settings(self, sectors, target_label, title, wheel_title):
        if sectors:
            self.wheel.sectors = sectors
        if target_label:
            self.wheel.target_label = target_label
        if title:
            self.setWindowTitle(title)
        if wheel_title:
            self.wheel.title_text = wheel_title 
        self.wheel.update()

    def open_sidebar_dialog(self):
        """打开设置弹窗"""
        # let the window appear in the middle of mai window
        self.sidebar_dialog.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        self.sidebar_dialog.show()
        self.sidebar_dialog.raise_()
        self.sidebar_dialog.activateWindow()

    def on_spin_finished(self, label: str):
        QtWidgets.QMessageBox.critical(
            self,
            "结果",
            f"指针指向：{label}",
        )