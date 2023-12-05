from Modele import *
import copy
import math

class Simplexe:
    def __init__(self, modele):
        self.module     = copy.deepcopy(modele)
        self.n          = self.module.n
        self.m          = self.module.m
        self.sens       = self.module.sens
        self.c          = copy.deepcopy(self.module.c)
        self.a          = copy.deepcopy(self.module.a)
        self.b          = copy.deepcopy(self.module.b)        
        self.variable   = []
        self.coeff      = [] #correspond aux coefficients impliqués dans la base.
        self.base       = [] #correspond aux noms des coefficients impliqués dans la base.
        self.z          = [] #correspond aux coefficients dans zi
        self.c_z        = [] #correspond aux coefficients de ci - zi
        self.a_next     = []
        self.b_next     = []
        self.coeff_next = []
        self.base_next  = []
        self.z_next     = []
        self.c_z_next   = []    
        self.compteur   = 0
        self.increment  = 0
        self.variable_artificielle = 0
        self.c_initiale = copy.deepcopy(self.module.c)
        self.a_initiale = copy.deepcopy(self.module.a)
        self.maximisation = copy.deepcopy(self.module.maximisation)

    def optimisation(self):
        # ----- initialisation ------ #
        for i in self.sens: # Si il y a un signe >= alors on compte le nombre de variables artificielles à rajouter
            if i  == True:
                self.variable_artificielle = self.variable_artificielle + 1
        
        if self.maximisation == False:
            for i in range(self.n):
                self.c[i] = self.c[i] * -1
                
        if self.variable_artificielle != 0: #Si il y des variables artificielles -> modification de self.c
            for i in range(self.n):
                self.c[i] = 0.0
        
        for i in range(self.m): #Modification de self.c
            self.c.append(0.0)

        self.variable = [f'X{i}' for i in range(1, self.n + 1)] + [f'E{j}' for j in range(1, self.m + 1)] #Modification de self.variable

        if self.variable_artificielle != 0: #Si il y des variables artificielles -> modification de self.c
            for i in range(self.variable_artificielle):
                self.c.append(-1.0)
                self.variable.append(f'A{i+1}')

        self.increment = 0
        for i in range(self.m): #Modification de self.a                
                for indice in range(self.m + self.variable_artificielle):
                    if indice < self.m:
                        if i == indice: #Gestion des variables d'excès ou d'écart
                            if self.sens[i] == False:
                                self.a[i].extend([1.0])
                            else:
                                self.a[i].extend([-1.0])
                        else:
                            self.a[i].extend([0.0])
                    else:
                        if indice == i + self.m: #Gestion des variables artificielles
                            self.a[i].extend([1.0])
                        else:
                            self.a[i].extend([0.0])

        
        for i in range(self.m): #Modification de self.coeff
            if i < self.variable_artificielle:
                self.coeff.extend([-1.0])
            else:
                self.coeff.extend([0.0])

        for i in range(self.m): #Modification de self.base
            if i < self.variable_artificielle:
                self.base.append(self.variable[self.n+self.m+i])
            else:
                self.base.append(self.variable[self.n+i])

        for i in range(self.n + self.m+ self.variable_artificielle): #Modification de self.z
            valeur = 0
            valeur1 = 0
            for j in range(self.m):               
                valeur = valeur + self.coeff[j]*self.a[j][i]
                if i == self.n + self.m +self.variable_artificielle -1:
                    valeur1 = valeur1 + self.coeff[j]*self.b[j]
            self.z.append(valeur)
        self.z.append(valeur1)
        
        for i in range(self.n+self.m+self.variable_artificielle): #Modification de self.c_z
            var = self.c[i] - self.z[i]
            self.c_z.append(var)     

        # ----- initialisation ------ #
        self.print()         
        if self.variable_artificielle != 0:
            while self.stop_artificielle():
                self.iteration_artificielle()
                self.print()
        
        while self.stop():
            self.iteration()
            self.print()
        

        # ----- Calcule du tableau suivant ------ #
        
    def stop(self):
        
        if self.compteur == 0:            
            self.compteur = self.compteur+1
            return True
        for i in range(self.n + self. m):
            if self.c_z[i] > 0:                
                return True
        return False
    
    def stop_artificielle(self):
        a_bis = []
        variable_bis = []
        c_z_bis = []

        for i in self.base:
            if i.startswith("A"):
                return True
           
        for i in range(self.n + self.m):
            variable_bis.append(self.variable[i])
            c_z_bis.append(self.c_z[i])
            

        self.variable = copy.deepcopy(variable_bis)
        
        
        self.c = copy.deepcopy(self.c_initiale)        
        for i in range(self.m): #Modification de self.c
            self.c.append(0.0)

        if self.maximisation == False: 
            for i in range(self.n):
                self.c[i] = self.c[i] * -1

        for i in range(self.m):
            self.coeff[i] = self.c[self.variable.index(self.base[i])]

        a_bis = copy.deepcopy(self.a)
        self.a = copy.deepcopy(self.a_initiale)
        for i in range(self.m): #Modification de self.a
                for indice in range(self.m):
                        if i == indice: #Gestion des variables d'excès ou d'écart
                            if self.sens[i] == False:
                                self.a[i].extend([1.0])
                            else:
                                self.a[i].extend([-1.0])
                        else:
                            self.a[i].extend([0.0])

        for i in range(self.m):
            for j in range(self.n+self.m):
                self.a[i][j] = a_bis[i][j]

        self.z = []
        valeur1 = 0
        for i in range(self.n + self.m): #Modification de self.z
            valeur = 0            
            for j in range(self.m):
                valeur = valeur + self.coeff[j]*self.a[j][i]
                if i == 0:
                    valeur1 = valeur1 + self.coeff[j]*self.b[j]                    
            self.z.append(valeur)
        self.z.append(valeur1)

        self.c_z = copy.deepcopy(c_z_bis)
        for i in range(self.n + self.m): #Modification de self.c_z.
                self.c_z[i] = self.c[i] - self.z[i]        
        self.print()
        self.compteur = self.compteur + 1
        

        return False
    
    def iteration(self):
        # ----- Recherche du pivot ------ #
            self.tmp = []
            self.index = self.c_z.index(max(self.c_z))
            for i in range(self.m):
                if self.a[i][self.index] != 0 and self.a[i][self.index] > 0:
                    self.tmp.append(self.b[i]/self.a[i][self.index])
                else:
                    self.tmp.append(math.inf)
            self.pos_pivot = (self.c_z.index(max(self.c_z)), self.tmp.index(min(self.tmp)))

            # ----- Recherche du pivot ------ #

            self.a_next     = copy.deepcopy(self.a)
            self.b_next     = copy.deepcopy(self.b)
            self.coeff_next = copy.deepcopy(self.coeff)
            self.base_next  = copy.deepcopy(self.base)
            self.z_next     = copy.deepcopy(self.z)
            self.c_z_next   = copy.deepcopy(self.c_z)
        
            # ----- Calcule du tableau suivant ------ #

            for i in range(self.n + self.m): #Division de la ligne du pivot par la valeur du pivot
                self.a_next[self.pos_pivot[1]][i] =  self.a[self.pos_pivot[1]][i] / self.a[self.pos_pivot[1]][self.pos_pivot[0]]
                           

            for i in range(self.m): #Mise à zéro de la colonne du pivot sauf le pivot
                if i != self.pos_pivot[1]:
                    self.a_next[i][self.pos_pivot[0]] = 0.0

            self.b_next[self.pos_pivot[1]] = min(self.tmp)
            for i in range(self.m): #Calcule des valeurs manquants avec la formule vu en cours.
                if i != self.pos_pivot[1]:
                    for j in range(self.n + self.m):
                        if j != self.pos_pivot[0]:
                            self.a_next[i][j] = self.a[i][j] - ((self.a[self.pos_pivot[1]][j] * self.a[i][self.pos_pivot[0]]) / self.a[self.pos_pivot[1]][self.pos_pivot[0]])
                        if j == 0:
                            self.b_next[i] = self.b[i] - (self.b[self.pos_pivot[1]] * self.a[i][self.pos_pivot[0]] / self.a[self.pos_pivot[1]][self.pos_pivot[0]])            

            self.base_next[self.pos_pivot[1]] = self.variable[self.pos_pivot[0]] #Modification de la variable en base
            self.coeff_next[self.pos_pivot[1]] = self.c[self.pos_pivot[0]]
        
            valeur1 = 0
            for i in range(self.n + self.m): #Modification de self.z
                valeur = 0            
                for j in range(self.m):
                    valeur = valeur + self.coeff_next[j]*self.a_next[j][i]
                    if i == 0:
                        valeur1 = valeur1 + self.coeff_next[j]*self.b_next[j]                    
                self.z_next[i] = valeur
            self.z_next[self.n +self.m] = valeur1

            for i in range(self.n + self.m): #Modification de self.c_z.
                self.c_z_next[i] = self.c[i] - self.z_next[i]
        

            self.a     = copy.deepcopy(self.a_next)
            self.b     = copy.deepcopy(self.b_next)
            self.base  = copy.deepcopy(self.base_next)
            self.c_z   = copy.deepcopy(self.c_z_next)
            self.z     = copy.deepcopy(self.z_next)
            self.coeff = copy.deepcopy(self.coeff_next)  

    def iteration_artificielle(self):
        # ----- Recherche du pivot ------ #
            self.tmp = []
            self.index = self.c_z.index(max(self.c_z))
            for i in range(self.m):
                if self.a[i][self.index] != 0 and self.a[i][self.index] > 0:
                    self.tmp.append(self.b[i]/self.a[i][self.index])
                else:
                    self.tmp.append(math.inf)
            self.pos_pivot = (self.c_z.index(max(self.c_z)), self.tmp.index(min(self.tmp)))

            # ----- Recherche du pivot ------ #

            self.a_next     = copy.deepcopy(self.a)
            self.b_next     = copy.deepcopy(self.b)
            self.coeff_next = copy.deepcopy(self.coeff)
            self.base_next  = copy.deepcopy(self.base)
            self.z_next     = copy.deepcopy(self.z)
            self.c_z_next   = copy.deepcopy(self.c_z)
        
            # ----- Calcule du tableau suivant ------ #

            for i in range(self.n + self.m+ self.variable_artificielle): #Division de la ligne du pivot par la valeur du pivot
                self.a_next[self.pos_pivot[1]][i] =  self.a[self.pos_pivot[1]][i] / self.a[self.pos_pivot[1]][self.pos_pivot[0]]
                           

            for i in range(self.m): #Mise à zéro de la colonne du pivot sauf le pivot
                if i != self.pos_pivot[1]:
                    self.a_next[i][self.pos_pivot[0]] = 0.0

            self.b_next[self.pos_pivot[1]] = min(self.tmp)
            for i in range(self.m): #Calcule des valeurs manquants avec la formule vu en cours.
                if i != self.pos_pivot[1]:
                    for j in range(self.n + self.m+self.variable_artificielle):
                        if j != self.pos_pivot[0]:
                            self.a_next[i][j] = self.a[i][j] - ((self.a[self.pos_pivot[1]][j] * self.a[i][self.pos_pivot[0]]) / self.a[self.pos_pivot[1]][self.pos_pivot[0]])
                        if j == 0:
                            self.b_next[i] = self.b[i] - (self.b[self.pos_pivot[1]] * self.a[i][self.pos_pivot[0]] / self.a[self.pos_pivot[1]][self.pos_pivot[0]])

            self.base_next[self.pos_pivot[1]] = self.variable[self.pos_pivot[0]] #Modification de la variable en base
            self.coeff_next[self.pos_pivot[1]] = self.c[self.pos_pivot[0]]
        
            valeur1 = 0
            for i in range(self.n + self.m+self.variable_artificielle): #Modification de self.z
                valeur = 0
                for j in range(self.m):
                    valeur = valeur + self.coeff_next[j]*self.a_next[j][i]
                    if i == 0:
                        valeur1 = valeur1 + self.coeff_next[j]*self.b_next[j]
                self.z_next[i] = valeur
            self.z_next[self.n +self.m+self.variable_artificielle] = valeur1

            for i in range(self.n + self.m+self.variable_artificielle): #Modification de self.c_z.
                self.c_z_next[i] = self.c[i] - self.z_next[i]
        
            self.a     = copy.deepcopy(self.a_next)
            self.b     = copy.deepcopy(self.b_next)
            self.base  = copy.deepcopy(self.base_next)
            self.c_z   = copy.deepcopy(self.c_z_next)
            self.z     = copy.deepcopy(self.z_next)
            self.coeff = copy.deepcopy(self.coeff_next)  

    def print(self):
        print("TODO : print")
        print("         ci        ", end=" ")
        print(self.c)
        print("Coeff Zi  |  Base  ", end=" ")
        print(self.variable, end = " ")
        print("bj")
        for i in range(self.m):
            print(self.coeff[i], end =" ")
            print("      | ", end =" ")
            print(self.base[i], end=" ")
            print("   ", end=" ")
            print(self.a[i], end=" ")
            print(" ", end=" ")
            print(self.b[i])
        print("         zi        ", end=" ")
        print(self.z)
        print("       ci - zi     ", end=" ")
        print(self.c_z)

