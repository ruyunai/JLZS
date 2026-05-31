try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QTextEdit, QPushButton, QFileDialog, QMessageBox)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
except ImportError:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QTextEdit, QPushButton, QFileDialog, QMessageBox)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

class MarkdownInputWindow(QDialog):
    TEMPLATE = """# 基本信息
姓名:
手机:
邮箱:
学历:

# 求职意向
行业:
岗位:
薪资:

# 工作经历
## 公司名称 | 职位 | 2022.01 - 2024.01
- 负责xxx工作
- 完成了xxx项目
- 取得了xxx成果

# 项目经验
## 项目名称
- 项目描述:
- 技术栈:
- 个人职责:

# 技能证书
- 技能1, 技能2, 技能3
- 证书1, 证书2

# 自我评价
"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("简历信息输入 - Markdown格式")
        self.setMinimumSize(700, 600)

        layout = QVBoxLayout(self)

        label = QLabel("请在下方输入您的简历内容（Markdown格式）")
        label.setStyleSheet("color: #333; font-size: 14px;")
        layout.addWidget(label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在此输入Markdown格式的简历...")
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(11)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()

        import_btn = QPushButton("📂 从文件导入")
        import_btn.clicked.connect(self.import_file)

        template_btn = QPushButton("📝 使用模板")
        template_btn.clicked.connect(self.use_template)

        verify_btn = QPushButton("✓ 验证格式")
        verify_btn.clicked.connect(self.verify_format)

        button_layout.addWidget(import_btn)
        button_layout.addWidget(template_btn)
        button_layout.addWidget(verify_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton("确认输入")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_btn.clicked.connect(self.confirm_input)
        action_layout.addWidget(confirm_btn)

        layout.addLayout(action_layout)

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Markdown文件",
            "",
            "Markdown文件 (*.md *.txt);;所有文件 (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_edit.setText(content)
                QMessageBox.information(self, "成功", "文件已导入")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导入失败: {str(e)}")

    def use_template(self):
        if QMessageBox.question(
            self, "确认",
            "确定要使用模板吗？这将替换当前内容。"
        ) == QMessageBox.StandardButton.Yes:
            self.text_edit.setText(self.TEMPLATE)

    def verify_format(self):
        content = self.text_edit.toPlainText()

        required_sections = ['基本信息', '求职意向', '工作经历', '技能证书']
        missing_sections = []

        for section in required_sections:
            if f'# {section}' not in content and f'#{section}' not in content:
                missing_sections.append(section)

        if missing_sections:
            QMessageBox.warning(
                self, "格式提示",
                f"建议包含以下部分:\n{', '.join(missing_sections)}\n\n但仍可以继续使用。"
            )
        else:
            QMessageBox.information(self, "格式检查", "✓ 格式检查通过！")

    def confirm_input(self):
        content = self.text_edit.toPlainText().strip()

        if not content:
            QMessageBox.warning(self, "提示", "请输入简历内容")
            return

        if len(content) < 50:
            QMessageBox.warning(self, "提示", "内容过短，请确认是否正确输入")

        self.accept()

    def get_markdown(self) -> str:
        return self.text_edit.toPlainText()
