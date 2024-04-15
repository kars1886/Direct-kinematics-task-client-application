from dataclasses import dataclass
from math import cos, sin, pi
import socket
import struct

@dataclass #Декоратор @dataclass автоматически добавляет методы, такие как __init__, __repr__, и __eq__
class RobotData:
    timestamp: int
    theta: list  # Список углов поворота сочленений

def calculate_kinematics(theta):
    # Параметры DH для каждого сочленения
    # Это параметры Денавита Хартенберга, я не физик, но как понял - так и решил :)
    # В данном случае я представил его как список кортежей
    # Если разобрать первый кортеж, то
    # 0 - a(m) длина звена, / 0.21 d(m) смещение вдоль оси Z пред. сочл. /
    # pi/2 alpha т.е. угол между осями / theta[0] угол вокруг общей нормали
    DH_params = [
        (0, 0.21, pi/2, theta[0]),
        (-0.8, 0.193, 0, theta[1]),
        (-0.598, -0.16, 0, theta[2]),
        (0, 0.25, pi/2, theta[3]),
        (0, 0.25, -pi/2, theta[4]),
        (0, 0.25, 0, theta[5])
    ]

    # Начальная матрица преобразования (единичная матрица), это матрица до преобразования
    T = [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]]

    # Вычисление общей матрицы преобразования
    for a, d, alpha, theta in DH_params:
        cos_theta, sin_theta = cos(theta), sin(theta)
        cos_alpha, sin_alpha = cos(alpha), sin(alpha)

        T_next = [
            [cos_theta, -sin_theta * cos_alpha, sin_theta * sin_alpha, a * cos_theta],
            [sin_theta, cos_theta * cos_alpha, -cos_theta * sin_alpha, a * sin_theta],
            [0, sin_alpha, cos_alpha, d],
            [0, 0, 0, 1]
        ]

        # Матричное умножение T и T_next
        T = matrix_multiply(T, T_next)

    # Позиция энд-эффектора - это последний столбец результирующей матрицы
    position = [T[0][3], T[1][3], T[2][3]]
    return position

def matrix_multiply(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

# Создание UDP сокета
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# AF_INET - используем IPv4 адресацию, создаем сокет
#DGRAM - указываем что используем протокол UDP
# DG - Datagram
# Например для TCP SOCK_STREAM
# Ось Z это ось в направлении оси соединения
serv_address = ('localhost', 8088)
message = "get"

try:
    # Отправка сообщения "get"
    udp_socket.sendto(message.encode(), serv_address)
    # # Открытие файла для записи результатов
    with open('results.txt', 'w') as file:
    #     udp_socket.sendto(message.encode(), serv_address)
    # Для записи в файл можно было бы использовать
    # Получение 5 сообщений от сервера
        for _ in range(5):
            data, _ = udp_socket.recvfrom(1024) #возвращает кортеж, data = сами данные, а _ адрес отправителя
            unpacked_data = struct.unpack('Q6d', data) #struct преобразует байтовые данные ( у нас это data )
            # в значения python, Q6d это формат распаковки байтовых данных, Q - беззнаковое целое число 64 бита,
            # 6d это шесть вещественных числе с двойной точностью double precision float
            robot_data = RobotData(timestamp=unpacked_data[0], theta=unpacked_data[1:])
            # print(f"Unpacked data = {unpacked_data}")
            # print(f"Robot data = {robot_data}"
            # print(f"Received message {robot_data.timestamp}: {robot_data.theta}")
            position = calculate_kinematics(robot_data.theta)
            file.write(f"{robot_data.timestamp}, {position}\n")
            print(f"Порядковый номер сообщения: {robot_data.timestamp}, позиция: {position}")
            # Можно использовать "сухой" вывод, для работы с данными:
            # print(f"{robot_data.timestamp}, {position}")
            # При желании, мы могли бы использовать цикл while для
            # того чтобы программа выполнялась без остановки на возможные ошибки

except socket.timeout:
    print("Время ожидания соединения истекло.")
except Exception as e:
    print("Произошла ошибка:", str(e))

finally:
    udp_socket.close()

#Тестовое задание выполнил Фатенков Максим :)
#Избыточное количество комментариев вызвано характером работы: тестовое задание,
#на практике наличие комментариев сведено к минимуму
