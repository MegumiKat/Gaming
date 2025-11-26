# sidebar_widget.py
from PyQt6 import QtCore, QtWidgets


class SidebarWidget(QtWidgets.QWidget):
    """
    左侧可缩略侧边栏：
    - 每个 sector 一个输入框
    - 应用时只允许偶数个 sector
    """
    settingsApplied = QtCore.pyqtSignal(list, str, str, str)

    def __init__(self, initial_sectors, initial_target, initial_title, initial_wheel_title, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(220)

        lbl_sectors_title = QtWidgets.QLabel("转盘元素（每个一个输入框）:")

        self.form_sectors = QtWidgets.QFormLayout()
        self.sector_edits = []

        for s in initial_sectors:
            self.add_sector_input(s)

        btn_add = QtWidgets.QPushButton("添加一个 sector")
        btn_remove = QtWidgets.QPushButton("删除最后一个")
        btn_add.clicked.connect(self.add_sector_input)
        btn_remove.clicked.connect(self.remove_sector_input)

        buttons_sectors = QtWidgets.QHBoxLayout()
        buttons_sectors.addWidget(btn_add)
        buttons_sectors.addWidget(btn_remove)

        lbl_target = QtWidgets.QLabel("默认指向的元素（target_label）:")
        self.edit_target = QtWidgets.QLineEdit(initial_target)

        lbl_title = QtWidgets.QLabel("窗口标题：")
        self.edit_title = QtWidgets.QLineEdit(initial_title)

        lbl_wheel_title = QtWidgets.QLabel("转盘标题（上方显示）：")
        self.edit_wheel_title = QtWidgets.QLineEdit(initial_wheel_title)

        self.btn_apply = QtWidgets.QPushButton("应用设置")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(lbl_sectors_title)
        layout.addLayout(self.form_sectors)
        layout.addLayout(buttons_sectors)
        layout.addSpacing(10)
        layout.addWidget(lbl_target)
        layout.addWidget(self.edit_target)
        layout.addWidget(lbl_title)
        layout.addWidget(self.edit_title)
        layout.addWidget(lbl_wheel_title)
        layout.addWidget(self.edit_wheel_title)
        layout.addWidget(self.btn_apply)
        layout.addStretch()

        self.btn_apply.clicked.connect(self.on_apply_clicked)

    def add_sector_input(self, text: str = ""):
        """
        - 初始化时传进来的 s 是 str -> 加 1 个
        - 按钮 clicked 传进来的是 bool -> 把它当成 ""，并一次加 2 个
        """
        # 如果是按钮 clicked 传来的 True/False，就认为是“点击事件”
        if isinstance(text, bool):
            text = ""
            times = 2      # 点击按钮：加两个
        else:
            times = 1      # 初始化时：每个 initial_sectors 加一个

        for _ in range(times):
            edit = QtWidgets.QLineEdit(text)
            label = QtWidgets.QLabel(f"Sector {len(self.sector_edits) + 1}:")
            self.form_sectors.addRow(label, edit)
            self.sector_edits.append(edit)
            # 后面再加的都默认空即可
            text = ""

    def remove_sector_input(self, arg=False):
        """
        - 每次尽量删除 2 个
        - 但必须保证删完后至少还剩 2 个
        """
        count = len(self.sector_edits)
        if count <= 2:
            QtWidgets.QMessageBox.warning(
                self,
                "不能再删了",
                "至少需要保留 2 个扇区。",
            )
            return

        # 最多可以删多少个，才能保证还剩 2 个
        removable = count - 2
        remove_count = min(2, removable)

        for _ in range(remove_count):
            index = len(self.sector_edits) - 1
            self.sector_edits.pop()
            self.form_sectors.removeRow(index)

    def on_apply_clicked(self):
        sectors = [e.text().strip() for e in self.sector_edits if e.text().strip()]

        if len(sectors) < 2:
            QtWidgets.QMessageBox.warning(
                self, "扇区数量不足", "至少需要 2 个扇区。"
            )
            return

        if len(sectors) % 2 != 0:
            QtWidgets.QMessageBox.warning(
                self,
                "扇区数量错误",
                f"扇区数量必须为偶数，目前为 {len(sectors)}，请再增减一个。",
            )
            return

        target = self.edit_target.text().strip()
        title = self.edit_title.text().strip()
        wheel_title = self.edit_wheel_title.text().strip()

        if target and target not in sectors:
            reply = QtWidgets.QMessageBox.question(
                self,
                "目标元素不在扇区中",
                f"当前 target_label = '{target}' 不在扇区列表中，仍然继续吗？",
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return

        self.settingsApplied.emit(sectors, target, title)