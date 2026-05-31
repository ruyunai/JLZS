try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QComboBox, QLineEdit, QPushButton, QGroupBox,
                                 QGridLayout, QMessageBox, QTabWidget, QWidget,
                                 QCheckBox, QSpinBox)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
except ImportError:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QComboBox, QLineEdit, QPushButton, QGroupBox,
                                   QGridLayout, QMessageBox, QTabWidget, QWidget,
                                   QCheckBox, QSpinBox)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

from utils import ConfigManager
from api import APIClientFactory

class ConfigWindow(QDialog):
    PROVIDERS = {
        'siliconflow': '硅基流动',
        'deepseek': 'DeepSeek',
        'zhipu': '智谱AI',
        'baidu': '百度千帆',
        'openai': 'OpenAI',
        'custom': '自定义'
    }

    MODELS = {
        'siliconflow': [
            'Qwen/Qwen2-VL-72B-Instruct',
            'Qwen/Qwen2.5-72B-Instruct',
            'Qwen/Qwen2.5-7B-Instruct',
            'deepseek-ai/DeepSeek-V2.5',
            'THUDM/GLM-4-9B-Chat'
        ],
        'deepseek': [
            'deepseek-chat',
            'deepseek-coder'
        ],
        'zhipu': [
            'glm-4',
            'glm-4-flash',
            'glm-4v'
        ],
        'baidu': [
            'ernie-4.0-8k',
            'ernie-3.5-8k'
        ],
        'openai': [
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4-turbo'
        ]
    }

    API_BASES = {
        'siliconflow': 'https://api.siliconflow.cn/v1',
        'deepseek': 'https://api.deepseek.com',
        'zhipu': 'https://open.bigmodel.cn/api/paas/v4',
        'baidu': 'https://qianfan.baidubce.com/v2'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.setWindowTitle("Agent API配置")
        self.setMinimumSize(700, 600)

        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        tabs.addTab(self.create_agent_tab('agent1_analyze', 'Agent 1 - 简历分析'), "Agent 1 分析")
        tabs.addTab(self.create_agent_tab('agent2_optimize', 'Agent 2 - 简历优化'), "Agent 2 优化")

        layout.addWidget(tabs)

        output_group = QGroupBox("输出设置")
        output_layout = QGridLayout()

        output_layout.addWidget(QLabel("输出目录:"), 0, 0)
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("留空使用默认目录（桌面）")
        output_layout.addWidget(self.output_dir, 0, 1)

        output_layout.addWidget(QLabel("命名模板:"), 1, 0)
        self.naming_template = QLineEdit()
        self.naming_template.setPlaceholderText("{name}_{position}_{date}")
        output_layout.addWidget(self.naming_template, 1, 1)

        self.auto_open_folder = QCheckBox("完成后自动打开输出文件夹")
        self.auto_open_folder.setChecked(True)
        output_layout.addWidget(self.auto_open_folder, 2, 0, 1, 2)

        self.show_preview = QCheckBox("完成后显示预览")
        self.show_preview.setChecked(True)
        output_layout.addWidget(self.show_preview, 3, 0, 1, 2)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("""
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

        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self.reset_config)

        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def create_agent_tab(self, agent_id: str, title: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox(title)
        grid = QGridLayout()

        grid.addWidget(QLabel("服务商:"), 0, 0)
        provider_combo = QComboBox()
        for key, value in self.PROVIDERS.items():
            provider_combo.addItem(value, key)
        provider_combo.currentIndexChanged.connect(
            lambda idx, combo=provider_combo, aid=agent_id: self.on_provider_changed(aid, combo)
        )
        grid.addWidget(provider_combo, 0, 1)

        grid.addWidget(QLabel("模型:"), 1, 0)
        model_combo = QComboBox()
        model_combo.setEditable(True)
        grid.addWidget(model_combo, 1, 1)

        grid.addWidget(QLabel("API地址:"), 2, 0)
        api_base_input = QLineEdit()
        grid.addWidget(api_base_input, 2, 1)

        grid.addWidget(QLabel("API Key:"), 3, 0)
        api_key_input = QLineEdit()
        api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(api_key_input, 3, 1)

        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(
            lambda _, aid=agent_id, p=provider_combo, m=model_combo,
                   a=api_base_input, k=api_key_input: self.test_connection(aid, p, m, a, k)
        )
        grid.addWidget(test_btn, 4, 1)

        group.setLayout(grid)
        layout.addWidget(group)

        self.agent_widgets = getattr(self, 'agent_widgets', {})
        self.agent_widgets[agent_id] = {
            'provider': provider_combo,
            'model': model_combo,
            'api_base': api_base_input,
            'api_key': api_key_input
        }

        return widget

    def on_provider_changed(self, agent_id: str, provider_combo: QComboBox):
        provider = provider_combo.currentData()
        if agent_id in self.agent_widgets:
            model_combo = self.agent_widgets[agent_id]['model']
            api_base = self.agent_widgets[agent_id]['api_base']

            model_combo.clear()
            if provider in self.MODELS:
                model_combo.addItems(self.MODELS[provider])

            if provider in self.API_BASES:
                api_base.setText(self.API_BASES[provider])

    def load_config(self):
        agents = self.config._config.get('agents', {})
        for agent_id, widgets in self.agent_widgets.items():
            if agent_id in agents:
                config = agents[agent_id]
                widgets['provider'].setCurrentIndex(
                    widgets['provider'].findData(config.get('provider', 'siliconflow'))
                )
                widgets['model'].setCurrentText(config.get('model', ''))
                widgets['api_base'].setText(config.get('api_base', ''))
                widgets['api_key'].setText(config.get('api_key', ''))

        output_config = self.config.get_output_config()
        self.output_dir.setText(output_config.get('directory', ''))
        self.naming_template.setText(output_config.get('naming_template', '{name}_{position}_{date}'))
        self.auto_open_folder.setChecked(output_config.get('auto_open_folder', True))
        self.show_preview.setChecked(output_config.get('show_preview', True))

    def save_config(self):
        agents_config = {}
        for agent_id, widgets in self.agent_widgets.items():
            agents_config[agent_id] = {
                'provider': widgets['provider'].currentData(),
                'model': widgets['model'].currentText(),
                'api_base': widgets['api_base'].text(),
                'api_key': widgets['api_key'].text()
            }

        self.config._config['agents'] = agents_config

        output_config = {
            'directory': self.output_dir.text(),
            'naming_template': self.naming_template.text(),
            'auto_open_folder': self.auto_open_folder.isChecked(),
            'show_preview': self.show_preview.isChecked()
        }
        self.config.update_output_config(output_config)

        QMessageBox.information(self, "成功", "配置已保存")
        self.accept()

    def reset_config(self):
        if QMessageBox.question(self, "确认", "确定要恢复默认配置吗？") == QMessageBox.StandardButton.Yes:
            self.config._config = self.config._get_default_config()
            self.config.save_config()
            self.load_config()
            QMessageBox.information(self, "成功", "已恢复默认配置")

    def test_connection(self, agent_id: str, provider_combo: QComboBox,
                       model_combo: QComboBox, api_base_input: QLineEdit,
                       api_key_input: QLineEdit):
        provider = provider_combo.currentData()
        api_key = api_key_input.text()
        api_base = api_base_input.text()
        model = model_combo.currentText()

        if not api_key:
            QMessageBox.warning(self, "提示", "请输入API Key")
            return

        try:
            result = APIClientFactory.test_connection(provider, api_key, api_base, model)
            if result['success']:
                QMessageBox.information(self, "成功", f"连接成功！\n\n可用模型: {', '.join(result['details'].get('models_available', [])[:3])}")
            else:
                QMessageBox.warning(self, "失败", result['message'])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试连接失败: {str(e)}")
