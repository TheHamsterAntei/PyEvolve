import numpy as np
import sys
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont


#Глобальные параметры (Россия и мир):
#Технические:
img = Image.open('Source.png').convert('RGB')
img_blue_colors = [0 for i in range(0, 256)]
for i in range(0, img.width):
    for j in range(0, img.height):
        t = img.getpixel((i, j))
        if t[0] == 0 and t[1] == 0:
            img_blue_colors[t[2]] += 1
gif_russians = []
gif_density = []
gif_gdp = []
gif_towners = []
assim_data = pd.read_excel('NationAssimTable.xlsx', index_col='Index')
#Мир:
year = 1897
month = 1
global_max_med = 10.0 #Максимальный уровень медицины в мире
global_gdp_med = 300.0 #Средний ВВП на душу населения в развитых странах
global_stability = 1.0 #Мировая стабильность
global_openness = 1.0 #Мировая открытость
#Россия:
russian_toleracy = 0.2 #Терпимость к меньшинствам
russian_openness = 1.0 #Открытость границ
russian_stability = 0.8 #Стабильность в стране
russian_democracy = 0.0 #Демократичность режима
russian_selfcon = 0.6 #Национальное самосознание русских
russian_humilation = 0.1 #Степень унижения русских/России
russian_unlabour = 90 #Возраст выхода на пенсию
russian_child = 12 #Возраст, с которого разрешён труд
russian_basic_cost = 8.0 #Базовая стоимость необходимых для жизни продуктов
russian_monthly_inflation = 1.003 #Месячная инфляция в России
russian_cumulative_inflation = 1.0 #Общая инфляция с 1897-го года


