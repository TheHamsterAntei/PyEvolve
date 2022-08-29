#Version 1.1.1
import tkinter
import time
import learning
import numpy as np

root = tkinter.Tk()
root.title("Evolve")
root.geometry("1200x800")
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
        self.life = [Alive(np.random.randint(0, self.width), np.random.randint(0, self.height), canvas, self, 100)]
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
        self.stat_count = [None for i in range(0, 262)]
        self.stat_count_value = [0 for i in range(0, 262)]
        self.stat_photo = None
        self.draw_stats()

    def change_mode(self):
        mode = table_mode.get()
        if mode != 1:
            self.undraw_food()
        if mode == 1:
            self.draw_food()

    def next(self):
        self.step += 1
        global photo_eff
        photo_eff = 1.2 * np.sin((self.step % (900 * np.pi)) / 900)
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
                self.food_data[i][j] += np.random.choice(
                    [0, np.random.uniform(0.01, 0.05), np.random.uniform(0.03, 0.25), 1.0],
                    p=[0.1, 0.15, 0.72, 0.03])
                if self.food_data[i][j] > 215:
                    t = [0, 0, 0, 0]
                    if j > 0:
                        t[0] = 1
                    if i < self.width - 1:
                        t[1] = 1
                    if j < self.height - 1:
                        t[2] = 1
                    if i > 0:
                        t[3] = 1
                    n = t.count(1)
                    if n > 0:
                        r = (self.food_data[i][j] - 215) / n
                        self.food_data[i][j] = 215
                        if t[0] == 1:
                            self.food_data[i][j - 1] += r
                        if t[1] == 1:
                            self.food_data[i + 1][j] += r
                        if t[2] == 1:
                            self.food_data[i][j + 1] += r
                        if t[3] == 1:
                            self.food_data[i - 1][j] += r


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
        if self.stat_photo != None:
            self.canvas.delete(self.stat_photo)
        world_red = 0
        world_green = 0
        world_blue = 0
        world_energy = 0
        world_food = 0
        if self.step % 50 == 0:
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
                    152 + (i * 4), 800, 155 + (i * 4), 800 - value,
                    outline=rgb(510 - (value * 5.1), value * 5.1, 0),
                    fill=rgb(510 - (value * 5.1), value * 5.1, 0)
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
            0, 800, 15, 800 - (world_red * 99 / 255),
            outline=rgb(255, 0, 0),
            fill=rgb(255, 0, 0)
        )
        self.stat_green = self.canvas.create_rectangle(
            16, 800, 30, 800 - (world_green * 99 / 255),
            outline=rgb(0, 255, 0),
            fill=rgb(0, 255, 0)
        )
        self.stat_blue = self.canvas.create_rectangle(
            31, 800, 45, 800 - (world_blue * 99 / 255),
            outline=rgb(0, 0, 255),
            fill=rgb(0, 0, 255)
        )
        self.stat_energy = self.canvas.create_rectangle(
            46, 800, 60, 800 - ((min(500, world_energy) * 99) / 500),
            outline=rgb(30, 180, 210),
            fill=rgb(30, 180, 210)
        )
        self.stat_food = self.canvas.create_rectangle(
            61, 800, 75, 800 - (world_food * 99 / 255),
            outline=rgb(180, 180, 180),
            fill=rgb(180, 180, 180)
        )
        self.stat_photo = self.canvas.create_rectangle(
            76, 800, 90, 800 - (photo_eff * 99 / 1.2),
            outline=rgb(180, 180, 180),
            fill=rgb(160, 140, 30)
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
        #Инвестиции
        self.dec_move = 3.0
        self.dec_mult = 1.0
        self.dec_noth = 0.0

        #Генетические характеристики
        self.speed = 1.0
        self.membrane = 0.5
        #Цвет
        self.red_color = 255
        self.green_color = 0
        self.blue_color = 255
        #Интеллект
        if energy != 45:
            self.neuro = learning.NeuralNet(learning.generate_layers([6, 8, 3]))
        else:
            self.neuro = None

        #Генетические свойства
        self.can_photo = 0 #Может ли питаться от энергии солнца
        self.can_assim = 1 #Может ли питаться от органики в почве

        #Внесение данных
        self.table.data[self.x][self.y] = 1
        self.image = self.draw()

    def draw(self):
        image = [self.canvas.create_rectangle(
            self.x * 20, self.y * 20, self.x * 20 + 19, self.y * 20 + 19,
            outline=rgb(0, 0, 0), fill=rgb(self.red_color, self.green_color, self.blue_color))]
        if self.can_photo == 1:
            image.append(self.canvas.create_line(self.x * 20, self.y * 20, self.x * 20 + 19, self.y * 20 + 19,
                                             fill=rgb(0, 0, 0)))
        if self.can_assim == 1:
            image.append(self.canvas.create_line(self.x * 20 + 19, self.y * 20, self.x * 20, self.y * 20 + 19,
                                             fill=rgb(0, 0, 0)))
        return image

    def genome(self, child):
        major_mutate = np.random.choice([0, 1, 2], p=[0.985, 0.014, 0.001])
        if major_mutate == 0:
            child.speed = self.speed + np.random.choice([-0.01, 0, 0.01], p=[0.05, 0.90, 0.05])
            child.red_color = max(0, min(255, self.red_color +
                                         np.random.choice([-2, -1, 0, 1, 2], p=[0.03, 0.05, 0.84, 0.05, 0.03])))
            child.green_color = max(0, min(255, self.green_color +
                                           np.random.choice([-2, -1, 0, 1, 2], p=[0.03, 0.05, 0.84, 0.05, 0.03])))
            child.blue_color = max(0, min(255, self.blue_color +
                                          np.random.choice([-2, -1, 0, 1, 2], p=[0.03, 0.05, 0.84, 0.05, 0.03])))
            child.dec_move = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.03, 0.94, 0.03]))
            child.dec_mult = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.03, 0.94, 0.03]))
            child.dec_noth = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.03, 0.94, 0.03]))
            child.can_photo = np.random.choice([self.can_photo, (self.can_photo + 1) % 2], p=[0.998, 0.002])
            child.can_assim = np.random.choice([self.can_assim, (self.can_assim + 1) % 2], p=[0.998, 0.002])
            child.membrane = self.membrane + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10])
            child.neuro = self.neuro.copy().mutate_weights(0.001)
        if major_mutate == 1:
            child.speed = self.speed + np.random.choice([-0.05, 0, 0.05], p=[0.30, 0.40, 0.30])
            child.red_color = max(0, min(255, self.red_color +
                                         np.random.choice([-5, -3, 0, 3, 5], p=[0.15, 0.25, 0.20, 0.25, 0.15])))
            child.green_color = max(0, min(255, self.green_color +
                                           np.random.choice([-5, -3, 0, 3, 5], p=[0.15, 0.25, 0.20, 0.25, 0.15])))
            child.blue_color = max(0, min(255, self.blue_color +
                                          np.random.choice([-5, -3, 0, 3, 5], p=[0.15, 0.25, 0.20, 0.25, 0.15])))
            child.dec_move = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10]))
            child.dec_mult = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10]))
            child.dec_noth = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10]))
            child.can_photo = np.random.choice([self.can_photo, (self.can_photo + 1) % 2], p=[0.995, 0.005])
            child.can_assim = np.random.choice([self.can_assim, (self.can_assim + 1) % 2], p=[0.995, 0.005])
            child.membrane = self.membrane + np.random.choice([-0.02, 0, 0.02], p=[0.25, 0.50, 0.25])
            child.neuro = self.neuro.copy().mutate_weights(0.005)
        if major_mutate == 2:
            child.speed = self.speed + np.random.choice([-0.01, 0, 0.01], p=[0.05, 0.90, 0.05])
            swap = np.random.choice([0, 1, 2])
            if swap == 0:
                child.red_color, child.green_color = self.green_color, self.red_color
            if swap == 1:
                child.red_color, child.blue_color = self.blue_color, self.red_color
            if swap == 2:
                child.blue_color, child.green_color = self.green_color, self.blue_color
            child.dec_move = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.03, 0.94, 0.03]))
            child.dec_mult = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.03, 0.94, 0.03]))
            child.dec_noth = max(0, self.dec_move + np.random.choice([-0.01, 0, 0.01], p=[0.03, 0.94, 0.03]))
            child.can_photo = np.random.choice([self.can_photo, (self.can_photo + 1) % 2], p=[0.998, 0.002])
            child.can_assim = np.random.choice([self.can_assim, (self.can_assim + 1) % 2], p=[0.998, 0.002])
            child.membrane = self.membrane + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10])
            child.neuro = self.neuro.copy().mutate_weights(0.001)
        #Основные характеристики
        child.speed = max(0, min(5.0, child.speed))
        child.membrane = max(0.1, min(10.0, child.membrane))
        # Цвет
        child.red_color = max(0, min(255, child.red_color))
        child.green_color = max(0, min(255, child.green_color))
        child.blue_color = max(0, min(255, child.blue_color))
        # Интеллект
        child.dec_move = max(0, child.dec_move)
        child.dec_mult = max(0, child.dec_mult)
        child.dec_noth = max(0, child.dec_noth)
        for i in child.image:
            child.canvas.delete(i)
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
        if self.can_photo == 1:
            self.energy += (((255 - self.red_color) + (255 - self.blue_color) + self.green_color) / 510) * photo_eff
        self.energy -= 0.1 + (0.4 * self.speed) + (0.02 * self.age) + (0.3 * self.can_photo) + (0.3 * self.can_assim) \
                       - (0.1 * self.membrane)
        if self.age > 80 + (40 / self.speed) + (50 * self.membrane):
            self.death()
            return
        if self.can_assim == 1:
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
            if self.neuro != None:
                result = self.look_around()
                result.append(self.energy)
                decisions = self.neuro.get_output(result)
                self.dec_move = decisions[0]
                self.dec_mult = decisions[1]
                self.dec_noth = decisions[2]
                self.dec_normalize()
            self.energy -= self.invest * (1 - self.dec_noth)
            if self.movement < 3 * (5.0 * (1 / (0.2 + self.speed)) + (2.0 * self.membrane)):
                self.movement += self.invest * self.dec_move
            else:
                self.energy += self.invest * self.dec_mult
            if self.mult < 1.5 * (45 + 5 * (0.5 + self.membrane)):
                self.mult += self.invest * self.dec_mult
            else:
                self.energy += self.invest * self.dec_mult
        if self.movement >= 5.0 * (1 / (0.2 + self.speed)) + (2.0 * self.membrane):
            if self.move(move_dict[np.random.randint(0, 4)]):
                self.movement -= 5.0 * (1 / (0.2 + self.speed)) + (2.0 * self.membrane)
        if self.mult >= 45 + 5 * (0.5 + self.membrane):
            if self.neuro != None:
                if self.multiply():
                    self.mult -= 45 + 5 * (0.5 + self.membrane)
            else:
                self.red_color = 255
                self.green_color = 255
                self.blue_color = 255

    def look_around(self):
        output = [self.table.food_data[self.x][self.y]]
        if self.table.isfree(self.x, self.y - 1):
            output.append(1)
        else:
            output.append(0)
        if self.table.isfree(self.x + 1, self.y):
            output.append(1)
        else:
            output.append(0)
        if self.table.isfree(self.x, self.y + 1):
            output.append(1)
        else:
            output.append(0)
        if self.table.isfree(self.x - 1, self.y):
            output.append(1)
        else:
            output.append(0)
        return output

    def death(self):
        self.table.data[self.x][self.y] = 0
        for i in self.image:
            self.canvas.delete(i)
        self.table.life.remove(self)
        self.table.food_data[self.x][self.y] += 15 + self.energy

    def eat(self):
        if self.table.food_data[self.x][self.y] >= 7.5:
            self.table.food_data[self.x][self.y] -= 7.5
            self.energy += 7.5 * 0.85
        else:
            self.energy += self.table.food_data[self.x][self.y] * 0.85
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
        for i in self.image:
            self.canvas.delete(i)
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
    countdown = 200
    canvas = tkinter.Canvas(root, width=1200, height=800, bg='white')
    #canvas.pack(fill=tkinter.BOTH, expand=0)
    canvas.place(x=0, y=0, width=1200, height=800)
    canvas.create_line(0, 700, 12000, 700, fill=rgb(0, 0, 0))
    canvas.create_line(151, 700, 151, 800, fill=rgb(0, 0, 0))
    canvas.create_line(1000, 0, 1000, 700, fill=rgb(0, 0, 0))
    table = Table(canvas, 50, 35)
    #Объявление кнопок
    tm1 = tkinter.Radiobutton(text='Выключить всё', variable=table_mode, value=0, bg='white',
                              command=lambda i=table: table.change_mode()).place(x=1006, y=10)
    tm2 = tkinter.Radiobutton(text='Отобразить богатство органикой', variable=table_mode, value=1, bg='white',
                              command=lambda i=table: table.change_mode()).place(x=1006, y=30)
    #tm3 = tkinter.Radiobutton(text='Выключить всё', variable=table_mod, value=0, bg='white').place(x=806, y=10)
    while True:
        time.sleep(0.08)
        if len(table.life) > 0:
            table.next()
        else:
            if countdown == 0:
                table.life.append(Alive(np.random.randint(0, table.width), np.random.randint(0, table.height), canvas,
                                        table, 100))
                countdown = 200
            else:
                countdown -= 1
        root.update()
    root.mainloop()


if __name__ == '__main__':
    main()
