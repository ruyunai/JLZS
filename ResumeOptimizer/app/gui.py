try:
    from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                 QPushButton, QLabel, QFileDialog, QLineEdit,
                                 QTextEdit, QComboBox, QProgressBar, QGroupBox,
                                 QMessageBox, QScrollArea, QFrame, QCheckBox,
                                 QSpinBox, QDialog, QDialogButtonBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
    QT_AVAILABLE = "PyQt6"
except ImportError:
    try:
        from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                                       QPushButton, QLabel, QFileDialog, QLineEdit,
                                       QTextEdit, QComboBox, QProgressBar, QGroupBox,
                                       QMessageBox, QScrollArea, QFrame, QCheckBox,
                                       QSpinBox, QDialog, QDialogButtonBox)
        from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal
        from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
        QT_AVAILABLE = "PySide6"
    except ImportError:
        raise ImportError("未找到PyQt6或PySide6，请先安装：pip install PyQt6")

import os
import re
from pathlib import Path
from datetime import datetime
from agents import ResumeWorkflow, Agent1Analyze, Agent2Optimize
from utils import DocxGenerator, ConfigManager
from app.config_window import ConfigWindow
from app.markdown_input import MarkdownInputWindow
from app.preview_window import PreviewWindow

class OptimizationThread(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str, dict)

    def __init__(self, resume_data, user_intent):
        super().__init__()
        self.resume_data = resume_data
        self.user_intent = user_intent

    def run(self):
        try:
            self.progress_signal.emit(30, "Agent 1: 分析简历与行业信息...")

            agent1 = Agent1Analyze()
            agent2 = Agent2Optimize()

            workflow = ResumeWorkflow(agent1, agent2)
            result = workflow.run(self.resume_data, self.user_intent)

            if not result or not result.get('personal_info'):
                raise Exception("简历优化失败：未获取到有效结果")

            self.progress_signal.emit(90, "生成文档...")
            self.finished_signal.emit(True, "", result)

        except Exception as e:
            self.progress_signal.emit(0, f"错误: {str(e)}")
            self.finished_signal.emit(False, str(e), {})

class ResumeOptimizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.current_file = None
        self.markdown_text = None
        self.optimization_thread = None
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.setWindowTitle(f"简历优化助手 v1.0 ({QT_AVAILABLE})")
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("简历优化助手")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        file_upload_group = QGroupBox("第一步：上传简历")
        file_layout = QVBoxLayout()

        self.drop_label = QLabel("拖拽简历文件到此处\n或点击\"上传简历\"按钮")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                background-color: #f5f5f5;
            }
        """)
        self.drop_label.setMinimumHeight(150)

        upload_btn = QPushButton("上传简历 (PDF/Word)")
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setMinimumHeight(40)

        manual_input_btn = QPushButton("手动输入简历 (Markdown)")
        manual_input_btn.clicked.connect(self.open_markdown_input)
        manual_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        file_layout.addWidget(self.drop_label)
        file_layout.addWidget(upload_btn)
        file_layout.addWidget(manual_input_btn)
        file_upload_group.setLayout(file_layout)
        layout.addWidget(file_upload_group)

        intent_group = QGroupBox("第二步：补充信息（可选）")
        intent_layout = QGridLayout()

        intent_layout.addWidget(QLabel("意向行业:"), 0, 0)
        self.industry_combo = QComboBox()
        self.industry_combo.addItems([
            "互联网/软件", "金融/银行", "教育培训", "医疗健康",
            "制造业", "房地产", "零售/电商", "咨询/专业服务",
            "媒体/文化", "政府/非营利", "其他"
        ])
        self.industry_combo.setEditable(True)
        intent_layout.addWidget(self.industry_combo, 0, 1)

        intent_layout.addWidget(QLabel("意向岗位:"), 1, 0)
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("例如：Python开发工程师")
        intent_layout.addWidget(self.position_input, 1, 1)

        intent_layout.addWidget(QLabel("期望薪资:"), 2, 0)
        salary_layout = QHBoxLayout()
        self.salary_min = QLineEdit()
        self.salary_min.setPlaceholderText("最低")
        self.salary_max = QLineEdit()
        self.salary_max.setPlaceholderText("最高")
        salary_layout.addWidget(self.salary_min)
        salary_layout.addWidget(QLabel("-"))
        salary_layout.addWidget(self.salary_max)
        intent_layout.addLayout(salary_layout, 2, 1)

        intent_layout.addWidget(QLabel("其他要求:"), 3, 0)
        self.other_requirements = QTextEdit()
        self.other_requirements.setMaximumHeight(80)
        self.other_requirements.setPlaceholderText("任何其他要求或备注...")
        intent_layout.addWidget(self.other_requirements, 3, 1)

        intent_group.setLayout(intent_layout)
        layout.addWidget(intent_group)

        button_layout = QHBoxLayout()
        self.optimize_btn = QPushButton("开始优化简历")
        self.optimize_btn.clicked.connect(self.start_optimization)
        self.optimize_btn.setMinimumHeight(50)
        self.optimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.optimize_btn)

        config_btn = QPushButton("⚙️ Agent配置")
        config_btn.clicked.connect(self.open_config)
        config_btn.setMinimumHeight(50)
        button_layout.addWidget(config_btn)

        layout.addLayout(button_layout)

        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_label = QLabel("就绪")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = event.mimeData().urls()
        if files:
            file_path = files[0].toLocalFile()
            self.load_file(file_path)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择简历文件",
            "",
            "简历文件 (*.pdf *.docx);;所有文件 (*.*)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "文件不存在")
            return

        self.current_file = file_path
        file_name = os.path.basename(file_path)
        self.drop_label.setText(f"已选择文件: {file_name}\n{file_path}")
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 40px;
                background-color: #e8f5e9;
                color: #2e7d32;
            }
        """)

    def open_markdown_input(self):
        dialog = MarkdownInputWindow(self)
        if dialog.exec():
            self.markdown_text = dialog.get_markdown()
            self.drop_label.setText(f"已通过Markdown输入简历\n共 {len(self.markdown_text)} 字符")
            self.drop_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    padding: 40px;
                    background-color: #e8f5e9;
                    color: #2e7d32;
                }
            """)
            self.current_file = None

    def open_config(self):
        dialog = ConfigWindow(self)
        dialog.exec()

    def get_user_intent(self) -> dict:
        return {
            "industry": self.industry_combo.currentText(),
            "position": self.position_input.text(),
            "salary_min": self.salary_min.text(),
            "salary_max": self.salary_max.text(),
            "other": self.other_requirements.toPlainText()
        }

    def start_optimization(self):
        if not self.current_file and not self.markdown_text:
            QMessageBox.warning(self, "提示", "请先上传简历文件或手动输入简历")
            return

        self.optimize_btn.setEnabled(False)
        self.progress_bar.setValue(10)
        self.progress_label.setText("初始化中...")

        try:
            resume_data = {}
            if self.current_file:
                resume_data['file_path'] = self.current_file
            elif self.markdown_text:
                resume_data['markdown_text'] = self.markdown_text

            user_intent = self.get_user_intent()

            self.progress_bar.setValue(20)
            self.progress_label.setText("准备中...")

            self.optimization_thread = OptimizationThread(resume_data, user_intent)
            self.optimization_thread.progress_signal.connect(self.on_progress)
            self.optimization_thread.finished_signal.connect(self.on_finished)
            self.optimization_thread.start()

        except Exception as e:
            self.progress_label.setText(f"错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"优化失败: {str(e)}")
            self.optimize_btn.setEnabled(True)

    def on_progress(self, value: int, message: str):
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)

    def on_finished(self, success: bool, error: str, optimized_resume: dict):
        if success:
            try:
                user_intent = self.get_user_intent()
                output_path = self.generate_output_path(optimized_resume, user_intent)
                DocxGenerator.generate(optimized_resume, output_path)

                self.progress_bar.setValue(100)
                self.progress_label.setText(f"完成！文件已保存到:\n{output_path}")

                self.show_preview(output_path, optimized_resume)

                QMessageBox.information(self, "成功", f"简历优化完成！\n\n文件已保存到:\n{output_path}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"生成文档失败: {str(e)}")
        else:
            self.progress_label.setText(f"错误: {error}")
            QMessageBox.critical(self, "错误", f"优化失败: {error}")

        self.optimize_btn.setEnabled(True)

    def generate_output_path(self, resume_data: dict, user_intent: dict) -> str:
        output_config = self.config.get_output_config()
        output_dir = output_config.get('directory', '')

        if not output_dir:
            desktop = Path(os.environ.get('USERPROFILE', '.')) / 'Desktop'
            output_dir = desktop / '简历优化输出'
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        name = resume_data.get('personal_info', {}).get('姓名', '未命名')
        position = user_intent.get('position', '未知岗位').replace(' ', '_')
        date = datetime.now().strftime('%Y%m%d')

        template = output_config.get('naming_template', '{name}_{position}_{date}')
        filename = template.format(
            name=name,
            position=position,
            date=date,
            industry=user_intent.get('industry', '')
        )
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        output_path = output_dir / f"{filename}.docx"

        counter = 1
        while output_path.exists():
            output_path = output_dir / f"{filename}_{counter}.docx"
            counter += 1

        return str(output_path)

    def show_preview(self, file_path: str, resume_data: dict):
        output_config = self.config.get_output_config()
        if output_config.get('show_preview', True):
            preview = PreviewWindow(file_path, resume_data, self)
            preview.exec()

    def load_config(self):
        pass