class Population:
    def __init__(self, region, nations, row):
        self.pop_by_nations = {}
        self.rel_by_nations = {}
        self.region = region
        self.nations = nations
        self.prev_laboured = -1
        for i in range(0, len(nations)):
            self.pop_by_nations[nations[i]] = []
            current_nation_pop = row[15 + i]
            men = region.men_pop / region.population
            women = 1.0 - men
            if pd.isna(current_nation_pop):
                for k in range(0, 10):
                    self.pop_by_nations[nations[i]].append([0.0, 0.0])
                continue
            age_weight = [15]
            for k in range(1, 80):
                age_weight.append(age_weight[k - 1] * (0.997 - 0.002 * k - 0.01 * max(0, k - 40)
                                                       - 0.02 * max(0, k - 60)))
            total_weights = sum(age_weight)
            for k in age_weight:
                p = k / total_weights
                cur_pop = current_nation_pop * p
                self.pop_by_nations[nations[i]].append([int(cur_pop * men), int(cur_pop * women)])

    def natural_growth(self):
        medicine = self.region.medicine_quality
        '''Медицина - важнейший параметр для роста населения. Она снижает смертность при родах, младенческую смертность,
        а также снижает "текущую" смертность от несчастных случаев и старения'''
        town_pop = self.region.town_pop
        '''Доля городских жителей определяет влияние эффектов демографического перехода. Поначалу горожане заводят детей
        реже селян, но со временем для обоих групп эффекты перехода будут проявляться в равной мере'''
        dtt = self.region.dem_transition_towns
        dtr = self.region.dem_transition_rural
        real_dt = town_pop * dtt + (1 - town_pop) * dtr
        '''Выгрузка текущей величины эффекта демографического перехода для горожан и селян'''
        region_stability = self.region.stability
        region_iswar = self.region.iswar
        region_hunger = self.region.hunger
        '''Низкая стабильность и нахождение в состоянии войны снижают желание людей заводить детей.
        Голод помимо понижения желания заводить детей также быстро сокращает население'''
        region_isrussian = self.region.isrussian
        if region_isrussian == 1:
            region_stability *= (russian_stability**0.5)
        '''Должны ли применяться к региону модификаторы нахождения в составе России'''
        region_prosperity = self.region.person_prosperity
        '''Достаток семей. Желание иметь детей наивысшее у людей с низким уровнем дохода, однако этот параметр имеет
        самую низкую важность'''

        #Посчитать доли национальностей
        nations_perc_pop = {}
        for i in self.nations:
            nations_perc_pop[i] = 0
            for j in self.pop_by_nations[i]:
                nations_perc_pop[i] += j[0] + j[1]
            if nations_perc_pop[i] == 0.0:
                nations_perc_pop.pop(i)
                continue
            nations_perc_pop[i] /= self.region.population
        perc_pop_keys = list(nations_perc_pop.keys())
        perc_pop_keys.sort(key=lambda x: -nations_perc_pop[x])

        #Шаг 1. "Состарить" население на месяц
        for i in self.nations:
            lnn = len(self.pop_by_nations[i])
            k = lnn
            while k > 0:
                k -= 1
                men = self.pop_by_nations[i][k][0]
                women = self.pop_by_nations[i][k][1]
                if men + women == 0.0:
                    continue
                #Мужчины
                elder_risk = max(0, k - 45 - medicine**0.7) * 0.0001 #Шанс умереть от болезней, связанных со старением
                #Шанс умереть от несчастного случая наивысший в подростковом возрасте и в молодости
                #Также этот эффект отражает шанс умереть младенцем
                basic_risk = 0.0
                if k == 0:
                    basic_risk = 0.012 - max(0.0115, 0.0001 * medicine)
                if 12 >= k > 0:
                    basic_risk = 0.00009
                if 28 > k > 12:
                    basic_risk = 0.00014
                if k >= 28:
                    basic_risk = 0.00009
                #Эффекты стабильности
                stability_risk = 0.00001 + 0.001 * (1 - region_stability)
                #Эффекты войны
                war_risk = max(0.0005 * region_iswar, 0.012 * region_iswar * int(bool(45 >= k >= 18)))
                #Эффекты голода
                hunger_risk = 0.008 * region_hunger * self.region.hungry_poverty
                men_dec = men / 12
                men_inc = (men / 12) * (1 - elder_risk - basic_risk - stability_risk - war_risk - hunger_risk)
                if men_dec < 1 and men > 0:
                    men_dec = np.random.choice([0, 1], p=(1 - men_dec, men_dec))
                if int(men_dec) == int(men_inc):
                    men_inc -= np.random.choice([0, 1],
                                                p=(1 - elder_risk - basic_risk - stability_risk -
                                                   war_risk - hunger_risk,
                                                   elder_risk + basic_risk + stability_risk +
                                                   war_risk + hunger_risk))
                men_dec = int(men_dec)
                men_inc = int(men_inc)
                self.pop_by_nations[i][k][0] -= min(self.pop_by_nations[i][k][0], men_dec)
                if k == lnn - 1:
                    self.pop_by_nations[i].append([men_inc, 0])
                    lnn += 1
                else:
                    self.pop_by_nations[i][k + 1][0] += men_inc

                #Женщины (эффекты от старения понижены, эффекты несчастных случаев понижены, эффекты войны понижены)
                elder_risk = max(0, k - 50 - medicine**0.7) * 0.00008 #Шанс умереть от болезней, связанных со старением
                # Шанс умереть от несчастного случая наивысший в подростковом возрасте и в молодости
                # Также этот эффект отражает шанс умереть младенцем
                basic_risk = 0.0
                if k == 0:
                    basic_risk = 0.012 - max(0.0115, 0.0001 * medicine)
                if 12 >= k > 0:
                    basic_risk = 0.00009
                if 28 > k > 12:
                    basic_risk = 0.00011
                if k >= 28:
                    basic_risk = 0.00006
                # Эффекты стабильности
                stability_risk = 0.00001 + 0.001 * (1 - region_stability)
                # Эффекты войны
                war_risk = 0.0005
                # Эффекты голода
                hunger_risk = 0.008 * region_hunger * self.region.hungry_poverty
                women_dec = int(women / 12)
                women_inc = int((women / 12) * (1 - elder_risk - basic_risk - stability_risk - war_risk - hunger_risk))
                if women_dec < 1 and women > 0:
                    women_dec = np.random.choice([0, 1], p=(1 - women_dec, women_dec))
                if int(women_dec) == int(women_inc):
                    women_inc -= np.random.choice([0, 1], p=(1 - elder_risk - basic_risk - stability_risk -
                                                             war_risk - hunger_risk,
                                                             elder_risk + basic_risk + stability_risk +
                                                             war_risk + hunger_risk))
                women_dec = int(women_dec)
                women_inc = int(women_inc)
                self.pop_by_nations[i][k][1] -= min(self.pop_by_nations[i][k][1], women_dec)
                if k == lnn - 1:
                    self.pop_by_nations[i].append([0, women_inc])
                    lnn += 1
                else:
                    self.pop_by_nations[i][k + 1][1] += women_inc

        #Шаг 2. "Родить" новых граждан, "умертвить" при родах часть женщин
        #Первичный расчёт граждан репродуктивного возраста
        rep_men = 0 #Количество мужчин репродуктивного возраста
        rep_women = 0 #Количество женщин репродуктивного возраста
        for i in self.nations:
            k = min(51, len(self.pop_by_nations[i]))
            while k > 14:
                k -= 1
                kf = 1
                if k < 16:
                    kf = 0.25
                if 16 <= k < 18:
                    kf = 0.5
                if 35 <= k < 40:
                    kf = 0.7
                if 40 <= k:
                    kf = 0.25
                rep_men += self.pop_by_nations[i][k][0] * kf
                rep_women += self.pop_by_nations[i][k][1] * kf
        k_chance = max(1.0, (rep_men / rep_women) ** 0.5) #Коэффициент "покрытия" женщин мужчинами
        for i in self.nations:
            k = min(51, len(self.pop_by_nations[i]))
            while k > 14:
                k -= 1
                basic_chance = 0.0 #Базовый шанс родить ребёнка в этом месяце
                preg_risk = 0.0 #Риск умереть при родах
                if k < 16:
                    basic_chance = 0.00067
                    preg_risk = 0.2 - min(0.19, 0.004 * medicine)
                if 16 <= k < 21:
                    basic_chance = 0.0067
                    preg_risk = 0.1 - min(0.095, 0.008 * medicine)
                if 21 <= k < 35:
                    basic_chance = 0.0067
                    preg_risk = 0.05 - min(0.048, 0.008 * medicine)
                if 35 <= k < 40:
                    basic_chance = 0.003
                    preg_risk = 0.1 - min(0.095, 0.006 * medicine)
                if 40 <= k:
                    basic_chance = 0.001
                    preg_risk = 0.2 - min(0.19, 0.006 * medicine)
                if region_iswar == 1:
                    basic_chance *= 0.5
                if region_hunger == 1:
                    basic_chance *= 0.3
                basic_chance *= k_chance
                basic_chance *= (region_stability + 0.3)**0.8
                basic_chance *= 3 - (2.8 * (real_dt**0.3))
                if region_prosperity < -100.0:
                    basic_chance *= 2 - (1 - real_dt**0.3)
                if -100.0 <= region_prosperity < -50.0:
                    basic_chance *= 1.5 - (0.5 - real_dt**0.3 * 0.5)
                if -50.0 <= region_prosperity < 0:
                    basic_chance *= 1.2 - (0.2 - real_dt**0.3 * 0.2)
                birth_count = self.pop_by_nations[i][k][1] * basic_chance
                if birth_count < 0:
                    birth_count = 0
                if 0.0 < birth_count < 1.0:
                    birth_count = np.random.choice([0, 1], p=(1 - birth_count, birth_count))
                    if birth_count == 1:
                        self.pop_by_nations[i][k][1] -= np.random.choice([0, 1], p=(1 - preg_risk, preg_risk))
                if birth_count >= 2.0:
                    self.pop_by_nations[i][0][0] += int(birth_count / 2)
                    self.pop_by_nations[i][0][1] += int(birth_count - int(birth_count / 2))
                    self.pop_by_nations[i][k][1] -= int(birth_count * preg_risk)
                if birth_count == 1.0:
                    if np.random.choice([0, 1], p=(0.5, 0.5)) == 0:
                        self.pop_by_nations[i][0][0] += 1
                    else:
                        self.pop_by_nations[i][0][1] += 1
                    self.pop_by_nations[i][k][1] -= np.random.choice([0, 1], p=(1 - preg_risk, preg_risk))

        #Шаг 3. Ассимилировать часть граждан в другие народы
        for i in self.nations:
            assim_chance = 0
            for j in perc_pop_keys:
                assim_chance = nations_perc_pop[j] * assim_data.at[i, j] * 0.005
                if j == self.region.state_nation:
                    assim_chance *= (1 + self.region.assimilation)
                if assim_chance == 0:
                    continue
                k = min(41, len(self.pop_by_nations[i]))
                while k > 12:
                    k -= 1
                    age_k = 0.0
                    if 12 <= k < 16:
                        age_k = 1.25
                    else:
                        if 16 <= k < 21:
                            age_k = 1.0
                        else:
                            if 21 <= k < 28:
                                age_k = 0.7
                            else:
                                if 28 <= k < 35:
                                    age_k = 0.35
                                else:
                                    if 35 <= k:
                                        age_k = 0.1
                    for sex in [0, 1]:
                        target_inc = self.pop_by_nations[i][k][sex] * assim_chance * age_k
                        if target_inc == 0:
                            continue
                        if 0 < target_inc < 1:
                            target_inc = np.random.choice([0, 1], p=(1 - target_inc, target_inc))
                            self.pop_by_nations[i][k][sex] -= target_inc
                            self.pop_by_nations[j][k][sex] += target_inc
                        if target_inc >= 1:
                            target_inc = int(target_inc)
                            self.pop_by_nations[i][k][sex] -= target_inc
                            self.pop_by_nations[j][k][sex] += target_inc

        #Шаг 4. Пересчитать население
        men_pop = sum([sum([self.pop_by_nations[k1][k2][0] for k2 in range(0, len(self.pop_by_nations[k1]))])
                          for k1 in self.pop_by_nations.keys()])
        women_pop = sum([sum([self.pop_by_nations[k1][k2][1] for k2 in range(0, len(self.pop_by_nations[k1]))])
                          for k1 in self.pop_by_nations.keys()])
        population = men_pop + women_pop
        self.region.population = population
        self.region.men_pop = men_pop
        self.region.women_pop = women_pop

    def return_labour(self):
        gdp = 0.0
        gdp_k = 1.0
        laboured = 0
        for i in self.nations:
            k = min(russian_unlabour + 1, len(self.pop_by_nations[i]))
            while k > russian_child:
                k -= 1
                if k < 21:
                    gdp += self.region.gdp_per_person * (self.pop_by_nations[i][k][0] +
                                                         self.pop_by_nations[i][k][1]) * 0.7
                    laboured += (self.pop_by_nations[i][k][0] + self.pop_by_nations[i][k][1]) * 0.7
                if 21 <= k < 50 + int(self.region.medicine_quality**0.7):
                    gdp += self.region.gdp_per_person * (self.pop_by_nations[i][k][0] +
                                                         self.pop_by_nations[i][k][1])
                    laboured += (self.pop_by_nations[i][k][0] + self.pop_by_nations[i][k][1])
                if 50 + int(self.region.medicine_quality**0.7) <= k:
                    gdp += self.region.gdp_per_person * (self.pop_by_nations[i][k][0] +
                                                         self.pop_by_nations[i][k][1]) * 0.5
                    laboured += (self.pop_by_nations[i][k][0] + self.pop_by_nations[i][k][1]) * 0.5
            if self.prev_laboured == -1:
                gdp_k = 1.0
            else:
                if laboured > self.prev_laboured:
                    gdp_k = ((self.prev_laboured / laboured) + 1) / 2
                else:
                    if laboured != 0:
                        gdp_k = ((self.prev_laboured / laboured) + 0.5) / 1.5
                    else:
                        gdp_k = 1.0
            self.prev_laboured = laboured
            self.region.unlaboured = self.region.population - laboured
        return int(gdp * gdp_k)


