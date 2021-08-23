from datetime import datetime
import matplotlib.pyplot as plt
import csv
from statistics import mean, stdev
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import Ridge
import json

rows = []

with open("mqtt_sub/messages.csv", "r") as file:
    csv_reader = csv.DictReader(file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        row['datetime'] = datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S.%f')
        row['chessboard'] = json.loads(row['chessboard'])
        row['move_to_x'] = int(row['move_to_x'])
        row['move_to_y'] = int(row['move_to_y'])
        rows.append(row)

game_moves = {}
for row in rows:
    if row['host_device_id'] not in game_moves:
        game_moves[row['host_device_id']] = 0

    game_moves[row['host_device_id']] += 1

plt.style.use('ggplot')

x = game_moves.keys()
x_pos = [i for i, _ in enumerate(x)]
energy = [5, 6, 15, 22, 24, 8]

x_pos = [i for i, _ in enumerate(x)]

plt.bar(x_pos, game_moves.values(), color='green')
plt.xlabel("Game Id")
plt.ylabel("Number of moves")
plt.title("Number of moves per game")

plt.xticks(x_pos, x, rotation = 'vertical')

plt.show()

print('Średnia liczba ruchów w grze:', mean(game_moves.values()))

print('Odchylenie standardowe średniej liczby ruchów w grze:', stdev(game_moves.values()))

def matrix_to_array(matrix):
    array = []
    for row in matrix:
        for field in row:
            array.append(field)

    return array

X = [matrix_to_array(row["chessboard"]) for row in rows]
Y = [(row['move_to_x'], row['move_to_y']) for row in rows]

regessor = Ridge()
regessor.fit(X, Y)
prediction = regessor.predict(
            [matrix_to_array([[0, 2, 0, 2, 0, 2, 0, 2], [2, 0, 2, 0, 2, 0, 0, 0], [0, 2, 0, 2, 0, 0, 0, 2], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 1, 0, 1, 0, 1], [1, 0, 1, 0, 1, 0, 1, 0]])]
        )[0]
print('Przewidywany ruch:', f'{int(round(prediction[0]))}, {int(round(prediction[1]))}')
