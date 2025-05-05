import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from gui import *
from database import *
from connections import *


class TM8SApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_TM8S()
        self.ui.setupUi(self)

        self.db = PlayerDatabase()

        print(f"Database loaded. Players: {len(self.db.players_db)}")
        for player in self.db.players_db:
            print(f"  - {player}")

        self.connection_finder = ConnectionFinder()

        self.initialize_ui()

        self.ui.p1_search_box.lineEdit().textChanged.connect(self.update_button_state)
        self.ui.p2_search_box.lineEdit().textChanged.connect(self.update_button_state)
        self.ui.player_search_button.clicked.connect(self.search_connection)
        self.ui.results_box_slider.valueChanged.connect(self.adjust_results_scroll)


    def initialize_ui(self) -> None:
        """Initialize UI elements with default values"""
        self.ui.p1_search_box.lineEdit().setPlaceholderText("Begin typing a player name")
        self.ui.p2_search_box.lineEdit().setPlaceholderText("Begin typing a player name")

        all_players = self.db.get_all_players()
        self.ui.p1_search_box.addItems(all_players)
        self.ui.p2_search_box.addItems(all_players)

        self.ui.p1_search_box.clearEditText()
        self.ui.p2_search_box.clearEditText()

        self.ui.search_progress_bar.setValue(0)
        self.ui.search_progress_bar.setVisible(False)

        self.setWindowTitle("Tm8s")


    def update_button_state(self):
        """Enable search button if both player search boxes have valid entry"""
        p1_text = self.ui.p1_search_box.currentText()
        p2_text = self.ui.p2_search_box.currentText()

        p1_valid = bool(p1_text) and (p1_text in self.db.players_db)
        p2_valid = bool(p2_text) and (p2_text in self.db.players_db)

        button_enabled = p1_valid and p2_valid
        self.ui.player_search_button.setEnabled(p1_valid and p2_valid)


    def search_connection(self):
        """Handle search button"""
        p1 = self.ui.p1_search_box.currentText()
        p2 = self.ui.p2_search_box.currentText()

        self.ui.search_progress_bar.setVisible(True)
        self.ui.player_search_button.setEnabled(False)

        self.start_search_process(p1, p2)


    def start_search_process(self, p1, p2):
        """Start search process with progress animation"""
        self.progress_counter = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.update_search_progress(p1, p2))
        self.timer.start(50)


    def update_search_progress(self, p1, p2):
        """Update progress bar when searching"""
        self.progress_counter += 2
        self.ui.search_progress_bar.setValue(self.progress_counter)

        if self.progress_counter >= 100:
            self.timer.stop()
            self.ui.search_progress_bar.setVisible(False)
            self.ui.player_search_button.setEnabled(True)

            self.find_display_connections(p1, p2)


    def find_display_connections(self, p1, p2):
        """Find connections between players, display result"""
        try:
            p1_clubs = self.db.get_player_data(p1)
            p2_clubs = self.db.get_player_data(p2)

            connections = self.connection_finder.find_player_connections(p1_clubs, p2_clubs)

            self.display_connection_results(p1, p2, connections)
        except Exception as e:
            print(f"Error: {str(e)}")


    def display_connection_results(self, p1, p2, connections):
        """Display formatted connection results"""

        bold_format = QtGui.QTextCharFormat()
        bold_format.setFontWeight(QtGui.QFont.Weight.Bold)

        normal_format = QtGui.QTextCharFormat()
        normal_format.setFontWeight(QtGui.QFont.Weight.Normal)

        self.ui.results_display.clear()

        cursor = self.ui.results_display.textCursor()

        cursor.insertText(f"{p1} and {p2}", bold_format)
        cursor.insertBlock()
        cursor.insertBlock()

        overlapping = [c for c in connections if c.get("overlapped", False)]

        if connections:
            cursor.insertText("✓ PLAYED TOGETHER AT:", bold_format)
            cursor.insertBlock()
            cursor.insertBlock()

            for conn in connections:
                cursor.insertText(f"{conn['club_name']}", bold_format)
                cursor.insertBlock()

                cursor.insertText(f"✓ Played together: {conn['overlap_start']}-{conn['overlap_end']}", normal_format)
                cursor.insertBlock()

                cursor.insertText(f"{p1} at club: {conn['p1_period']}", normal_format)
                cursor.insertBlock()
                cursor.insertText(f"{p2} at club: {conn['p2_period']}", normal_format)
                cursor.insertBlock()
                cursor.insertBlock()
        else:
            cursor.insertText("✗ Never played together at the same club", bold_format)

        self.update_results_slider_range()


    def adjust_results_scroll(self, value):
        """Adjust scrollbar of the results text"""
        scrollbar = self.ui.results_display.verticalScrollBar()
        if scrollbar.maximum() > 0:
            position = int(value * scrollbar.maximum() / 100)
            scrollbar.setValue(position)


    def update_results_slider_range(self):
        """Update the slider range based on content height"""
        try:
            scrollbar = self.ui.results_display.verticalScrollBar()
            if scrollbar.maximum() > 0:
                self.ui.results_box_slider.setMaximum(100)
                self.ui.results_box_slider.setValue(0)
            else:
                self.ui.results_box_slider.setMaximum(0)
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    """
    Entry point that launches the application
    """
    app = QtWidgets.QApplication(sys.argv)
    window = TM8SApp()
    window.show()
    sys.exit(app.exec())