class Region:
    def __init__(self, nations, row):
        #Неизменяемые параметры:
        self.name = row[0]
        self.img_color = row[len(row) - 1]
        self.square = img_blue_colors[self.img_color]

        #Экономические параметры:
        self.gdp_per_person = row[1]
        self.region_gdp = row[2]
        self.person_prosperity = row[3]
        self.life_cost = row[4]
        self.stratification = row[5] * 0.01
        self.infrastructure = row[6]

        #Демографические параметры:
        self.population = row[11]
        self.men_pop = row[13]
        self.women_pop = row[14]
        self.town_pop = row[12]
        self.literacy = row[7] * 0.01
        self.education_quality = row[8]
        self.medicine_quality = row[9]
        self.migration_attract = 1.0 #Привлекательность региона для миграции
        self.pop_density = self.population / self.square
        self.dem_transition_towns = 0.3 #Выраженность демографического перехода в городах
        self.dem_transition_rural = 0.0 #Выраженность демографического перехода в деревне
        self.population_object = Population(self, nations, row)
        self.hunger = 0 #Есть ли в регионе ГОЛОД

        #Политические параметры:
        self.isrussian = 1
        self.iswar = 0 #Находится ли регион в составе государства, ведущего войну
        self.openness = 0.6
        self.governor_eff = 1
        self.stability = 1
        self.state_nation = 'Русские'
        self.assimilation = 0.4
        self.monarch_power = 0.5 #Поддержка монархии
        self.autocrat_power = 0.5 #Поддержка авторитаризма
        self.democracy_power = 0.3 #Поддержка демократии
        self.natpop_power = 0.0  #Поддержка национал-популизма
        self.liberal_power = 0.4 #Поддержка либерализма
        self.socialist_power = 0.5 #Поддержка социализма
        self.communist_power = 0.1 #Поддержка коммунизма
        self.conserv_power = 0.7 #Поддержка традиционных ценностей
        self.progress_power = 0.2 #Поддержка прогрессивных ценностей

        #Природные параметры:
        self.climate = row[10]

        # Параметры уровня жизни
        self.housing = int(0.9 * self.population)
        self.arenda = self.gdp_per_person * (self.population / self.housing) * 0.1
        self.product_cost = ((russian_basic_cost / self.infrastructure) *
                             (1 + (self.gdp_per_person / russian_basic_cost**2)))
        self.poverty = 0
        self.hungry_poverty = 0
        self.unlaboured = 0 #Численность иждивенцев

    def natural_growth(self):
        #Снижение стабильности в случае голода
        if self.stability < 1.0:
            self.stability = min(1.0, self.stability + 0.02)
        if self.hunger == 1:
            if self.stability > 0.25:
                self.stability -= 0.05
        self.population_object.natural_growth()

    def economy_growth(self):
        #Догоняющее развитие
        if self.isrussian == 1:
            if self.gdp_per_person * 2 / (0.1 + russian_openness * 0.9) < global_gdp_med:
                self.gdp_per_person += 0.25
        else:
            if self.gdp_per_person * 2 < global_gdp_med:
                self.gdp_per_person += 0.25
        #Развитие благодаря урбанизации
        self.gdp_per_person *= 1 + 0.0005 * self.town_pop
        #Развитие благодаря грамотности
        if self.literacy < 0.1:
            self.gdp_per_person = min(200, self.gdp_per_person)
        else:
            if self.literacy < 0.5:
                self.gdp_per_person = min(500, self.gdp_per_person)
                if self.gdp_per_person < 100:
                    self.gdp_per_person += 0.1
            else:
                if self.literacy < 0.9:
                    if self.gdp_per_person < 150:
                        self.gdp_per_person += 0.2
                    self.gdp_per_person *= 1 + 0.0003
                else:
                    if self.gdp_per_person < 200:
                        self.gdp_per_person += 0.25
                    self.gdp_per_person *= 1 + 0.0005
        #Развитие благодаря эффективности губернатора
        if self.governor_eff < 0.5:
            self.gdp_per_person *= 0.9998
        else:
            if 0.5 <= self.governor_eff < 0.9:
                self.gdp_per_person *= 1 + (self.governor_eff - 0.7) * 0.0001
            else:
                self.gdp_per_person += 0.1
                self.gdp_per_person *= 1 + (self.governor_eff - 0.7) * 0.0001
        #Развитие благодаря инфраструктуре
        self.gdp_per_person += (self.infrastructure - 1.0) / 2
        self.gdp_per_person *= 1 + (self.infrastructure - 0.5) * 0.00002
        #Учёт инфляции
        self.gdp_per_person *= (1 / russian_monthly_inflation)
        #Пересчёт стоимости жизни и благосостояния
        self.housing = int(0.9 * self.population)
        self.arenda = self.gdp_per_person * (self.population / self.housing) * (1 - self.stratification) * 0.1
        self.product_cost = russian_basic_cost / self.infrastructure
        self.life_cost = self.arenda + self.product_cost + self.product_cost * (self.unlaboured /
                                                                                (self.population - self.unlaboured))
        if self.population < 180000:
            self.life_cost = 0
            self.arenda = 0
            self.product_cost = 0
        self.person_prosperity = (0.5 * self.gdp_per_person + (0.5 * self.gdp_per_person * self.stratification) -
                                  self.life_cost)
        self.poverty = 0.0
        self.hungry_poverty = 0.0
        s = max(0.01, self.stratification)
        self.poverty = ((self.life_cost / (0.01 * self.gdp_per_person * (1 + s)) -
                         (1 - s) * 50) / s)
        if self.poverty > 99.9:
            self.poverty = 99.9
        if self.poverty < 0:
            self.poverty = 0
        self.hungry_poverty = (((self.life_cost - self.arenda) / (0.01 * self.gdp_per_person * (1 + s)) -
                                (1 - s) * 50) / s)
        if self.hungry_poverty > 99.9:
            self.hungry_poverty = 99.9
        if self.hungry_poverty < 0:
            self.hungry_poverty = 0
        if self.hungry_poverty > 10.0:
            self.hunger = 1
        if self.hungry_poverty < 7.0:
            self.hunger = 0
        #Итоговый подсчёт
        self.region_gdp = self.population_object.return_labour()

    def literacy_and_medicine(self):
        if self.literacy < 1:
            #Рост грамотности от урбанизации
            if self.town_pop > 0.45:
                if self.literacy < 0.5:
                    self.literacy += 0.001
                else:
                    self.literacy += 0.0002
            #Рост грамотности от качества образования
            if self.education_quality > 1.0:
                self.literacy += 0.001
            if self.education_quality > 5.0:
                self.literacy += 0.002
            if self.education_quality > 9.0:
                self.literacy += 0.002
            #Рост грамотности от ВВП
            if self.gdp_per_person > 300:
                self.literacy += 0.001
        else:
            self.literacy = 1.0
        #Медицина
        if self.literacy < 0.1:
            if self.medicine_quality > 0.1:
                self.medicine_quality -= 0.025
            else:
                self.medicine_quality = 0.1
        else:
            if self.literacy < 0.5:
                if self.medicine_quality > 10.0:
                    self.medicine_quality -= 0.05
            else:
                if self.education_quality > 3.0:
                    if self.medicine_quality * 2 < global_max_med:
                        self.medicine_quality += 0.025
                if self.education_quality > 6.0:
                    if self.medicine_quality * 1.2 < global_max_med:
                        self.medicine_quality += 0.025
                if self.education_quality > 8.5:
                    if self.medicine_quality < global_max_med:
                        self.medicine_quality += 0.01
                    else:
                        self.medicine_quality = global_max_med
        #Качество образования
        if month == 6:
            self.education_quality -= 0.1
        if self.gdp_per_person * 0.9 > global_gdp_med:
            if self.education_quality < 10.0:
                self.education_quality += 0.02
            else:
                self.education_quality = 10.0
        if self.gdp_per_person * 1.2 > global_gdp_med:
            if self.education_quality < 9.0:
                self.education_quality += 0.02
        if self.gdp_per_person * 1.5 > global_gdp_med:
            if self.education_quality < 5.0:
                self.education_quality += 0.02
        if self.gdp_per_person * 2.0 > global_gdp_med:
            if self.education_quality < 2.0:
                self.education_quality += 0.02
        if self.gdp_per_person * 3.0 > global_gdp_med:
            if self.education_quality < 1.0:
                self.education_quality += 0.02

    def urban(self):
        #Рост урбанизации
        if self.gdp_per_person > 100:
            if self.town_pop < 0.5:
                self.town_pop += 0.0001
        if self.gdp_per_person > 500:
            if self.town_pop < 0.7:
                self.town_pop += 0.0001
        if self.literacy > 0.9:
            if self.town_pop < 0.8:
                self.town_pop += 0.0001
        #Демографический переход
        if self.gdp_per_person > 200:
            if self.dem_transition_towns < 0.9:
                self.dem_transition_towns += 0.001
            if self.dem_transition_rural < 0.2:
                self.dem_transition_rural += 0.001
        if self.gdp_per_person > 1000:
            if self.dem_transition_towns < 0.95:
                self.dem_transition_towns += 0.0004
            if self.dem_transition_rural < 0.8:
                self.dem_transition_rural += 0.0005
        if self.gdp_per_person > 2000:
            if self.dem_transition_towns < 1.0:
                self.dem_transition_towns += 0.0002
            else:
                self.dem_transition_towns = 1.0
            if self.dem_transition_rural < 1.0:
                self.dem_transition_rural += 0.0002
            else:
                self.dem_transition_rural = 1.0
        if self.literacy > 0.95:
            if self.dem_transition_towns < 0.9:
                self.dem_transition_towns += 0.0004
            if self.dem_transition_rural < 0.5:
                self.dem_transition_rural += 0.0005
        if self.town_pop > 0.3:
            if self.dem_transition_rural < 0.3:
                self.dem_transition_rural += 0.0004
        if self.town_pop > 0.5:
            if self.dem_transition_rural < self.dem_transition_towns:
                self.dem_transition_rural += 0.001

    def building(self):
        #Изменение инфраструктуры
        if month == 3:
            if self.infrastructure > 0.01:
                self.infrastructure = max(0.01, self.infrastructure - 0.2 / self.climate)
        if self.gdp_per_person * self.governor_eff > 200:
            if self.infrastructure < 0.5:
                self.gdp_per_person -= 0.2
                self.infrastructure += 0.1
        if self.gdp_per_person * self.governor_eff > 300:
            if self.infrastructure < 1.0:
                self.gdp_per_person -= 0.2
                self.infrastructure += 0.07
        if self.gdp_per_person * self.governor_eff > 500:
            if self.infrastructure < 1.5:
                self.gdp_per_person -= 0.2
                self.infrastructure += 0.05
        if self.gdp_per_person * self.governor_eff > 800:
            if self.infrastructure < 2.0:
                self.gdp_per_person -= 0.2
                self.infrastructure = min(2.0, self.infrastructure + 0.04)
        #Строительство жилья
        if month == 3:
            if self.housing > 0:
                self.housing = max(0, int(self.housing * (0.998 - (3 - self.climate) * 0.0001)))
        if self.housing < self.population:
            self.housing += int(self.population * 0.001)
            self.gdp_per_person *= 0.9995


