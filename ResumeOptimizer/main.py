import sys
import os
from pathlib import Path

def setup_environment():
    app_dir = Path(__file__).parent
    temp_dir = app_dir / 'temp'
    temp_dir.mkdir(exist_ok=True)

    if 'TEMP' not in os.environ or not os.environ.get('TEMP'):
        os.environ['TEMP'] = str(temp_dir)

    config_dir = Path(os.environ.get('APPDATA', '.')) / 'ResumeOptimizer'
    config_dir.mkdir(parents=True, exist_ok=True)

def main():
    setup_environment()

    # 尝试导入GUI框架
    qt_module = None
    QApplication = None
    ResumeOptimizerGUI = None

    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        qt_module = "PyQt6"
        print(f"[信息] 使用 {qt_module}")
    except ImportError:
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            qt_module = "PySide6"
            print(f"[信息] 使用 {qt_module}")
        except ImportError as e:
            print(f"[错误] 无法导入GUI框架: {e}")
            print("[错误] 请安装PyQt6或PySide6:")
            print("[错误] pip install PyQt6")
            print("[错误] 或 pip install PySide6")
            input("\n按Enter键退出...")
            sys.exit(1)

    try:
        from app import ResumeOptimizerGUI
    except ImportError as e:
        print(f"[错误] 无法导入应用模块: {e}")
        print("[提示] 可能是打包路径问题")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("简历优化助手")
    app.setOrganizationName("ResumeOptimizer")

    # PyQt6已经内置高DPI支持，不需要手动设置
    # PySide6需要时可以启用
    # if qt_module == "PySide6":
    #     app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    window = ResumeOptimizerGUI()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
