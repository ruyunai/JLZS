try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QTextEdit, QPushButton, QFileDialog)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
except ImportError:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QTextEdit, QPushButton, QFileDialog)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

import os
import subprocess
import shutil

class PreviewWindow(QDialog):
    def __init__(self, file_path: str, resume_data: dict, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.resume_data = resume_data
        self.setup_ui()
        self.load_preview()

    def setup_ui(self):
        self.setWindowTitle("简历预览")
        self.setMinimumSize(800, 700)

        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        self.file_label = QLabel(f"文件: {os.path.basename(self.file_path)}")
        self.file_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(self.file_label)
        header_layout.addStretch()

        size = os.path.getsize(self.file_path)
        size_label = QLabel(f"大小: {size / 1024:.1f} KB")
        size_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(size_label)

        layout.addLayout(header_layout)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        self.preview_text.setFont(font)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
            }
        """)
        layout.addWidget(self.preview_text)

        button_layout = QHBoxLayout()

        open_folder_btn = QPushButton("📂 打开文件夹")
        open_folder_btn.clicked.connect(self.open_folder)

        re_save_btn = QPushButton("💾 另存为...")
        re_save_btn.clicked.connect(self.save_as)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(open_folder_btn)
        button_layout.addWidget(re_save_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_preview(self):
        preview_content = self._generate_preview_text()
        self.preview_text.setText(preview_content)

    def _generate_preview_text(self) -> str:
        lines = []
        resume = self.resume_data

        lines.append("=" * 50)
        lines.append("简历预览")
        lines.append("=" * 50)
        lines.append("")

        if 'personal_info' in resume:
            lines.append("【基本信息】")
            for key, value in resume['personal_info'].items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        if 'intent' in resume and resume['intent']:
            lines.append("【求职意向】")
            for key, value in resume['intent'].items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        if 'education' in resume and resume['education']:
            lines.append("【教育背景】")
            for edu in resume['education']:
                if isinstance(edu, dict):
                    lines.append(f"  - {edu.get('description', '')}")
                else:
                    lines.append(f"  - {edu}")
            lines.append("")

        if 'experience' in resume and resume['experience']:
            lines.append("【工作经历】")
            for exp in resume['experience']:
                if isinstance(exp, dict):
                    lines.append(f"  {exp.get('company', '')} | {exp.get('position', '')} | {exp.get('period', '')}")
                    desc = exp.get('description', '')
                    for line in desc.split('\n'):
                        if line.strip():
                            lines.append(f"    {line.strip()}")
                else:
                    lines.append(f"  - {exp}")
            lines.append("")

        if 'projects' in resume and resume['projects']:
            lines.append("【项目经验】")
            for proj in resume['projects']:
                if isinstance(proj, dict):
                    lines.append(f"  {proj.get('name', proj.get('description', ''))}")
                    desc = proj.get('description', '')
                    for line in desc.split('\n'):
                        if line.strip():
                            lines.append(f"    {line.strip()}")
                else:
                    lines.append(f"  - {proj}")
            lines.append("")

        if 'skills' in resume and resume['skills']:
            lines.append("【技能证书】")
            if isinstance(resume['skills'], list):
                for skill in resume['skills']:
                    lines.append(f"  - {skill}")
            else:
                lines.append(f"  {resume['skills']}")
            lines.append("")

        if 'summary' in resume and resume['summary']:
            lines.append("【自我评价】")
            lines.append(f"  {resume['summary']}")

        lines.append("")
        lines.append("=" * 50)
        lines.append(f"完整文件: {self.file_path}")
        lines.append("=" * 50)

        return '\n'.join(lines)

    def open_folder(self):
        folder = os.path.dirname(self.file_path)
        if folder:
            subprocess.Popen(f'explorer /select,"{self.file_path}"')

    def save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            self.file_path,
            "Word文档 (*.docx)"
        )
        if file_path:
            try:
                shutil.copy2(self.file_path, file_path)
                self.file_path = file_path
                self.file_label.setText(f"文件: {os.path.basename(file_path)}")
                QMessageBox = None
                try:
                    from PyQt6.QtWidgets import QMessageBox
                except ImportError:
                    from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "成功", f"文件已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox = None
                try:
                    from PyQt6.QtWidgets import QMessageBox
                except ImportError:
                    from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")