def population_to_str(pop):
    str_pop = ''
    pop = int(pop)
    if pop < 1000:
        str_pop = str(pop)
        return str_pop
    else:
        while pop > 0:
            if str_pop != '':
                to_pop = str(pop % 1000)
                if pop > 1000:
                    while len(to_pop) < 3:
                        to_pop = '0' + to_pop
                str_pop = to_pop + '.' + str_pop
            else:
                to_pop = str(pop % 1000)
                if pop > 1000:
                    while len(to_pop) < 3:
                        to_pop = '0' + to_pop
                str_pop = to_pop
            pop //= 1000
        return str_pop


def save_populi_image(regs_dict):
    dict_blues = {}
    max_pop = -1.0
    max_in_reg = {}
    hunger = {}
    for i in regs_dict.keys():
        dict_blues[regs_dict[i].img_color] = i
        if regs_dict[i].hunger == 1:
            hunger[i] = True
        else:
            hunger[i] = False
        rus_sum = sum([regs_dict[i].population_object.pop_by_nations['Русские'][k][0] +
                       regs_dict[i].population_object.pop_by_nations['Русские'][k][1]
                       for k in range(0, len(regs_dict[i].population_object.pop_by_nations['Русские']))])
        ukr_sum = sum([regs_dict[i].population_object.pop_by_nations['Украинцы'][k][0] +
                       regs_dict[i].population_object.pop_by_nations['Украинцы'][k][1]
                       for k in range(0, len(regs_dict[i].population_object.pop_by_nations['Украинцы']))])
        bel_sum = sum([regs_dict[i].population_object.pop_by_nations['Белорусы'][k][0] +
                       regs_dict[i].population_object.pop_by_nations['Белорусы'][k][1]
                       for k in range(0, len(regs_dict[i].population_object.pop_by_nations['Белорусы']))])
        max_pop = max(max_pop, rus_sum, ukr_sum, bel_sum)
        max_in_reg[i] = [-1.0, (0, 0, 0)]
        if rus_sum > max_in_reg[i][0]:
            max_in_reg[i][0] = rus_sum
            max_in_reg[i][1] = (200, 30, 120)
        if ukr_sum > max_in_reg[i][0]:
            max_in_reg[i][0] = ukr_sum
            max_in_reg[i][1] = (220, 180, 30)
        if bel_sum > max_in_reg[i][0]:
            max_in_reg[i][0] = bel_sum
            max_in_reg[i][1] = (30, 225, 60)
    img_density = img.copy()
    for x in range(0, img_density.width):
        for y in range(38, img_density.height):
            t = img_density.getpixel((x, y))
            if t[0] == 0 and t[1] == 0:
                if t[2] in dict_blues.keys():
                    cur_reg = dict_blues[t[2]]
                    red = max_in_reg[cur_reg][1][0]
                    green = max_in_reg[cur_reg][1][1]
                    blue = max_in_reg[cur_reg][1][2]
                    bright = (max_in_reg[cur_reg][0] / max_pop)
                    if hunger[cur_reg]:
                        red = 220
                        green = 0
                        blue = 0
                        bright = 1
                    img_density.putpixel((x, y), (int(red * bright), int(green * bright), int(blue * bright)))
    draw = ImageDraw.Draw(img_density)
    fnt = ImageFont.truetype("calibri.ttf", 35)
    draw.text((30, 1), population_to_str(sum([regs_dict[i].population for i in regs_dict.keys()])), font=fnt,
              fill=(0, 0, 0))
    draw.text((280, 1), population_to_str(sum([regs_dict[i].region_gdp for i in regs_dict.keys()])), font=fnt,
              fill=(0, 0, 0))
    img_density.save("Output/Population/Pop" + str(int(((year - 1897) * 12 + month - 1) / 3)) + '.png', 'PNG')


