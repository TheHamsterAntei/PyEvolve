#Version 1.0.2
import tkinter
import time
import numpy as np

root = tkinter.Tk()
root.title("Evolve")
root.geometry("1000x700")
move_dict = ['up', 'right', 'down', 'left']
photo_eff = 1.2
table_mode = tkinter.IntVar()
table_mode.set(1)

class Table:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.data = [[0 for j in range(0, height)] for i in range(0, width)]
        self.life = [Alive(19, 14, canvas, self, 100)]
        self.food_data = [[np.random.uniform(10, 100) for j in range(0, height)] for i in range(0, width)]
        self.food_data_images = [[None for j in range(0, height)] for i in range(0, width)]
        self.step = 0
        if table_mode.get() == 1:
            self.draw_food()

        #Статистика
        self.stat_red = None
        self.stat_green = None
        self.stat_blue = None
        self.stat_energy = None
        self.stat_food = None
        self.stat_count = [None for i in range(0, 212)]
        self.stat_count_value = [0 for i in range(0, 212)]
        self.draw_stats()

    def change_mode(self):
        mode = table_mode.get()
        if mode == 0:
            self.undraw_food()
        if mode == 1:
            self.draw_food()

    def next(self):
        self.step += 1
        if self.step % 3000 >= 0 and self.step % 3000 < 1200:
            photo_eff = 1.2
        if self.step % 3000 >= 1200 and self.step % 3000 < 1600:
            photo_eff = 0.3
        if self.step % 3000 >= 1600 and self.step % 3000 < 2600:
            photo_eff = 0.0
        if self.step % 3000 >= 2600 and self.step % 3000 < 3000:
            photo_eff = 0.3
        for i in self.life:
            i.next()
        self.food_refresh()
        if table_mode.get() == 1:
            self.draw_food()
        self.draw_stats()

    def isfree(self, x, y):
        if x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1:
            return False
        else:
            if self.data[x][y] == 1:
                return False
            else:
                return True


    def food_refresh(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                self.food_data[i][j] += np.random.uniform(0, 1.35)
                if self.food_data[i][j] > 200:
                    self.food_data[i][j] = 200

    def draw_food(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                color = self.food_data[i][j]
                color = max(0, min(255, color))
                if self.food_data_images[i][j] != None:
                    self.canvas.delete(self.food_data_images[i][j])
                if self.data[i][j] == 0 and color != 0:
                    self.food_data_images[i][j] = self.canvas.create_rectangle(
                        i * 20, j * 20, i * 20 + 19, j * 20 + 19,
                        outline=rgb(255 - int(color), 255 - int(color), 255 - int(color)),
                        fill=rgb(255 - int(color), 255 - int(color), 255 - int(color))
                    )
                else:
                    self.food_data_images[i][j] = None

    def undraw_food(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                if self.food_data_images[i][j] != None:
                    self.canvas.delete(self.food_data_images[i][j])
                    self.food_data_images[i][j] = None

    def draw_stats(self):
        if self.stat_red != None:
            self.canvas.delete(self.stat_red)
        if self.stat_green != None:
            self.canvas.delete(self.stat_green)
        if self.stat_blue != None:
            self.canvas.delete(self.stat_blue)
        if self.stat_energy != None:
            self.canvas.delete(self.stat_energy)
        if self.stat_food != None:
            self.canvas.delete(self.stat_food)
        world_red = 0
        world_green = 0
        world_blue = 0
        world_energy = 0
        world_food = 0
        if self.step % 7 == 0:
            self.stat_count_value.pop()
            self.stat_count_value.insert(0, len(self.life))
            value_max = 0
            for i in range(0, len(self.stat_count_value)):
                if self.stat_count_value[i] > value_max:
                    value_max = self.stat_count_value[i]
            for i in range(0, len(self.stat_count)):
                if self.stat_count[i] != None:
                    self.canvas.delete(self.stat_count[i])
                value = (self.stat_count_value[i] / value_max) * 99
                self.stat_count[i] = self.canvas.create_rectangle(
                    152 + (i * 4), 700, 155 + (i * 4), 700 - value,
                    outline=rgb(255 - (value * 2.55), value * 2.55, 0),
                    fill=rgb(255 - (value * 2.55), value * 2.55, 0)
                )
        for i in self.life:
            world_red += i.red_color / len(self.life)
            world_green += i.green_color / len(self.life)
            world_blue += i.blue_color / len(self.life)
            world_energy += i.energy / len(self.life)
        for i in range(0, len(self.food_data)):
            for j in range (0, len(self.food_data[i])):
                world_food += self.food_data[i][j] / (self.width * self.height)
        self.stat_red = self.canvas.create_rectangle(
            0, 700, 15, 700 - (world_red * 99 / 255),
            outline=rgb(255, 0, 0),
            fill=rgb(255, 0, 0)
        )
        self.stat_green = self.canvas.create_rectangle(
            16, 700, 30, 700 - (world_green * 99 / 255),
            outline=rgb(0, 255, 0),
            fill=rgb(0, 255, 0)
        )
        self.stat_blue = self.canvas.create_rectangle(
            31, 700, 45, 700 - (world_blue * 99 / 255),
            outline=rgb(0, 0, 255),
            fill=rgb(0, 0, 255)
        )
        self.stat_energy = self.canvas.create_rectangle(
            46, 700, 60, 700 - ((min(500, world_energy) * 99) / 500),
            outline=rgb(30, 180, 210),
            fill=rgb(30, 180, 210)
        )
        self.stat_food = self.canvas.create_rectangle(
            61, 700, 75, 700 - (world_food * 99 / 255),
            outline=rgb(180, 180, 180),
            fill=rgb(180, 180, 180)
        )


class Alive:
    def __init__(self, x, y, canvas, table, energy):
        #Технические детали
        self.canvas = canvas
        self.x = x
        self.y = y
        self.table = table

        #Характеристики
        self.energy = energy
        self.invest = 10.0
        self.movement = 0.0
        self.mult = 0.0
        self.age = 0

        #Геном
        self.speed = 1.0
        self.red_color = 255
        self.green_color = 0
        self.blue_color = 255
        self.dec_move = 3.0
        self.dec_mult = 1.0
        self.dec_noth = 0.0

        #Внесение данных
        self.table.data[self.x][self.y] = 1
        self.image = self.draw()

    def draw(self):
        return self.canvas.create_rectangle(
            self.x * 20, self.y * 20, self.x * 20 + 19, self.y * 20 + 19,
            outline=rgb(0, 0, 0), fill=rgb(self.red_color, self.green_color, self.blue_color)
        )

    def genome(self, child):
        child.speed = self.speed + np.random.uniform(-0.05, 0.05)
        child.red_color = max(0, min(255, self.red_color + np.random.randint(-20, 20)))
        child.green_color = max(0, min(255, self.green_color + np.random.randint(-20, 20)))
        child.blue_color = max(0, min(255, self.blue_color + np.random.randint(-20, 20)))
        child.dec_move = max(0, self.dec_move + np.random.uniform(-0.03, 0.03))
        child.dec_mult = max(0, self.dec_move + np.random.uniform(-0.03, 0.03))
        child.dec_noth = max(0, self.dec_move + np.random.uniform(-0.03, 0.03))
        child.canvas.delete(child.image)
        child.image = child.draw()

    def dec_normalize(self):
        dec_move_new = self.dec_move / (self.dec_move + self.dec_mult + self.dec_noth)
        dec_mult_new = self.dec_move / (self.dec_move + self.dec_mult + self.dec_noth)
        dec_noth_new = self.dec_move / (self.dec_move + self.dec_mult + self.dec_noth)
        self.dec_move = dec_move_new
        self.dec_mult = dec_mult_new
        self.dec_noth = dec_noth_new

    def next(self):
        self.dec_normalize()
        self.age += 1
        self.energy += (((255 - self.red_color) + (255 - self.blue_color) + self.green_color) / 510) * photo_eff
        self.energy -= 0.1 + (0.7 * (0.05 + self.speed)) + (0.01 * self.age)
        if self.age > 80 + (40 / self.speed):
            self.death()
            return
        if self.table.food_data[self.x][self.y] > 0:
            self.eat()
        if self.energy <= 0:
            self.energy += (self.movement * 0.25) + (self.mult * 0.5)
            self.movement = 0
            self.mult = 0
            if self.energy <= 0:
                self.death()
                return
        if self.energy > self.invest:
            self.energy -= self.invest * (1 - self.dec_noth)
            self.movement += self.invest * self.dec_move
            self.mult += self.invest * self.dec_mult
        if self.movement >= 5 * (1 / (0.2 + self.speed)):
            if self.move(move_dict[np.random.randint(0, 4)]):
                self.movement -= 5 * (1 / (0.2 + self.speed))
        if self.mult >= 50:
            if self.multiply():
                self.mult -= 50

    def death(self):
        self.table.data[self.x][self.y] = 0
        self.canvas.delete(self.image)
        self.table.life.remove(self)
        self.table.food_data[self.x][self.y] += 15 + self.energy

    def eat(self):
        if self.table.food_data[self.x][self.y] >= 7.5:
            self.table.food_data[self.x][self.y] -= 7.5
            self.energy += 7.5 * 0.98
        else:
            self.energy += self.table.food_data[self.x][self.y] * 0.98
            self.table.food_data[self.x][self.y] = 0

    def multiply(self):
        t = [0, 0, 0, 0]
        if self.table.isfree(self.x, self.y - 1):
            t[0] = 1
        if self.table.isfree(self.x + 1, self.y):
            t[1] = 1
        if self.table.isfree(self.x, self.y + 1):
            t[2] = 1
        if self.table.isfree(self.x - 1, self.y):
            t[3] = 1
        n = t.count(1)
        if n == 0:
            return False
        p = [t[i] * (1 / n) for i in range(0, 4)]
        direction = np.random.choice(move_dict, p=p)
        if direction == 'up':
            child = Alive(self.x, self.y - 1, self.canvas, self.table, 45)
            self.table.life.append(child)
            self.genome(child)
            return True
        if direction == 'right':
            child = Alive(self.x + 1, self.y, self.canvas, self.table, 45)
            self.table.life.append(child)
            self.genome(child)
            return True
        if direction == 'down':
            child = Alive(self.x, self.y + 1, self.canvas, self.table, 45)
            self.table.life.append(child)
            self.genome(child)
            return True
        if direction == 'left':
            child = Alive(self.x - 1, self.y, self.canvas, self.table, 45)
            self.table.life.append(child)
            self.genome(child)
            return True

    def move(self, direction):
        if direction == 'up':
            if self.table.isfree(self.x, self.y - 1):
                self.table.data[self.x][self.y] = 0
                self.y -= 1
                self.table.data[self.x][self.y] = 1
            else:
                return False
        if direction == 'down':
            if self.table.isfree(self.x, self.y + 1):
                self.table.data[self.x][self.y] = 0
                self.y += 1
                self.table.data[self.x][self.y] = 1
            else:
                return False
        if direction == 'left':
            if self.table.isfree(self.x - 1, self.y):
                self.table.data[self.x][self.y] = 0
                self.x -= 1
                self.table.data[self.x][self.y] = 1
            else:
                return False
        if direction == 'right':
            if self.table.isfree(self.x + 1, self.y):
                self.table.data[self.x][self.y] = 0
                self.x += 1
                self.table.data[self.x][self.y] = 1
            else:
                return False
        self.canvas.delete(self.image)
        self.image = self.draw()
        return True


def rgb(red, green, blue):
    red = int(max(0, min(255, red)))
    green = int(max(0, min(255, green)))
    blue = int(max(0, min(255, blue)))
    rt = ''
    gt = ''
    bt = ''
    if red < 16: rt = '0'
    if green < 16: gt = '0'
    if blue < 16: bt = '0'
    return '#' + rt + hex(red)[2:] + gt + hex(green)[2:] + bt + hex(blue)[2:]


def main():
    canvas = tkinter.Canvas(root, width=1000, height=700, bg='white')
    #canvas.pack(fill=tkinter.BOTH, expand=0)
    canvas.place(x=0, y=0, width=1000, height=700)
    canvas.create_line(0, 600, 1000, 600, fill=rgb(0, 0, 0))
    canvas.create_line(151, 600, 151, 700, fill=rgb(0, 0, 0))
    canvas.create_line(800, 0, 800, 600, fill=rgb(0, 0, 0))
    table = Table(canvas, 40, 30)
    #Объявление кнопок
    tm1 = tkinter.Radiobutton(text='Выключить всё', variable=table_mode, value=0, bg='white',
                              command=lambda i=table: table.change_mode()).place(x=806, y=10)
    tm2 = tkinter.Radiobutton(text='Отобразить богатство органикой', variable=table_mode, value=1, bg='white',
                              command=lambda i=table: table.change_mode()).place(x=806, y=30)
    #tm3 = tkinter.Radiobutton(text='Выключить всё', variable=table_mod, value=0, bg='white').place(x=806, y=10)
    while len(table.life) > 0:
        time.sleep(0.08)
        table.next()
        root.update()
    root.mainloop()


if __name__ == '__main__':
    main()
