#Version 1.2.7
import tkinter
import time
import learning
import numpy as np

root = tkinter.Tk()
root.title("Evolve")
root.geometry("1200x800")
move_dict = ['up', 'right', 'down', 'left']
photo_eff = 1.0
mutation_mult = 22.5
table_mode = tkinter.IntVar()
table_mode.set(1)
cell_size = 14
fps = 30

zoom = 1.0
screen_w = 1008
screen_h = 700

offset_x = 0
offset_y = 0

class Table:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.data = [[0 for j in range(0, height)] for i in range(0, width)]
        self.life = [Alive(np.random.randint(0, self.width), np.random.randint(0, self.height), canvas, self, 100, 0)]
        self.food_data = [[0 for j in range(0, height)] for i in range(0, width)]
        for i in range(0, width):
            for j in range(0, height):
                if i < int(width / 2) - 1 and j < int(height / 2) - 1:
                    self.food_data[i][j] = np.random.uniform(10, 100)
                    continue
                if i < int(width / 2) - 1 and j > int(height / 2) + 1:
                    self.food_data[i][j] = np.random.uniform(5, 50)
                    continue
                if i > int(width / 2) + 1 and j < int(height / 2) - 1:
                    self.food_data[i][j] = np.random.uniform(5, 50)
                    continue
                if i > int(width / 2) + 1 and j > int(height / 2) + 1:
                    self.food_data[i][j] = np.random.uniform(1, 10)
                    continue
        self.food_data_images = [[None for j in range(0, height)] for i in range(0, width)]
        self.food_mult = 1.0
        self.step = 0
        if table_mode.get() == 1:
            self.draw_food()
        self.create_life()

        #Статистика
        self.stat_red = None
        self.stat_green = None
        self.stat_blue = None
        self.stat_energy = None
        self.stat_food = None
        self.stat_count = [None for i in range(0, 262)]
        self.stat_count_value = [0 for i in range(0, 262)]
        self.stat_photo = None
        self.stat_fps = None
        self.draw_stats()

        #Управление
        canvas.master.bind('<MouseWheel>', self.zoom_change)
        canvas.master.bind('<Button-4>', self.zoom_change)
        canvas.master.bind('<Button-5>', self.zoom_change)
        canvas.master.bind('<Key>', self.key_pressed)

    def change_mode(self):
        mode = table_mode.get()
        if mode != 1:
            self.undraw_food()
        if mode == 1:
            self.draw_food()
            for i in self.life:
                for j in i.image:
                    self.canvas.delete(j)
                i.image = i.draw()

    def create_life(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                if self.isfree(i, j):
                    if np.random.choice([0, 1], p=[0.98, 0.02]):
                        self.life.append(Alive(i, j, self.canvas, self, 100, 0))

    def draw_food(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                x1 = i * cell_size - offset_x
                y1 = j * cell_size - offset_y
                x2 = (i + 1) * cell_size - 1 - offset_x
                y2 = (j + 1) * cell_size - 1 - offset_y
                color = self.food_data[i][j]
                color = max(0, min(255, color))
                if x1 >= screen_w or y1 >= screen_h or x2 < 0 or y2 < 0 or self.data[i][j] == 1:
                    self.canvas.itemconfig(self.food_data_images[i][j], state="hidden")
                    continue
                self.canvas.itemconfig(self.food_data_images[i][j], state="normal")
                if self.food_data_images[i][j] == None:
                    self.food_data_images[i][j] = self.canvas.create_rectangle(
                        max(0, x1),
                        max(0, y1),
                        min(screen_w - 2, x2),
                        min(screen_h - 2, y2),
                        outline=rgb(255 - int(color), 255 - int(color), 255 - int(color)),
                        fill=rgb(255 - int(color), 255 - int(color), 255 - int(color))
                    )
                else:
                    if self.food_data_images[i][j]!=None:
                        self.canvas.itemconfig(self.food_data_images[i][j],
                                               outline=rgb(255 - int(color), 255 - int(color), 255 - int(color)),
                                               fill=rgb(255 - int(color), 255 - int(color), 255 - int(color)))
                        self.canvas.coords(self.food_data_images[i][j], max (0, x1), max(0, y1),
                                           min(screen_w - 1, x2),
                                           min(screen_h - 1, y2))

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
        if self.stat_fps != None:
            self.canvas.delete(self.stat_fps)
        world_red = 0
        world_green = 0
        world_blue = 0
        world_energy = 0
        world_food = 0
        if self.step % 10 == 0:
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
            46, 800, 60, 800 - ((min(200, world_energy) * 99) / 200),
            outline=rgb(30, 180, 210),
            fill=rgb(30, 180, 210)
        )
        self.stat_food = self.canvas.create_rectangle(
            61, 800, 75, 800 - (world_food * 99 / 255),
            outline=rgb(180, 180, 180),
            fill=rgb(180, 180, 180)
        )
        self.stat_photo = self.canvas.create_rectangle(
            76, 800, 90, 800 - (photo_eff * 99 / 1.0),
            outline=rgb(180, 180, 180),
            fill=rgb(160, 140, 30)
        )
        self.stat_fps = self.canvas.create_text(
            1014, 685,
            text="FPS: " + str(int(fps * 1000) / 1000),
            anchor="w",
            font='Calibri 14'
        )

    def draw_stats_update(self):
        world_red = 0
        world_green = 0
        world_blue = 0
        world_energy = 0
        world_food = 0
        if self.step % 10 == 0:
            self.stat_count_value.pop()
            self.stat_count_value.insert(0, len(self.life))
            value_max = 0
            for i in range(0, len(self.stat_count_value)):
                if self.stat_count_value[i] > value_max:
                    value_max = self.stat_count_value[i]
            for i in range(0, len(self.stat_count)):
                value = (self.stat_count_value[i] / value_max) * 99
                self.canvas.itemconfig(self.stat_count[i],
                                       outline=rgb(510 - (value * 5.1), value * 5.1, 0),
                                       fill=rgb(510 - (value * 5.1), value * 5.1, 0))
                self.canvas.coords(self.stat_count[i], 152 + (i * 4), 800, 155 + (i * 4), 800 - value)
        for i in self.life:
            world_red += i.red_color / len(self.life)
            world_green += i.green_color / len(self.life)
            world_blue += i.blue_color / len(self.life)
            world_energy += i.energy / len(self.life)
        for i in range(0, len(self.food_data)):
            for j in range(0, len(self.food_data[i])):
                world_food += self.food_data[i][j] / (self.width * self.height)
        self.canvas.coords(self.stat_red, 0, 800, 15, 800 - (world_red * 99 / 255))
        self.canvas.coords(self.stat_green, 16, 800, 30, 800 - (world_green * 99 / 255))
        self.canvas.coords(self.stat_blue, 31, 800, 45, 800 - (world_blue * 99 / 255))
        self.canvas.coords(self.stat_energy, 46, 800, 60, 800 - ((min(200, world_energy) * 99) / 200))
        self.canvas.coords(self.stat_food, 61, 800, 75, 800 - (world_food * 99 / 255))
        self.canvas.coords(self.stat_photo, 76, 800, 90, 800 - (photo_eff * 99 / 1.0))
        self.canvas.itemconfig(self.stat_fps, text="FPS: " + str(int(fps * 1000) / 1000))

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
                mult = 0.0
                if self.data[i][j] == 0:
                    if i < int(self.width / 2) - 1 and j < int(self.height / 2) - 1:
                        mult = max(0.0, 2.0 - self.food_data[i][j] / 100) * self.food_mult
                    if i < int(self.width / 2) - 1 and j > int(self.height / 2) + 1:
                        mult = max(0.0, 1.0 - self.food_data[i][j] / 200) * self.food_mult
                    if i > int(self.width / 2) + 1 and j < int(self.height / 2) - 1:
                        mult = max(0.0, 1.0 - self.food_data[i][j] / 200) * self.food_mult
                    if i > int(self.width / 2) + 1 and j > int(self.height / 2) + 1:
                        mult = max(0.0, 0.5 - self.food_data[i][j] / 400) * self.food_mult
                self.food_data[i][j] += np.random.choice(
                    [0, np.random.uniform(0.01, 0.05), np.random.uniform(0.03, 0.25), 1.0],
                    p=[0.1, 0.15, 0.72, 0.03]) * mult
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
                    else:
                        if self.food_data[i][j] > 255:
                            self.food_data[i][j] = 255

    def key_pressed(self, event):
        global offset_x
        global offset_y
        if event.keysym == 'Right':
            offset_x += 14
        if event.keysym == 'Left':
            offset_x -= 14
        if event.keysym == 'Up':
            offset_y -= 14
        if event.keysym == 'Down':
            offset_y += 14
        if table_mode == 1:
            self.draw_food()
        for i in self.life:
            i.draw_update()

    def next(self):
        self.step += 1
        global photo_eff
        global mutation_mult
        photo_eff = 1.0 * np.sin((self.step % (900 * np.pi)) / 900)
        if mutation_mult > 0.65:
            mutation_mult *= 0.99
        if self.food_mult > 0.40:
            self.food_mult *= 0.995
        for i in self.life:
            i.next()
        self.food_refresh()
        if table_mode.get() == 1:
            self.draw_food()
        self.draw_stats_update()

    def undraw_food(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                if self.food_data_images[i][j] != None:
                    self.canvas.delete(self.food_data_images[i][j])
                    self.food_data_images[i][j] = None

    def zoom_change(self, event):
        global zoom
        global cell_size
        global offset_x
        global offset_y
        prev_zoom = zoom
        if event.delta < 0 or event.num == 5:
            if zoom > 1.0:
                zoom /= 1.35
            if zoom < 1.0:
                zoom = 1.0
        if event.delta > 0 or event.num == 4:
            if zoom < 10.0:
                zoom *= 1.35
            if zoom > 10.0:
                zoom = 10.0
        cell_size = 14 * zoom
        offset_x = (offset_x + event.x) * (zoom / prev_zoom) - event.x
        offset_y = (offset_y + event.y) * (zoom / prev_zoom) - event.y
        if table_mode.get() == 1:
            self.draw_food()
        for i in self.life:
            i.draw_update()


class Alive:
    def __init__(self, x, y, canvas, table, energy, parent):
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
        if parent == 0:
            self.neuro_invest = learning.NeuralNet(learning.generate_layers([4, 3]))
            self.neuro_move = learning.NeuralNet(learning.generate_layers([5, 4]))

        #Генетические свойства
        self.can_photo = 0 #Может ли питаться от энергии солнца
        self.can_assim = 1 #Может ли питаться от органики в почве

        #Внесение данных
        self.table.data[self.x][self.y] = 1
        self.image = self.draw()

    def dec_normalize(self):
        dec_move_new = self.dec_move / (self.dec_move + self.dec_mult + self.dec_noth)
        dec_mult_new = self.dec_mult / (self.dec_move + self.dec_mult + self.dec_noth)
        dec_noth_new = self.dec_noth / (self.dec_move + self.dec_mult + self.dec_noth)
        self.dec_move = dec_move_new
        self.dec_mult = dec_mult_new
        self.dec_noth = dec_noth_new

    def death(self):
        self.table.data[self.x][self.y] = 0
        for i in self.image:
            self.canvas.delete(i)
        self.table.life.remove(self)
        self.table.food_data[self.x][self.y] += 15 + self.energy

    def draw(self):
        x1 = self.x * cell_size - offset_x
        y1 = self.y * cell_size - offset_y
        x2 = (self.x + 1) * cell_size - offset_x - 1
        y2 = (self.y + 1) * cell_size - offset_y - 1
        if x1 < screen_w and y1 < screen_h and x2 > 0 and y2 > 0:
            image = [self.canvas.create_rectangle(
                max(0, x1),
                max(0, y1),
                min(screen_w, x2),
                min(screen_h, y2),
                outline=rgb(0, 0, 0), fill=rgb(self.red_color, self.green_color, self.blue_color),
                tag="main_rect")]
            if self.can_photo == 1:
                a = check_line_visibility(x1, y1, x2, y2)
                if a[0]:
                    x3, y3, x4, y4 = a[1], a[2], a[3], a[4]
                    image.append(self.canvas.create_line(x3, y3, x4, y4, fill=rgb(0, 0, 0),
                                                         tag="can_photo"))
            if self.can_assim == 1:
                a = check_line_visibility(x1, y2, x2, y1)
                if a[0]:
                    x3, y3, x4, y4 = a[1], a[2], a[3], a[4]
                    image.append(self.canvas.create_line(x3, y3, x4, y4, fill=rgb(0, 0, 0),
                                                         tag="can_assim"))
        else:
            image = []
        return image

    def draw_update(self):
        x1 = self.x * cell_size - offset_x
        y1 = self.y * cell_size - offset_y
        x2 = (self.x + 1) * cell_size - offset_x - 1
        y2 = (self.y + 1) * cell_size - offset_y - 1
        if self.image == [] and x1 < screen_w and y1 < screen_h and x2 > 0 and y2 > 0:
            self.image = self.draw()
            return
        if x1 < screen_w and y1 < screen_h and x2 > 0 and y2 > 0:
            for i in self.image:
                self.canvas.itemconfig(i, state="normal")
                if self.canvas.gettags(i) == ("main_rect",):
                    self.canvas.coords(i, max(0, x1), max(0, y1),
                                        min(screen_w, x2), min(screen_h, y2))
                if self.canvas.gettags(i) == ("can_photo",):
                    a = check_line_visibility(x1, y1, x2, y2)
                    if a[0]:
                        x3, y3, x4, y4 = a[1], a[2], a[3], a[4]
                        self.canvas.coords(i, x3, y3, x4, y4)
                    else:
                        self.canvas.coords(i, 1008, 700, 1009, 700)
                if self.canvas.gettags(i) == ("can_assim",):
                    a = check_line_visibility(x1, y2, x2, y1)
                    if a[0]:
                        x3, y3, x4, y4 = a[1], a[2], a[3], a[4]
                        self.canvas.coords(i, x3, y3, x4, y4)
                    else:
                        self.canvas.coords(i, 1008, 700, 1009, 700)
        else:
            for i in self.image:
                self.canvas.itemconfig(i, state="hidden")

    def eat(self):
        if self.table.food_data[self.x][self.y] >= 8.0:
            self.table.food_data[self.x][self.y] -= 8.0
            self.energy += 8.0 * 0.85
        else:
            self.energy += self.table.food_data[self.x][self.y] * 0.85
            self.table.food_data[self.x][self.y] = 0

    def genome(self, child):
        major_mutate = np.random.choice([0, 1, 2], p=[0.985, 0.014, 0.001])
        if major_mutate == 0:
            child.speed = self.speed + np.random.choice([-0.01, 0, 0.01], p=[0.05, 0.90, 0.05]) * mutation_mult
            child.red_color = max(0, min(255, self.red_color +
                                         np.random.choice([-2, -1, 0, 1, 2], p=[0.03, 0.05, 0.84, 0.05, 0.03])
                                         * mutation_mult))
            child.green_color = max(0, min(255, self.green_color +
                                           np.random.choice([-2, -1, 0, 1, 2], p=[0.03, 0.05, 0.84, 0.05, 0.03])
                                           * mutation_mult))
            child.blue_color = max(0, min(255, self.blue_color +
                                          np.random.choice([-2, -1, 0, 1, 2], p=[0.03, 0.05, 0.84, 0.05, 0.03])
                                          * mutation_mult))
            child.can_photo = np.random.choice([self.can_photo, (self.can_photo + 1) % 2], p=[0.998, 0.002])
            child.can_assim = np.random.choice([self.can_assim, (self.can_assim + 1) % 2], p=[0.998, 0.002])
            child.membrane = self.membrane + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10]) * mutation_mult
            new_neuro = self.neuro_invest.copy()
            new_neuro.mutate_weights(0.01 * mutation_mult)
            child.neuro_invest = new_neuro
            new_neuro = self.neuro_move.copy()
            new_neuro.mutate_weights(0.01 * mutation_mult)
            child.neuro_move = new_neuro
        if major_mutate == 1:
            child.speed = self.speed + np.random.choice([-0.05, 0, 0.05], p=[0.30, 0.40, 0.30]) * mutation_mult
            child.red_color = max(0, min(255, self.red_color +
                                         np.random.choice([-5, -3, 0, 3, 5], p=[0.15, 0.25, 0.20, 0.25, 0.15])
                                         * mutation_mult))
            child.green_color = max(0, min(255, self.green_color +
                                           np.random.choice([-5, -3, 0, 3, 5], p=[0.15, 0.25, 0.20, 0.25, 0.15])
                                           * mutation_mult))
            child.blue_color = max(0, min(255, self.blue_color +
                                          np.random.choice([-5, -3, 0, 3, 5], p=[0.15, 0.25, 0.20, 0.25, 0.15])
                                          * mutation_mult))
            child.can_photo = np.random.choice([self.can_photo, (self.can_photo + 1) % 2], p=[0.995, 0.005])
            child.can_assim = np.random.choice([self.can_assim, (self.can_assim + 1) % 2], p=[0.995, 0.005])
            child.membrane = self.membrane + np.random.choice([-0.02, 0, 0.02], p=[0.25, 0.50, 0.25]) * mutation_mult
            new_neuro = self.neuro_invest.copy()
            new_neuro.mutate_weights(0.05 * mutation_mult)
            child.neuro_invest = new_neuro
            new_neuro = self.neuro_move.copy()
            new_neuro.mutate_weights(0.05 * mutation_mult)
            child.neuro_move = new_neuro
        if major_mutate == 2:
            child.speed = self.speed + np.random.choice([-0.01, 0, 0.01], p=[0.05, 0.90, 0.05]) * mutation_mult
            swap = np.random.choice([0, 1, 2])
            if swap == 0:
                child.red_color, child.green_color = self.green_color, self.red_color
            if swap == 1:
                child.red_color, child.blue_color = self.blue_color, self.red_color
            if swap == 2:
                child.blue_color, child.green_color = self.green_color, self.blue_color
            child.can_photo = np.random.choice([self.can_photo, (self.can_photo + 1) % 2], p=[0.998, 0.002])
            child.can_assim = np.random.choice([self.can_assim, (self.can_assim + 1) % 2], p=[0.998, 0.002])
            child.membrane = self.membrane + np.random.choice([-0.01, 0, 0.01], p=[0.10, 0.80, 0.10]) * mutation_mult
            new_neuro = self.neuro_invest.copy()
            new_neuro.mutate_weights(0.01 * mutation_mult)
            child.neuro_invest = new_neuro
            new_neuro = self.neuro_move.copy()
            new_neuro.mutate_weights(0.01 * mutation_mult)
            child.neuro_move = new_neuro
        #Основные характеристики
        child.speed = max(0.0, min(5.0, child.speed))
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

    def look_around(self):
        output = [self.table.food_data[self.x][self.y] / 255]
        space = 0
        if self.table.isfree(self.x, self.y - 1):
            space += 0.25
        if self.table.isfree(self.x + 1, self.y):
            space += 0.25
        if self.table.isfree(self.x, self.y + 1):
            space += 0.25
        if self.table.isfree(self.x - 1, self.y):
            space += 0.25
        output.append(space)
        return output

    def look_for_food(self):
        output = [self.table.food_data[self.x][self.y] / 255]
        if self.table.isfree(self.x, self.y - 1):
            output.append(self.table.food_data[self.x][self.y - 1] / 255)
        else:
            output.append(0)
        if self.table.isfree(self.x + 1, self.y):
            output.append(self.table.food_data[self.x + 1][self.y] / 255)
        else:
            output.append(0)
        if self.table.isfree(self.x, self.y + 1):
            output.append(self.table.food_data[self.x][self.y + 1] / 255)
        else:
            output.append(0)
        if self.table.isfree(self.x - 1, self.y):
            output.append(self.table.food_data[self.x - 1][self.y] / 255)
        else:
            output.append(0)
        return output

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
        self.draw_update()
        return True

    def move_choice(self, values):
        values = sorted(enumerate(values), key=lambda n: -n[1])
        for i in range(0, 4):
            direction = values[i][0]
            if direction == 0:
                if self.table.isfree(self.x, self.y - 1):
                    return direction
                else:
                    continue
            if direction == 1:
                if self.table.isfree(self.x + 1, self.y):
                    return direction
                else:
                    continue
            if direction == 2:
                if self.table.isfree(self.x, self.y + 1):
                    return direction
                else:
                    continue
            if direction == 3:
                if self.table.isfree(self.x - 1, self.y):
                    return direction
                else:
                    continue
        return np.random.randint(0, 4)

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
            child = Alive(self.x, self.y - 1, self.canvas, self.table, 45, 1)
            self.table.life.append(child)
            self.genome(child)
            return True
        if direction == 'right':
            child = Alive(self.x + 1, self.y, self.canvas, self.table, 45, 1)
            self.table.life.append(child)
            self.genome(child)
            return True
        if direction == 'down':
            child = Alive(self.x, self.y + 1, self.canvas, self.table, 45, 1)
            self.table.life.append(child)
            self.genome(child)
            return True
        if direction == 'left':
            child = Alive(self.x - 1, self.y, self.canvas, self.table, 45, 1)
            self.table.life.append(child)
            self.genome(child)
            return True

    def next(self):
        self.age += 1
        if self.can_photo == 1:
            self.energy += (((255 - self.red_color) + (255 - self.blue_color) + self.green_color) / 510) * photo_eff
        energy_cost = 0.2 + (0.4 * self.speed) + (0.02 * self.age) + (0.3 * self.can_photo) + (0.3 * self.can_assim) \
                       - (0.1 * self.membrane)
        if energy_cost < 0.7: energy_cost = 0.7
        energy_cost += max(0.0, self.energy - 200) / 150
        energy_cost += max(0.0, self.table.food_data[self.x][self.y] - 150) / 20
        self.energy -= energy_cost
        if self.age > 150 + (50 / (0.5 + self.speed)) + (100 * self.membrane):
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
        if self.energy >= 500:
            self.energy = 50
            for i in self.table.life:
                distance = np.sqrt((i.x - self.x)**2 + (i.y - self.y)**2)
                if distance < 5.0 - i.membrane * 0.5 and i != self:
                    i.energy *= 0.5
                    i.death()
            self.death()
            return
        result = self.look_around()
        result.append(self.energy)
        result.append(photo_eff / 1.2)
        decisions = self.neuro_invest.get_output(result)
        self.dec_move = decisions[0]
        self.dec_mult = decisions[1]
        self.dec_noth = decisions[2]
        move_dir = self.move_choice(self.neuro_move.get_output(self.look_for_food()))
        self.dec_normalize()
        if self.energy > self.invest:
            if self.movement < 5 * (0.3 * (1 / (0.2 + self.speed)) + (0.05 * self.membrane)):
                self.movement += self.invest * self.dec_move
                self.energy -= self.invest * self.dec_move
            if self.mult < 1.5 * (45 + 5 * (0.5 + self.membrane)):
                self.mult += self.invest * self.dec_mult
                self.energy -= self.invest * self.dec_mult
        if self.movement >= 0.3 * (1 / (0.2 + self.speed)) + (0.05 * self.membrane):
            if self.move(move_dict[move_dir]):
                self.movement -= 0.3 * (1 / (0.2 + self.speed)) + (0.05 * self.membrane)
        if self.mult >= 45 + 5 * (0.5 + self.membrane):
            if self.multiply():
                self.mult -= 45 + 5 * (0.5 + self.membrane)

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