def main():
    data = pd.read_excel('RegData.xlsx').drop(['Итого', 'Столица субъекта'], axis=1)
    if not os.path.exists('Output/'):
        os.mkdir('Output')
    if not os.path.exists('Output/Population/'):
        os.mkdir('Output/Population')
    nations = data.columns.to_list()
    nations = nations[15:len(nations) - 1]
    regs_dict = {}
    for i in data.iterrows():
        row = i[1].to_list()
        regs_dict[row[0]] = Region(nations, row)
    global month, year, global_gdp_med, global_max_med, russian_cumulative_inflation, russian_basic_cost
    while year < 2001:
        if ((year - 1897) * 12 + month - 1) % 3 == 0 and ((year - 1897) * 12 + month - 1) != 0:
            save_populi_image(regs_dict)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        russian_cumulative_inflation *= russian_monthly_inflation
        russian_basic_cost *= russian_monthly_inflation
        if month == 3:
            global_max_med += 0.1
            global_gdp_med *= 1.03
        if month == 9:
            global_max_med += 0.1
        for i in regs_dict.keys():
            regs_dict[i].natural_growth()
            regs_dict[i].economy_growth()
            regs_dict[i].literacy_and_medicine()
            regs_dict[i].urban()
    #Ниже тесты рисования
    sys.exit(0)
    dict_blues = {}
    for i in regs_dict.keys():
        dict_blues[regs_dict[i].img_color] = i
        max_dens = max(max_dens, regs_dict[i].pop_density)
        max_gdp = max(max_gdp, regs_dict[i].region_gdp)
    img_density = img.copy()
    for x in range(0, img_density.width):
        for y in range(0, img_density.height):
            t = img_density.getpixel((x, y))
            if t[0] == 0 and t[1] == 0:
                if t[2] in dict_blues.keys():
                    density = (regs_dict[dict_blues[t[2]]].pop_density)**0.5 / (max_dens)**0.5 * 255
                    img_density.putpixel((x, y), (int(density * 0.8), 0, int(density * 0.4)))
    img_density.save("Output//PopDens.png", 'PNG')
    img_gdp = img.copy()
    for x in range(0, img_gdp.width):
        for y in range(0, img_gdp.height):
            t = img_gdp.getpixel((x, y))
            if t[0] == 0 and t[1] == 0:
                if t[2] in dict_blues.keys():
                    gdp = (regs_dict[dict_blues[t[2]]].region_gdp)**0.5 / (max_gdp)**0.5 * 255
                    img_gdp.putpixel((x, y), (int(gdp * 0.8), 0, int(gdp * 0.4)))
    img_gdp.save("Output//GDP.png", 'PNG')
    img_russians = img.copy()
    for x in range(0, img_russians.width):
        for y in range(0, img_russians.height):
            t = img_russians.getpixel((x, y))
            if t[0] == 0 and t[1] == 0:
                if t[2] in dict_blues.keys():
                    russians = (regs_dict[dict_blues[t[2]]].population_object.pop_by_nations['Русские'] /
                                regs_dict[dict_blues[t[2]]].population * 255)
                    img_russians.putpixel((x, y), (int(russians * 0.8), 0, int(russians * 0.4)))
    img_russians.save("Output//Russians.png", 'PNG')

if __name__ == '__main__':
    main()
