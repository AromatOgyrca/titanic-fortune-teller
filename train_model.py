import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Загрузка данных
df = pd.read_csv('train.csv')

# 2. Выбор колонок, которые будет вводить пользователь
features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
X = df[features].copy()
y = df['Survived']

# 3. Заполнение пропущенных значений (требование преподавателя)
# Возраст заполняем медианой
X['Age'] = X['Age'].fillna(X['Age'].median())
# Стоимость билета заполняем медианой 
X['Fare'] = X['Fare'].fillna(X['Fare'].median())
# Порт посадки заполняем самым частым значением (модой)
X['Embarked'] = X['Embarked'].fillna(X['Embarked'].mode()[0])

# 4. Преобразование текстовых данных в числовые
# Пол: male -> 0, female -> 1
X['Sex'] = X['Sex'].map({'male': 0, 'female': 1})
# Порт: S -> 0, C -> 1, Q -> 2
X['Embarked'] = X['Embarked'].map({'S': 0, 'C': 1, 'Q': 2})

# 5. Обучение модели (Случайный лес)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 6. Сохранение обученной модели в файл
joblib.dump(model, 'model.pkl')
print("Модель сохранена в файл model.pkl")