def check_line_visibility(x1, y1, x2, y2):
    visible = True
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    a = (y2 - y1) / (x2 - x1)
    b = y1 - (x1 * a)
    x3 = -b / a
    if y1 < y2:
        if x3 < 0:
            x3 = 0
            y3 = b
            if y3 < 0 or y3 > screen_h:
                visible = False
        else:
            y3 = 0
    else:
        if x3 > screen_w:
            x3 = screen_w
            y3 = a * x3 + b
            if y3 < 0 or y3 > screen_h:
                visible = False
        else:
            y3 = 0
    x4 = (screen_h - b) / a
    if y1 < y2:
        if x4 > screen_w:
            x4 = screen_w
            y4 = a * x4 + b
            if y4 < 0 or y4 > screen_h:
                visible = False
        else:
            y4 = screen_h
    else:
        if x4 < 0:
            x4 = 0
            y4 = b
            if y4 < 0 or y4 > screen_h:
                visible = False
        else:
            y4 = screen_h
    if x3 > x4:
        x3, x4 = x4, x3
        y3, y4 = y4, y3
    if x3 < x1: x3 = x1
    if x4 > x2: x4 = x2
    if y1 < y2:
        if y3 < y1: y3 = y1
        if y4 > y2: y4 = y2
    else:
        if y3 > y1: y3 = y1
        if y4 < y2: y4 = y2
    return [visible, x3, y3, x4, y4]


