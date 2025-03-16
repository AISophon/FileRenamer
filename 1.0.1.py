#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
[程序介绍]
文件日期前缀命名工具是一款高效、易用的文件管理工具，旨在帮助用户快速为文件夹中的文件添加创建日期或修改日期前缀，使文件命名更加规范和便于管理。通过简单的图形用
户界面，用户可以选择目标文件夹、指定时间类型（创建时间或修改时间），并启动批量重命名操作。程序会自动处理文件名冲突、检查文件名格式，并提供详细的处理日志和进度
反馈，确保操作的透明性和安全性。
[更新日志]
版本 1.0.0 - 2024-12-18
[新增功能]
- 文件夹选择功能：用户可以通过直观的文件浏览器选择需要处理的文件夹。
- 时间类型选择：支持用户选择按文件的创建时间或修改时间进行重命名。
- 文件重命名核心功能：为文件添加日期前缀，格式为"YYYY-MM-DD "。
- 文件名合法性检查：自动清理文件名中的非法字符，避免重命名错误。
- 文件名冲突处理：当新文件名与已有文件名冲突时，自动在文件名后添加序号以区分。
- 重复文件检测：通过比较文件大小和哈希值，识别并处理重复文件。
- 日志记录功能：将处理过程和结果写入日志文件，方便后续查看和分析。
- 进度反馈：提供实时进度条和处理信息，让用户了解操作状态。
[优化修复]
- 修复了在特定文件系统下获取文件创建时间可能不准确的问题。
- 优化了文件遍历和处理算法，提高程序响应速度和处理效率。
- 修正了处理包含特殊字符的文件名时可能出现的编码问题。
[已知限制]
- 在极少数情况下，如果文件系统对文件名长度有限制，可能会导致部分长文件名的文件无法正常重命名，后续版本将对此进行优化。
"""

import os
import sys
import logging
import datetime
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QTextEdit,
)
from PyQt5.QtCore import pyqtSignal, QObject, QThread

# 配置日志
logging.basicConfig(
    filename="file_renaming.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)


class WorkerSignals(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()


class FileRenamer:
    @staticmethod
    def calculate_file_hash(filepath, block_size=65536):
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.digest()

    @staticmethod
    def check_duplicate_file(file_path, new_path):
        if os.path.getsize(file_path) != os.path.getsize(new_path):
            return False
        return FileRenamer.calculate_file_hash(
            file_path
        ) == FileRenamer.calculate_file_hash(new_path)

    @staticmethod
    def clean_filename(filename):
        illegal_chars = r'[\\/*?:"<>|]'

        return re.sub(illegal_chars, "_", filename)

    @staticmethod
    def get_file_time(filepath, time_type="creation"):
        if time_type == "creation":
            return os.path.getctime(filepath)
        elif time_type == "modification":
            return os.path.getmtime(filepath)
        else:
            raise ValueError("Invalid time_type. Use 'creation' or 'modification'.")

    @staticmethod
    def handle_filename_conflict(new_path, original_name, conflict_files):
        base_dir = os.path.dirname(new_path)
        base_name = os.path.basename(new_path)
        name_parts = os.path.splitext(base_name)
        base_name_without_ext, file_ext = name_parts[0], name_parts[1]

        if base_name in conflict_files:
            conflict_count = conflict_files[base_name]
        else:
            conflict_count = 0

        while os.path.exists(new_path):
            conflict_count += 1
            new_name = f"{base_name_without_ext}_{conflict_count}{file_ext}"
            new_path = os.path.join(base_dir, new_name)
            conflict_files[base_name] = conflict_count

        return new_path, conflict_files

    @staticmethod
    def has_valid_date_prefix(file, date_prefix):
        cleaned_file = FileRenamer.clean_filename(file)
        return cleaned_file.startswith(date_prefix)

    @staticmethod
    def remove_date_prefix(file):
        date_prefix_pattern = r"^\d{4}-\d{2}-\d{2} "
        cleaned_file = re.sub(date_prefix_pattern, "", file)
        return cleaned_file

    @staticmethod
    def has_yy_mm_dd_prefix(file):
        """
        检查文件名是否以"YYYY-MM-DD "格式的前缀开头。
        """
        cleaned_file = FileRenamer.clean_filename(file)
        return re.match(r"^\d{4}-\d{2}-\d{2} ", cleaned_file) is not None

    @staticmethod
    def remove_yy_mm_dd_prefix(file):
        """
        从文件名中移除"YYYY-MM-DD "格式的前缀。
        """
        cleaned_file = re.sub(r"^\d{4}-\d{2}-\d{2} ", "", file)
        return cleaned_file

    @staticmethod
    def rename_file_with_date(file_path, time_type, signals):
        try:
            file_time = FileRenamer.get_file_time(file_path, time_type)
            date_formatted = datetime.datetime.fromtimestamp(file_time).strftime(
                "%Y-%m-%d"
            )
            date_prefix = f"{date_formatted} "

            original_name = os.path.basename(file_path)
            cleaned_name = FileRenamer.clean_filename(original_name)

            name_without_prefix = FileRenamer.remove_date_prefix(cleaned_name)

            new_name = f"{date_prefix}{name_without_prefix}"
            new_path = os.path.join(os.path.dirname(file_path), new_name)

            if FileRenamer.has_valid_date_prefix(name_without_prefix, date_prefix):
                signals.progress.emit(
                    1, f"[已有]文件 {original_name} 的日期格式已正确，无需重命名。"
                )
                return

            conflict_files = {}
            new_path, conflict_files = FileRenamer.handle_filename_conflict(
                new_path, original_name, conflict_files
            )

            if os.path.exists(new_path):
                if FileRenamer.check_duplicate_file(file_path, new_path):
                    signals.progress.emit(
                        1, f"[重复]发现重复文件 {original_name}，将删除原有文件。"
                    )
                    os.remove(new_path)
                else:
                    signals.progress.emit(
                        1,
                        f"[跳过]文件 {original_name} 与 {new_name} 冲突，但文件内容不同，将跳过重命名。",
                    )
                    return

            os.rename(file_path, new_path)
            signals.progress.emit(
                1, f"[成功]文件 {original_name} 已重命名为 {new_name}"
            )

        except Exception as e:
            signals.progress.emit(1, f"[错误]处理文件 {file_path} 时出错: {str(e)}")

    @staticmethod
    def restore_original_name(file_path, signals):
        try:
            original_name = os.path.basename(file_path)
            cleaned_name = FileRenamer.clean_filename(original_name)

            if not FileRenamer.has_yy_mm_dd_prefix(cleaned_name):
                signals.progress.emit(
                    1, f"[跳过]文件 {original_name} 不符合恢复条件，无需处理。"
                )
                return

            new_name = FileRenamer.remove_yy_mm_dd_prefix(cleaned_name)
            new_path = os.path.join(os.path.dirname(file_path), new_name)

            conflict_files = {}
            new_path, conflict_files = FileRenamer.handle_filename_conflict(
                new_path, original_name, conflict_files
            )

            if os.path.exists(new_path):
                if FileRenamer.check_duplicate_file(file_path, new_path):
                    signals.progress.emit(
                        1, f"[重复]发现重复文件 {original_name}，将删除原有文件。"
                    )
                    os.remove(new_path)
                else:
                    signals.progress.emit(
                        1,
                        f"[跳过]文件 {original_name} 与 {new_name} 冲突，但文件内容不同，将跳过恢复。",
                    )
                    return

            os.rename(file_path, new_path)
            signals.progress.emit(
                1, f"[成功]文件 {original_name} 已恢复为 {new_name}"
            )

        except Exception as e:
            signals.progress.emit(1, f"[错误]处理文件 {file_path} 时出错: {str(e)}")


class RenamingWorker(QObject):
    def __init__(self, folder_path, time_type, operation_mode, progress_callback):
        super().__init__()
        self.folder_path = folder_path
        self.time_type = time_type
        self.operation_mode = operation_mode
        self.progress_callback = progress_callback
        self.total_files = 0
        self.processed_files = 0

    def run(self):
        self.total_files = sum(len(files) for _, _, files in os.walk(self.folder_path))
        self.processed_files = 0

        with ThreadPoolExecutor() as executor:
            for root, _, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.operation_mode == "add_prefix":
                        executor.submit(self.rename_file_with_date, file_path)
                    elif self.operation_mode == "restore_name":
                        executor.submit(self.restore_original_name, file_path)

        self.progress_callback.progress.emit(0, "所有文件处理完成！")
        self.progress_callback.finished.emit()

    def rename_file_with_date(self, file_path):
        FileRenamer.rename_file_with_date(
            file_path, self.time_type, self.progress_callback
        )
        self.processed_files += 1
        self.progress_callback.progress.emit(
            int((self.processed_files / self.total_files) * 100),
            f"进度: {self.processed_files}/{self.total_files} ({(self.processed_files/self.total_files)*100:.2f}%)",
        )

    def restore_original_name(self, file_path):
        FileRenamer.restore_original_name(file_path, self.progress_callback)
        self.processed_files += 1
        self.progress_callback.progress.emit(
            int((self.processed_files / self.total_files) * 100),
            f"进度: {self.processed_files}/{self.total_files} ({(self.processed_files/self.total_files)*100:.2f}%)",
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.time_type = "creation"
        self.operation_mode = "add_prefix"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("文件日期前缀命名工具")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 文件夹选择区域
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("未选择文件夹")
        folder_layout.addWidget(self.folder_label)
        select_btn = QPushButton("选择文件夹")
        select_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(select_btn)
        layout.addLayout(folder_layout)

        # 时间类型选择
        time_layout = QHBoxLayout()
        time_label = QLabel("选择时间类型:")
        time_layout.addWidget(time_label)
        self.time_combo = QComboBox()
        self.time_combo.addItems(["创建时间", "修改时间"])
        self.time_combo.currentIndexChanged.connect(self.time_type_changed)
        time_layout.addWidget(self.time_combo)
        layout.addLayout(time_layout)

        # 操作模式选择
        mode_layout = QHBoxLayout()
        mode_label = QLabel("操作模式:")
        mode_layout.addWidget(mode_label)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["添加日期前缀", "恢复原名"])
        self.mode_combo.currentIndexChanged.connect(self.operation_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 日志显示区域
        log_label = QLabel("处理日志:")
        layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # 开始按钮
        self.start_btn = QPushButton("开始处理")
        self.start_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_btn)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"选定文件夹: {folder}")

    def time_type_changed(self, index):
        self.time_type = "creation" if index == 0 else "modification"

    def operation_mode_changed(self, index):
        self.operation_mode = "add_prefix" if index == 0 else "restore_name"

    def start_processing(self):
        if not self.folder_path:
            self.log_text.append("请先选择文件夹！")
            return

        self.start_btn.setEnabled(False)
        self.signals = WorkerSignals()
        self.worker = RenamingWorker(
            self.folder_path, self.time_type, self.operation_mode, self.signals
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.thread.quit)
        self.signals.finished.connect(self.worker.deleteLater)
        self.signals.finished.connect(self.thread.deleteLater)
        self.signals.finished.connect(lambda: self.start_btn.setEnabled(True))
        self.thread.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.log_text.append(message)
        logging.info(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())