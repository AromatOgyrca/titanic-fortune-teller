import os
import sys
import pandas as pd
import joblib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QPushButton, QWidget, QComboBox, QSpinBox, QHBoxLayout, QFrame)
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase, QPalette, QBrush
from PyQt5.QtCore import Qt, QTimer, QSize

# Устанавливаем пути для плагинов PyQt5 в виртуальном окружении
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r"C:\Users\Галым\визуал студио\.venv\Lib\site-packages\PyQt5\Qt5\plugins\platforms"
os.environ['QT_PLUGIN_PATH'] = r"C:\Users\Галым\визуал студио\.venv\Lib\site-packages\PyQt5\Qt5\plugins"

class TitanicFortuneTeller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тайны Титаника")
        
        # Размеры окна
        self.setFixedSize(800, 600)
        
        # Загрузка кастомного шрифта
        self.font_id = QFontDatabase.addApplicationFont("font.ttf")
        if self.font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(self.font_id)[0]
            self.custom_font = QFont(self.font_family, 16)
            self.custom_font_large = QFont(self.font_family, 24)
        else:
            print("Шрифт font.ttf не найден, используется стандартный.")
            self.custom_font = QFont("Arial", 14)
            self.custom_font_large = QFont("Arial", 20)

        # Загрузка модели
        try:
            self.model = joblib.load('model.pkl')
        except FileNotFoundError:
            print("Ошибка: Файл model.pkl не найден!")
            sys.exit(1)

        # Переменные для хранения ответов
        self.user_data = {
            'Pclass': 3, 'Sex': 0, 'Age': 25, 
            'SibSp': 0, 'Parch': 0, 'Fare': 15.0, 'Embarked': 0
        }
        
        self.step = 0 # Текущий шаг диалога
        self.base_size = 130  
        self.pulse_direction = 1
        self.current_size = 130
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Установка фонового изображения bg.jpg
        palette = QPalette()
        bg_pixmap = QPixmap("bg.jpg").scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(bg_pixmap))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Лейбл для шара
        self.ball_label = QLabel()
        self.ball_label.setFixedSize(150, 150)
        self.ball_label.setAlignment(Qt.AlignCenter)
        self.ball_label.setStyleSheet("background: transparent;")
        
        self.update_ball_image(self.base_size)
        
        # Таймер для пульсации шара
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.animate_pulse)

        # Центрирование шара на экране
        ball_layout = QHBoxLayout()
        ball_layout.addStretch()
        ball_layout.addWidget(self.ball_label)
        ball_layout.addStretch()
        
        main_layout.addStretch(4)
        main_layout.addLayout(ball_layout)
        main_layout.addStretch(1)

        # Контейнер для диалога
        self.dialog_frame = QFrame()
        self.dialog_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 10px;
                padding: 10px;
            }
            QLabel, QPushButton, QComboBox, QSpinBox {
                color: #e0e0e0;
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: rgba(80, 20, 100, 200);
                border: 1px solid #a050c0;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(100, 40, 120, 255);
            }
        """)
        dialog_layout = QVBoxLayout(self.dialog_frame)
        
        # Текст гадалки
        self.dialog_text = QLabel("Подойди ближе, путник... Готов ли ты узнать свою судьбу на Титанике?")
        self.dialog_text.setFont(self.custom_font)
        self.dialog_text.setAlignment(Qt.AlignCenter)
        self.dialog_text.setWordWrap(True)
        dialog_layout.addWidget(self.dialog_text)
        
        # Виджеты для ответов
        self.combo_box = QComboBox()
        self.combo_box.setFont(self.custom_font)
        self.combo_box.setStyleSheet("background-color: rgba(50,50,50,200);")
        self.combo_box.hide()
        dialog_layout.addWidget(self.combo_box)
        
        self.spin_box = QSpinBox()
        self.spin_box.setFont(self.custom_font)
        self.spin_box.setStyleSheet("background-color: rgba(50,50,50,200);")
        self.spin_box.hide()
        dialog_layout.addWidget(self.spin_box)

        # Панель для кнопок управления (Назад, Ответить, Выход)
        buttons_layout = QHBoxLayout()
        
        self.back_button = QPushButton("Назад")
        self.back_button.setFont(self.custom_font)
        self.back_button.hide()
        self.back_button.clicked.connect(self.prev_step)
        buttons_layout.addWidget(self.back_button)

        self.action_button = QPushButton("Начать сеанс")
        self.action_button.setFont(self.custom_font_large)
        self.action_button.clicked.connect(self.next_step)
        buttons_layout.addWidget(self.action_button)

        # Кнопка выхода с крупным шрифтом и коротким текстом
        self.exit_button = QPushButton("✕")
        self.exit_button.setFont(self.custom_font_large)
        self.exit_button.setFixedSize(50, 45)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(120, 20, 20, 200);
                border: 1px solid #c05050;
                border-radius: 5px;
                color: #ffcccc;
            }
            QPushButton:hover {
                background-color: rgba(160, 30, 30, 255);
            }
        """)
        self.exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_button)
        
        dialog_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.dialog_frame)

    def update_ball_image(self, size):
        pixmap = QPixmap('ball.png').scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.ball_label.setPixmap(pixmap)

    def animate_pulse(self):
        self.current_size += self.pulse_direction * 2
        if self.current_size >= 145 or self.current_size <= 125:
            self.pulse_direction *= -1
        self.update_ball_image(self.current_size)

    def save_current_answer(self):
        """Сохраняет ответ пользователя с текущего шага перед тем, как идти дальше или назад"""
        if self.step == 1:
            ans = self.combo_box.currentIndex()
            if ans == 0: self.user_data['Pclass'] = 1
            elif ans == 1: self.user_data['Pclass'] = 2
            else: self.user_data['Pclass'] = 3
        elif self.step == 2:
            self.user_data['Sex'] = 0 if self.combo_box.currentIndex() == 0 else 1
        elif self.step == 3:
            self.user_data['Age'] = self.spin_box.value()
        elif self.step == 4:
            self.user_data['SibSp'] = self.spin_box.value()
        elif self.step == 5:
            self.user_data['Parch'] = self.spin_box.value()
        elif self.step == 6:
            self.user_data['Fare'] = self.spin_box.value()
        elif self.step == 7:
            ans = self.combo_box.currentIndex()
            if ans == 0: 
                self.user_data['Embarked'] = 1  # Шербур (C) -> 1
            elif ans == 1: 
                self.user_data['Embarked'] = 2  # Квинстаун (Q) -> 2
            else: 
                self.user_data['Embarked'] = 0  # Саутгемптон (S) -> 0

    def next_step(self):
        if self.step > 0 and self.step < 8:
            self.save_current_answer()

        self.step += 1
        self.update_ui_state()

    def prev_step(self):
        if self.step > 1:
            self.step -= 1
            self.update_ui_state()
        elif self.step == 1:
            self.step = 0
            self.update_ui_state()

    def update_ui_state(self):
        """Управляет тем, что показывается на каждом шаге диалога"""
        self.combo_box.hide()
        self.spin_box.hide()
        self.action_button.show()
        
        if self.step == 0:
            self.back_button.hide()
        else:
            self.back_button.show()

        if self.step == 0:
            self.dialog_text.setText("Подойди ближе, путник... Готов ли ты узнать свою судьбу на Титанике?")
            self.action_button.setText("Начать сеанс")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 1:
            self.dialog_text.setText("Каким классом ты путешествуешь?")
            self.combo_box.clear()
            self.combo_box.addItems(["Элита (1 класс)", "Средний класс (2 класс)", "Бедняк (3 класс)"])
            val = self.user_data['Pclass']
            self.combo_box.setCurrentIndex(0 if val == 1 else (1 if val == 2 else 2))
            self.combo_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 2:
            self.dialog_text.setText("Кто ты?")
            self.combo_box.clear()
            self.combo_box.addItems(["Мужчина", "Женщина"])
            self.combo_box.setCurrentIndex(self.user_data['Sex'])
            self.combo_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 3:
            self.dialog_text.setText("Сколько тебе лет?")
            self.spin_box.setRange(0, 100)
            self.spin_box.setValue(self.user_data['Age'])
            self.spin_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 4:
            self.dialog_text.setText("Сколько братьев, сестер или супругов с тобой?")
            self.spin_box.setRange(0, 10)
            self.spin_box.setValue(self.user_data['SibSp'])
            self.spin_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 5:
            self.dialog_text.setText("Сколько родителей или детей с тобой?")
            self.spin_box.setRange(0, 10)
            self.spin_box.setValue(self.user_data['Parch'])
            self.spin_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 6:
            self.dialog_text.setText("Сколько долларов ты заплатил за билет?")
            self.spin_box.setRange(0, 1000)
            self.spin_box.setValue(int(self.user_data['Fare']))
            self.spin_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 7:
            self.dialog_text.setText("В каком порту ты сел на корабль?")
            self.combo_box.clear()
            self.combo_box.addItems(["Шербур (C)", "Квинстаун (Q)", "Саутгемптон (S)"])
            val = self.user_data['Embarked']
            self.combo_box.setCurrentIndex(0 if val == 1 else (1 if val == 2 else 2))
            self.combo_box.show()
            self.action_button.setText("Ответить")
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.next_step)
            
        elif self.step == 8:
            self.dialog_text.setText("Духи готовы дать ответ...")
            self.action_button.setText("Узнать судьбу")
            self.back_button.hide()
            self.action_button.disconnect()
            self.action_button.clicked.connect(self.predict_survival)

    def predict_survival(self):
        self.action_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.exit_button.setEnabled(False)
        self.combo_box.hide()
        self.spin_box.hide()
        self.dialog_text.setText("Вглядываюсь в туман будущего...")
        
        self.pulse_timer.start(40)
        QTimer.singleShot(3000, self.show_result)

    def show_result(self):
        self.pulse_timer.stop()
        self.current_size = self.base_size
        self.update_ball_image(self.base_size)
        
        features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
        input_data = pd.DataFrame([[self.user_data[f] for f in features]], columns=features)
        
        probability = self.model.predict_proba(input_data)[0][1] * 100
        
        if probability > 50:
            result_text = f"Ты выживешь с вероятностью {probability:.1f}%. Духи благосклонны к тебе."
            self.dialog_text.setStyleSheet("color: #4CAF50;")
        else:
            result_text = f"Вероятность твоего выживания лишь {probability:.1f}%. Ледяные воды ждут тебя."
            self.dialog_text.setStyleSheet("color: #F44336;")
            
        self.dialog_text.setText(result_text)
        
        self.action_button.setText("Спросить снова")
        self.action_button.setEnabled(True)
        self.exit_button.setEnabled(True)
        self.action_button.disconnect()
        self.action_button.clicked.connect(self.reset_dialog)

    def reset_dialog(self):
        self.step = 0
        self.dialog_text.setStyleSheet("color: #e0e0e0;")
        self.back_button.setEnabled(True)
        self.update_ui_state()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TitanicFortuneTeller()
    window.show()
    sys.exit(app.exec_())