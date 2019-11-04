# =============================================================================
#                      Classe de la grille de Morpion
# =============================================================================

import numpy as np
from Exceptions import IllegalMoveError

VIDE = 2
NOIR, MACHINE = 1, 1
BLANC, HUMAIN = 0, 0 # l'homme joue toujours les blancs (les X)
LISTECOULEURS = (BLANC, NOIR)
UI = ('X', 'O')

class Grille :
    def __init__ (self, N, nbPions) :
        # Initialement, aucun pion n'est placé
        self.__VB = []
        self.__VN = []

        self.__dim = N
        self.__nbPions = nbPions

        # On inscrit toutes les cases puisque toutes les cases sont vides au début
        self.__VV = []
        for l in range(N) :
            for c in range(N) :
                self.__VV.append((l,c))

    # =============================================================================
    #                               get...()
    # =============================================================================
    def getVector (self, Color) :
        if Color == BLANC : return  self.__VB
        elif Color == NOIR : return self.__VN
        elif Color == VIDE : return self.__VV
        else : return None

    def getNbPions (self):
        return self.__nbPions

    def getDim (self):
        return self.__dim

    # =============================================================================
    #                               set...()
    # =============================================================================
    def resetGrille(self, newGrille):
        """ Reset la grille à partir d'une nouvelle grille """
        VB, VN, VV = newGrille.getVector(BLANC), newGrille.getVector(NOIR), newGrille.getVector(VIDE)
        self.__VB = VB[:] # faisons une copie et non une = entre 2 variables
        self.__VN = VN[:]
        self.__VV = VV[:]

    # =============================================================================
    #                       Fonctions utiles à la grille
    # =============================================================================
    def echangerCase (self, Case, Color, placer="PLACER") :
        try :
            # On récupère le vecteur correspondant à la couleur
            VC = self.getVector(Color)

            if placer == "PLACER" :
                # On retire la case de la liste des vides
                self.__VV.pop(self.__VV.index(Case))

                # On ajoute la case à la liste de la bonne couleur
                VC.append(Case)
            elif placer == "LIBERER" :
                # On retire la case de la liste des color
                VC.pop(VC.index(Case))

                # On ajoute la case à la liste de la bonne couleur
                self.__VV.append(Case)
            else :
                raise IllegalMoveError("in - Grille.echangerCase")
        except IllegalMoveError as error:
            print("ERROR : Oops! That was an illegal move. Try again...")
            print("\t[error_type] %s, \n\t[error] %s"%(type(error), error))
        # DEBUG: traceback.print_exc()
        return self

    def gagnant(self, Color):
        """ Vérifie si la couleur en paramètre est gagnante ou non """

        # On récupère le vecteur correspondant à la couleur
        VC = self.getVector(Color)

        # S'il y a assez de pions en jeu...
        if len(VC) >= self.__nbPions :

            # Vérifions qu'il n'y ait pas de gagnant
            if len(set([l for (l, c) in VC])) == 1 : return True
                # set renvoie une liste ordonnée sans doublon
                # on check les lignes pour la couleur donnée Color

            elif len(set([c for (l, c) in VC])) == 1 : return True
                # on check les colonnes

            elif len(set([l for (l,c) in VC if l==c])) == 3 : return True
                # on check la première diagonale

            elif len(set([l for (l,c) in VC if l+c==self.__dim-1])) == 3 : return True
                # on check la 2e diagonale

            else : return False
        else : return False

    def isEmpty(self):
        return len(self.__VV) >= self.__dim**2 # si toutes les cases sont vides c'est que la grille est vierge

    # =============================================================================
    #                      Fonctions utiles pour l'affichage
    # =============================================================================
    def afficherGrilleConsole(self) :
        """ Affiche la grille dans la console """
        grilleJeu = np.reshape(np.array(['*']*self.__dim**2), (self.__dim, self.__dim)) # crée une grille de '*' de taille n*n

        for case in self.__VB :
            grilleJeu[case] = UI[BLANC]
        for case in self.__VN :
            grilleJeu[case] = UI[NOIR]

        print(grilleJeu)
        print('\n'+ "#"*17 + '\n')

    # =============================================================================
    #                    Fonctions d'évaluation pour BestFirst
    # =============================================================================
    def evaluation(self, Color, Case):
        """ Evalue la valeur d'une case selon le calcul de g """
        lst1, lst2 = self.getVector(Color), self.getVector(not(Color)) # Mes pions (1) et ceux de l'adversaire (2)
        l, c = Case
        N = self.getDim()

        # Lignes
        NL1 = len([0 for (x,y) in lst1 if x == l])   # nombre de pions du joueur 1 sur la ligne l
        NL2 = len([0 for (x,y) in lst2 if x == l])    # nombre de pions du joueur 2 sur la ligne l

        # Colonnes
        NC1 = len([0 for (x,y) in lst1 if c == y])    # nombre de pions du joueur 1 sur la colonne c
        NC2 = len([0 for (x,y) in lst2 if c == y])    # nombre de pions du joueur 2 sur la colonne c

        # Diagonales
        if l == c: # la case est sur la diagonale
            ND1 = len([0 for (x,y) in lst1 if x == y])
            ND2 = len([0 for (x,y) in lst2 if x == y])
        elif l + c == N+1: # la case est sur l'antidiagonale
            ND1 = len([0 for (x,y) in lst1 if x + y == N+1])
            ND2 = len([0 for (x,y) in lst2 if x + y == N+1])
        else:
            ND1, ND2 = 0, 0

        # Calcul de g
        g = (NL1 - NL2)**2 + (NC1 - NC2)**2 + (ND1 - ND2)**2
        return g

    def evaluationAmelioree (self, Color, Case):
        """ Evaluation optimisée de la valeur d'une case selon le calcul de gAmeliore """
        lst1, lst2 = self.getVector(Color), self.getVector(not(Color)) # Mes pions (1) et ceux de l'adversaire (2)
        l, c = Case
        N = self.getDim()

        # Lignes
        NL1 = len([0 for (x,y) in lst1 if x == l])   # nombre de pions du joueur 1 sur la ligne l
        NL2 = len([0 for (x,y) in lst2 if x == l])    # nombre de pions du joueur 2 sur la ligne l
        _NL = 2 if NL2 > 1 else 1

        # Colonnes
        NC1 = len([0 for (x,y) in lst1 if c == y])    # nombre de pions du joueur 1 sur la colonne c
        NC2 = len([0 for (x,y) in lst2 if c == y])    # nombre de pions du joueur 2 sur la colonne c
        _NC = 2 if NC2 > 1 else 1

        # Diagonales
        if l == c: # la case est sur la diagonale
            ND1 = len([0 for (x,y) in lst1 if x == y])
            ND2 = len([0 for (x,y) in lst2 if x == y])
        elif l + c == N+1: # la case est sur l'antidiagonale
            ND1 = len([0 for (x,y) in lst1 if x + y == N+1])
            ND2 = len([0 for (x,y) in lst2 if x + y == N+1])
        else:
            ND1, ND2 = 0, 0
        _ND = 2 if ND2 > 1 else 1

        # Calcul de g
        g = (NL1 - NL2)**2 + (NC1 - NC2)**2 + (ND1 - ND2)**2

        # Calcul de gAmelioré
        gAmeliore = g*_NL*_NC*_ND
        return gAmeliore

    # =============================================================================
    #                    Fonctions d'évaluation pour MinMax
    # =============================================================================
    def valeurPlateau (self, Color):
        """ Calcule la valeur du plateau """
        N = self.getDim()
        lst1, lst2 = self.getVector(Color), self.getVector(not(Color)) # Mes pions (1) et ceux de l'adversaire (2)
        def lignesBloquees(lst):
            """ Calcule le nombre de lignes/colonnes/diag bloquées """
            lignes, colonnes, diagonales, antidiagonales = [], [], [], []
            for (l,c) in lst:
                lignes.append(l)
                colonnes.append(c)
                if l == c:
                    diagonales.append(1)
                if l+c == N+1:
                    antidiagonales.append(1)
            return len(set(lignes)) + len(set(colonnes)) + len(set(diagonales)) + len(set(antidiagonales))

        return lignesBloquees(lst1) - lignesBloquees(lst2)