def main():
    global mutation_mult
    global fps
    countdown = 300
    canvas = tkinter.Canvas(root, width=1200, height=800, bg='white')
    #canvas.pack(fill=tkinter.BOTH, expand=0)
    canvas.place(x=0, y=0, width=1200, height=800)
    canvas.create_line(0, 700, 12000, 700, fill=rgb(0, 0, 0))
    canvas.create_line(151, 700, 151, 800, fill=rgb(0, 0, 0))
    canvas.create_line(1008, 0, 1008, 700, fill=rgb(0, 0, 0))
    table = Table(canvas, 80, 60)
    #Объявление кнопок
    tm1 = tkinter.Radiobutton(text='Выключить всё', variable=table_mode, value=0, bg='white',
                              command=lambda i=table: table.change_mode()).place(x=1014, y=10)
    tm2 = tkinter.Radiobutton(text='Отобразить богатство органикой', variable=table_mode, value=1, bg='white',
                              command=lambda i=table: table.change_mode()).place(x=1014, y=30)
    #tm3 = tkinter.Radiobutton(text='Выключить всё', variable=table_mod, value=0, bg='white').place(x=806, y=10)
    while True:
        start_time = time.time()
        if len(table.life) > 0:
            table.next()
        else:
            if countdown == 0:
                table.create_life()
                table.food_mult = 1.0
                mutation_mult = 22.5
                countdown = 300
            else:
                table.food_mult = 5.0
                table.next()
                countdown -= 1
        root.update()
        fps = 1.0 / (time.time() - start_time + 0.00001)
    root.mainloop()


if __name__ == '__main__':
    main()
