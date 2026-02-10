from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from .collector import PublicCollector
from .llm import DEFAULT_CRITERIA, DEFAULT_MODEL, score_with_llm
from .models import CompanyResult
from .reports import ReportWriter
from .storage import CacheStore


APP_DIR = Path.home() / ".itpark_scoring"
DB_PATH = APP_DIR / "cache.db"
OUTPUT_DIR = APP_DIR / "reports"


@dataclass
class ResolvedCompany:
    name: str
    website: Optional[str]


class CriteriaDialog(QtWidgets.QDialog):
    def __init__(self, criteria: list, selected_ids: set[str], parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("criteria settings")
        self.setMinimumSize(560, 520)
        self.criteria = criteria
        self.selected_ids = set(selected_ids)
        self.category_items: Dict[str, tuple[QtWidgets.QTreeWidgetItem, int]] = {}

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        note = QtWidgets.QLabel("Select the criteria you want to include in scoring.")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setUniformRowHeights(True)
        layout.addWidget(self.tree, 1)

        self.count_label = QtWidgets.QLabel("")
        layout.addWidget(self.count_label)

        button_row = QtWidgets.QHBoxLayout()
        self.select_all_button = QtWidgets.QPushButton("select all")
        self.clear_all_button = QtWidgets.QPushButton("clear all")
        self.save_button = QtWidgets.QPushButton("save")
        self.cancel_button = QtWidgets.QPushButton("cancel")
        button_row.addWidget(self.select_all_button)
        button_row.addWidget(self.clear_all_button)
        button_row.addStretch(1)
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.select_all_button.clicked.connect(self._select_all)
        self.clear_all_button.clicked.connect(self._clear_all)
        self.tree.itemChanged.connect(self._handle_item_change)

        self._populate()
        self._update_count()

    def _populate(self) -> None:
        self.tree.blockSignals(True)
        self.tree.clear()
        categories: Dict[str, list] = {}
        for item in self.criteria:
            categories.setdefault(item["category"], []).append(item)

        for category, items in categories.items():
            parent = QtWidgets.QTreeWidgetItem([category])
            parent.setFlags(parent.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            parent.setCheckState(0, QtCore.Qt.Checked)
            self.tree.addTopLevelItem(parent)
            self.category_items[category] = (parent, len(items))

            for criterion in items:
                child = QtWidgets.QTreeWidgetItem([criterion["name"]])
                child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                child.setData(0, QtCore.Qt.UserRole, criterion["id"])
                child.setCheckState(
                    0, QtCore.Qt.Checked if criterion["id"] in self.selected_ids else QtCore.Qt.Unchecked
                )
                parent.addChild(child)

        self.tree.expandAll()
        self.tree.blockSignals(False)
        self._update_count()

    def _select_all(self) -> None:
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            for j in range(category_item.childCount()):
                category_item.child(j).setCheckState(0, QtCore.Qt.Checked)

    def _clear_all(self) -> None:
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            for j in range(category_item.childCount()):
                category_item.child(j).setCheckState(0, QtCore.Qt.Unchecked)

    def _handle_item_change(self, item: QtWidgets.QTreeWidgetItem, _: int) -> None:
        self.tree.blockSignals(True)
        if item.childCount() > 0:
            state = item.checkState(0)
            if state in (QtCore.Qt.Checked, QtCore.Qt.Unchecked):
                for i in range(item.childCount()):
                    item.child(i).setCheckState(0, state)
        else:
            parent = item.parent()
            if parent is not None:
                total = parent.childCount()
                checked = 0
                for i in range(total):
                    if parent.child(i).checkState(0) == QtCore.Qt.Checked:
                        checked += 1
                if checked == 0:
                    parent.setCheckState(0, QtCore.Qt.Unchecked)
                elif checked == total:
                    parent.setCheckState(0, QtCore.Qt.Checked)
                else:
                    parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
        self.tree.blockSignals(False)
        self._update_count()

    def _update_count(self) -> None:
        selected_ids = self.get_selected_ids()
        self.count_label.setText(f"{len(selected_ids)} selected")
        for category, (item, total) in self.category_items.items():
            selected = 0
            for i in range(item.childCount()):
                if item.child(i).checkState(0) == QtCore.Qt.Checked:
                    selected += 1
            item.setText(0, f"{category} ({selected}/{total})")

    def get_selected_ids(self) -> set[str]:
        selected = set()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            for j in range(category_item.childCount()):
                child = category_item.child(j)
                if child.checkState(0) == QtCore.Qt.Checked:
                    criterion_id = child.data(0, QtCore.Qt.UserRole)
                    if criterion_id:
                        selected.add(str(criterion_id))
        return selected


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("IT Park company scoring")
        self.setMinimumSize(980, 680)

        self.cache = CacheStore(DB_PATH)
        self.collector = PublicCollector(self.cache)
        self.reporter = ReportWriter(OUTPUT_DIR)
        self.criteria_by_id = {}
        self.selected_criteria_ids = {item["id"] for item in DEFAULT_CRITERIA}

        self._build_ui()
        self._apply_style()
        self._update_actions()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background: #ffffff; color: #000000; }
            QGroupBox { border: 1px solid #000000; border-radius: 8px; margin-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLineEdit, QTextEdit, QTreeWidget {
                border: 1px solid #000000;
                border-radius: 6px;
                padding: 6px;
                background: #ffffff;
                selection-background-color: #000000;
                selection-color: #ffffff;
            }
            QPushButton {
                border: 1px solid #000000;
                border-radius: 8px;
                padding: 6px 12px;
                background: #ffffff;
            }
            QPushButton:hover { background: #f2f2f2; }
            QPushButton:pressed { background: #e6e6e6; }
            QStatusBar { background: #ffffff; color: #000000; border-top: 1px solid #000000; }
            """
        )

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.setSpacing(14)

        title = QtWidgets.QLabel("IT Park company scoring")
        title_font = QtGui.QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "AI-only scoring using public web data. API key is required and stored in memory only."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #333;")
        layout.addWidget(subtitle)

        form_group = QtWidgets.QGroupBox("run settings")
        form_layout = QtWidgets.QFormLayout(form_group)
        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Company name")
        self.website_input = QtWidgets.QLineEdit()
        self.website_input.setPlaceholderText("https://example.com (optional)")
        self.api_key_input = QtWidgets.QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.api_key_hint = QtWidgets.QLabel("OpenAI API key is required.")
        self.api_key_hint.setStyleSheet("color: #000;")

        form_layout.addRow("company name", self.name_input)
        form_layout.addRow("website (optional)", self.website_input)
        form_layout.addRow("OpenAI API key", self.api_key_input)
        form_layout.addRow("", self.api_key_hint)

        self.criteria_settings_button = QtWidgets.QPushButton("open criteria settings")
        self.criteria_settings_button.clicked.connect(self._open_criteria_settings)
        self.criteria_count_label = QtWidgets.QLabel("")
        self.criteria_count_label.setStyleSheet("color: #333;")
        criteria_row = QtWidgets.QHBoxLayout()
        criteria_row.addWidget(self.criteria_settings_button)
        criteria_row.addStretch(1)
        criteria_row.addWidget(self.criteria_count_label)
        form_layout.addRow("criteria", criteria_row)

        layout.addWidget(form_group)

        score_row = QtWidgets.QHBoxLayout()
        self.search_button = QtWidgets.QPushButton("score company")
        self.search_button.setMinimumHeight(38)
        self.search_button.setStyleSheet(
            "QPushButton { background-color: #000; color: #fff; font-weight: 600; "
            "border-radius: 8px; padding: 8px 16px; }"
            "QPushButton:disabled { background-color: #999; color: #eee; }"
        )
        self.search_button.clicked.connect(self._run_scoring)
        score_row.addStretch(1)
        score_row.addWidget(self.search_button)
        score_row.addStretch(1)
        layout.addLayout(score_row)

        results_group = QtWidgets.QGroupBox("results")
        results_layout = QtWidgets.QVBoxLayout(results_group)
        summary_grid = QtWidgets.QGridLayout()
        self.overall_value = QtWidgets.QLabel("--")
        self.coverage_value = QtWidgets.QLabel("--")
        self.confidence_value = QtWidgets.QLabel("--")
        self.flags_value = QtWidgets.QLabel("--")
        self.flags_value.setWordWrap(True)
        summary_grid.addWidget(QtWidgets.QLabel("overall score"), 0, 0)
        summary_grid.addWidget(self.overall_value, 0, 1)
        summary_grid.addWidget(QtWidgets.QLabel("coverage"), 0, 2)
        summary_grid.addWidget(self.coverage_value, 0, 3)
        summary_grid.addWidget(QtWidgets.QLabel("confidence"), 0, 4)
        summary_grid.addWidget(self.confidence_value, 0, 5)
        summary_grid.addWidget(QtWidgets.QLabel("flags"), 1, 0)
        summary_grid.addWidget(self.flags_value, 1, 1, 1, 5)
        results_layout.addLayout(summary_grid)

        self.category_table = QtWidgets.QTableWidget(0, 2)
        self.category_table.setHorizontalHeaderLabels(["category", "score"])
        self.category_table.verticalHeader().setVisible(False)
        self.category_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.category_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.category_table.setAlternatingRowColors(True)
        self.category_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.category_table)

        self.criteria_table = QtWidgets.QTableWidget(0, 5)
        self.criteria_table.setHorizontalHeaderLabels(
            ["category", "criterion", "score", "weight", "rationale"]
        )
        self.criteria_table.verticalHeader().setVisible(False)
        self.criteria_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.criteria_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.criteria_table.setAlternatingRowColors(True)
        self.criteria_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )
        self.criteria_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents
        )
        self.criteria_table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents
        )
        self.criteria_table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.ResizeToContents
        )
        self.criteria_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.criteria_table, 1)
        layout.addWidget(results_group, 2)

        footer_row = QtWidgets.QHBoxLayout()
        self.export_button = QtWidgets.QPushButton("export pdf/csv/excel")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export_reports)
        self.clear_button = QtWidgets.QPushButton("clear")
        self.clear_button.clicked.connect(self._clear_form)
        footer_row.addStretch(1)
        footer_row.addWidget(self.export_button)
        footer_row.addWidget(self.clear_button)
        layout.addLayout(footer_row)

        self.setCentralWidget(central)
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Ready")

        self.name_input.textChanged.connect(self._update_actions)
        self.api_key_input.textChanged.connect(self._update_actions)
        self._update_selected_count()

    def _get_selected_criteria(self) -> list:
        self.criteria_by_id = {item["id"]: item for item in DEFAULT_CRITERIA}
        return [self.criteria_by_id[cid] for cid in self.selected_criteria_ids if cid in self.criteria_by_id]

    def _update_selected_count(self) -> None:
        count = len(self.selected_criteria_ids)
        self.criteria_count_label.setText(f"{count} selected")

    def _open_criteria_settings(self) -> None:
        dialog = CriteriaDialog(DEFAULT_CRITERIA, self.selected_criteria_ids, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.selected_criteria_ids = dialog.get_selected_ids()
            self._update_selected_count()
            self._update_actions()

    def _run_scoring(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Missing name", "Enter a company name.")
            return

        self._set_status("Resolving company...")
        self._clear_results()
        self.export_button.setEnabled(False)

        website = self.website_input.text().strip() or None
        candidates = self.collector.resolve_candidates(name, website)
        if not candidates:
            self._set_status("No public info found.")
            return

        website = candidates[0]
        if len(candidates) > 1:
            chosen, ok = QtWidgets.QInputDialog.getItem(
                self, "Select company", "Choose the correct website:", candidates, editable=False
            )
            if not ok:
                self._set_status("Cancelled.")
                return
            website = chosen

        run_id = uuid.uuid4().hex
        self.cache.start_run(run_id, name, website)

        self._set_status("Collecting public pages...")
        pages = self.collector.collect_company(website)
        if not pages:
            self._set_status("No public info found or blocked by robots.txt.")
            return

        api_key = self.api_key_input.text().strip()
        if not api_key:
            QtWidgets.QMessageBox.warning(self, "Missing API key", "OpenAI API key is required.")
            self._set_status("Missing API key.")
            return

        selected_criteria = self._get_selected_criteria()
        if not selected_criteria:
            QtWidgets.QMessageBox.warning(
                self, "No criteria selected", "Select at least one criterion to score."
            )
            self._set_status("No criteria selected.")
            return

        self._set_status("Scoring with AI...")
        scorecard = score_with_llm(
            pages=[(page.url, page.content) for page in pages],
            api_key=api_key,
            model=DEFAULT_MODEL,
            criteria_list=selected_criteria,
        )
        if not scorecard:
            self._set_status("AI scoring failed.")
            return

        if "No public information found." in scorecard.flags:
            self._set_status("No public info found (disqualified).")
            return

        if "No English support." in scorecard.flags:
            self._set_status("No English support (disqualified).")
            return

        result = CompanyResult(
            company_name=name,
            website=website,
            features={},
            scorecard=scorecard,
            run_id=run_id,
        )

        self.cache.save_criteria(run_id, scorecard.criteria)
        self.cache.finish_run(run_id, scorecard)

        self._display_result(result)
        self._last_result = result
        self.export_button.setEnabled(True)
        self._set_status("Done")

    def _display_result(self, result: CompanyResult) -> None:
        self.overall_value.setText(f"{result.scorecard.overall_score:.2f}")
        self.coverage_value.setText(f"{result.scorecard.coverage * 100:.1f}%")
        self.confidence_value.setText(f"{result.scorecard.confidence * 100:.1f}%")
        if result.scorecard.flags:
            self.flags_value.setText(", ".join(result.scorecard.flags))
        else:
            self.flags_value.setText("none")

        categories = sorted(result.scorecard.category_scores.items(), key=lambda item: item[0])
        self.category_table.setRowCount(len(categories))
        for row, (category, score) in enumerate(categories):
            self.category_table.setItem(row, 0, QtWidgets.QTableWidgetItem(category))
            self.category_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{score:.2f}"))

        criteria = result.scorecard.criteria
        self.criteria_table.setRowCount(len(criteria))
        for row, criterion in enumerate(criteria):
            self.criteria_table.setItem(row, 0, QtWidgets.QTableWidgetItem(criterion.category))
            self.criteria_table.setItem(row, 1, QtWidgets.QTableWidgetItem(criterion.name))
            self.criteria_table.setItem(
                row,
                2,
                QtWidgets.QTableWidgetItem(f"{criterion.score:.2f}/{criterion.max_score:.2f}"),
            )
            self.criteria_table.setItem(
                row,
                3,
                QtWidgets.QTableWidgetItem(f"{criterion.weight:.2f}"),
            )
            self.criteria_table.setItem(row, 4, QtWidgets.QTableWidgetItem(criterion.rationale))

    def _export_reports(self) -> None:
        result = getattr(self, "_last_result", None)
        if not result:
            return
        self.reporter.write_csv(result)
        self.reporter.write_excel(result)
        self.reporter.write_pdf(result)
        QtWidgets.QMessageBox.information(
            self,
            "Export complete",
            f"Reports saved to: {OUTPUT_DIR}",
        )

    def _clear_form(self) -> None:
        self.name_input.clear()
        self.website_input.clear()
        self.api_key_input.clear()
        self._clear_results()
        self.export_button.setEnabled(False)
        self._set_status("Ready")
        self._update_actions()

    def _clear_results(self) -> None:
        self.overall_value.setText("--")
        self.coverage_value.setText("--")
        self.confidence_value.setText("--")
        self.flags_value.setText("--")
        self.category_table.setRowCount(0)
        self.criteria_table.setRowCount(0)

    def _update_actions(self) -> None:
        has_name = bool(self.name_input.text().strip())
        has_key = bool(self.api_key_input.text().strip())
        has_criteria = bool(self.selected_criteria_ids)
        self.search_button.setEnabled(has_name and has_key and has_criteria)
        self.api_key_hint.setVisible(not has_key)
        self._update_selected_count()

    def _set_status(self, text: str) -> None:
        self.status_bar.showMessage(text)


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
