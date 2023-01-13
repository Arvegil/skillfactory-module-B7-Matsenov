from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongInputException(BoardException):
    def __str__(self):
        return "Неверный формат ввода"

class BoardWrongPlaceException(BoardException):
    def __str__(self):
        return "Корабль не удается разместить, попробуйте еще раз"

class Dot:
    def __init__(self,x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction in ['v', 1]:
                cur_x += i

            elif self.direction in ['h', 0]:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

class Board:
    def __init__(self, size):
        self.size = size
        self.field = [['~']*self.size for _ in range(self.size)]
        self.busy = []
        self.ships = []
        self.count = 0

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongPlaceException
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        self.contour(ship)
        self.ships.append(ship)

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, flag = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if flag:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def display_board(self):
        line = '  1  2  3  4  5  6'

        print(line)
        for row, i in zip(self.field, line.split()):
            print(i, '  '.join(str(j) for j in row))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, flag=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
            else:
                self.field[d.x][d.y] = "O"

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)

class Game:
    def __init__(self, size=6):
        self.size = size
        self.us = None
        self.ai = None

    def create_players(self):
        pl = self.player_input()
        # pl = self.random_input()
        co = self.random_input()
        while (pl == None or co == None):
            if pl == None:
                pl = self.random_input()
            if co == None:
                co = self.random_input()
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def greet(self):
        print("  Приветсвуем вас в игре")
        print("       морской бой    ")
        print("-"*65)
        print(" Заполните свое поле.")
        print(" Вы можете расставить корабли самостоятельно,")
        print(" или ввести 'random', чтобы разместить корабль случайным образом  ")
        print(" Введите 'clear', чтобы  начать размещение заново")
        print("-"*65)

    def display(self, board_p, board_c):
        line = '  1  2  3  4  5  6        1  2  3  4  5  6'
        print( '  Ваше поле:            Поле противника:')
        print(line)
        for i in range(0,6):
            for j in range(0,6):
                if board_c.field[i][j] == "■":
                    board_c.field[i][j] = "~"
        for row_1, row_2, i in zip(board_p.field, board_c.field, line.split()):
            print(i, '  '.join(str(j) for j in row_1), '    ', i, '  '.join(str(j) for j in row_2))

    def player_input(self):
        board = Board(self.size)
        lens = [3, 2, 2, 1, 1, 1, 1]
        for l in lens:
            while True:
                try:
                    print(f'Разместите {l} -палубный корабль, введите координаты носа и направление h/v через пробел: ')
                    ship = input().split()
                    if ship[0] == 'random':
                        self.random_place(l,board)
                        board.display_board()
                    elif ship[0] == 'clear':
                        board = None
                        board = Board(self.size)
                        self.player_input()
                    else:
                        self.player_place(l, ship, board)
                        board.display_board()
                except BoardException as e:
                    print(e)
                else:
                    break
        board.busy = []
        return board

    def player_place(self, length, place, board):
        if not ((len(place) == 3 and place[0].isdigit() and place[1].isdigit()) and \
                1<=int(place[0])<=self.size and 1<=int(place[1])<=self.size and place[2] in ['h', 'v']):
            raise BoardWrongInputException()
        ship = Ship(length, Dot(int(place[0])-1, int(place[1])-1), place[2])
        board.add_ship(ship)

    def random_place(self, l, board):
        t_board = board
        attempts = 0
        while t_board == board:
            attempts += 1
            if attempts > 20000:
                raise BoardWrongPlaceException()
                return None
            ship = Ship(l, Dot(randint(0, board.size-1), randint(0, board.size-1)), randint(0, 1))
            board.add_ship(ship)
            break
        return board

    def random_input(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 20000:
                    return None
                ship = Ship(l, Dot(randint(0, board.size), randint(0, board.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except:
                    pass
            # board.display_board()
            # print(l)
        board.busy = []
        return board

    def loop(self):
        print('Вводите номер строки и номер столбца через пробел, чтобы совершить выстрел')
        turn = 0
        while True:
            self.display(self.us.board,self.ai.board)
            if turn % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                turn -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                self.display(self.us.board, self.ai.board)
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                self.display(self.us.board, self.ai.board)
                break
            turn += 1

g=Game()

g.greet()
g.create_players()

# g.player_input(board)
g.loop()