# =============================================================================
#                       Classe du jeu de morpion
# =============================================================================

import numpy as np
import tkinter as tk
import random
import traceback

from Grille import * # dont VIDE, BLANC, NOIR, LISTECOULEURS, UI
from Exceptions import FinDuJeuParRepetitionError, IllegalMoveError
import Application
from Application import MODES
from Tour import * # dont TourRandom, TourBestFirst, TourMinMax, TourAlphaBeta


FIN_REPETITION = 3
TAB_YES = ['', 'y', 'yes', 'oui', 1, True]
TAB_NO = ['n', 'no', 'non', 0, False]

class JeuMorpion :
    # =============================================================================
    #                               __init__
    # =============================================================================
    def __init__ (self, N, nbPions):
        """
        params :
            N (int) : dimension de la grille
            nbPions (int) : nombre de pions
        """
        self.__dim = N
        self.__nbPions = nbPions

        # Initialisation de la grille
        self.__Grille = Grille(N, nbPions)

        # Initialisation de l'Historique (FIFO)
        self.__Historique = []

        # Console ou UI ?
        self.__isConsoleActive = self.activateConsole()
        print("INFO : Vous avez choisi de jouer %s"%("dans l'UI", "dans la console")[self.__isConsoleActive])

        # Premier joueur
        self.__colorInit = random.randint(BLANC, NOIR)

        # Tableau des fonctions placer pion. On y accède avec self.__ModeJeu
        self.__TAB_PLACER_PION = [self.placer_pion_machine, self.placer_pion_humain, self.placer_pion, self.placer_pion, self.placer_pion, self.placer_pion, self.placer_pion_2machines]
        # Tableau des constructeurs de tour. On y accède avec self.__ModeJeu
        self.__TAB_TOUR = [TourRandom, None, TourRandom, TourBestFirst, TourMinMax, TourAlphaBeta, (TourRandom, TourMinMax)]
        self.__ModeJeu = 2 # par défaut ordirandom/humain

        self.__forceStop = False

        if not self.__isConsoleActive :
            # Initialisation de la fenêtre d'affichage
            self.__root = tk.Tk()
            # tk.CallWrapper = TkErrorCatcher
            self.__Application = Application.Application(self, master=self.__root)

            # Selectionnons le mode de Jeu
            self.selectionnerModeJeu()

            # Lançons le tout
            self.jouer()
            self.__Application.mainloop()

        else:
            # Selectionnons le mode de Jeu
            self.selectionnerModeJeu()

            # Lançons le tout
            self.jouer()



    # =============================================================================
    #                       Fonctions utiles à l'UI
    # =============================================================================
    def activateConsole (self):
        while True:
            try:
                ans = input("Q : Voulez-vous jouer dans la console (Y, n) ? ")
                if ans in TAB_YES : return True
                elif ans in TAB_NO : return False
                else : raise ValueError
            except ValueError as e :
                self.handleError(e)
                continue
            break

    def updateButtonText (self, Color):
        """ Mise à jour des textes des boutons """
        # On récupère le vecteur correspondant à la couleur
        VC = self.__Grille.getVector(Color)
        VV = self.__Grille.getVector(VIDE)

        def fromTuple2Number(i, j):
            return i*self.__dim + j

        # Effacer
        if len(VC) >= 3 :
            self.__Application.getButtonList()[fromTuple2Number(VV[-1][0], VV[-1][1])]["text"]=''
                    # puisque l'on .append(), la case en question est la dernière ajoutée, d'où -1
        # Imprimer
        self.__Application.getButtonList()[fromTuple2Number(VC[-1][0], VC[-1][1])]["text"]=UI[Color] # idem


    # =============================================================================
    #                       Fonctions utiles au jeu
    # =============================================================================
    def ajoutHistorique (self) :
        """ Sauvegarde les grilles dans un historique (fifo) de taille fixe """
        tailleMax = 5

        # Si l'historique dépasse la taille autorisée
        if len(self.__Historique) > tailleMax :
            self.__Historique.pop(0) # on retire le premier élt (grille la plus ancienne)
            self.__Historique.append(self.__Grille)
        else :
            self.__Historique.append(self.__Grille)

    def checkRepetition(self):
        """ Vérifie que la grille n'est pas une répétition  """
        if len(self.__Historique) > FIN_REPETITION and self.__Grille == self.__Historique[-FIN_REPETITION] :
            raise FinDuJeuParRepetitionError()
        return

    def initNewGame (self):
        """ Reset everything to play another game """
        print("INFO : NEW GAME STARTING")
        self.__forceStop = True # pour arrêter la boucle de jeu

        # Nouvelle Grille
        del self.__Grille
        self.__Grille = Grille(self.__dim, self.__nbPions)

        # Nouvel historique
        del self.__Historique
        self.__Historique = []

        # Nouveau premier joueur
        del self.__colorInit
        self.__colorInit = random.randint(BLANC, NOIR)

        print("INFO : RESET COMPLETED")


    def forceStop(self):
        """ Stop le jeu brutalement """
        print("INFO : FORCED STOP")
        self.__forceStop = True

    def lireCaseConsole (self, Color=HUMAIN, placer="PLACER") :
        """ Lecture d'une case (x, y) dans la console """
        # On récupère le vecteur correspondant à la couleur
        VC = self.__Grille.getVector(Color)
        VV = self.__Grille.getVector(VIDE)

        while True:
            try:
                print("*"*3 + placer + "*"*3, end='')
                X, Y = input("X, Y ? ").split()
                X, Y = int(X), int(Y)

                if X >= self.__dim or Y >= self.__dim : raise IndexError # vérifions que les coordonées sont dans les bornes
                elif placer == "PLACER" and (X, Y) not in VV : raise IllegalMoveError # Vérifions que la case à placer est bien disponible
                elif placer == "LIBERER" and (X, Y) not in VC : raise IllegalMoveError # Vérifions que la case à libérer est bien libérable

            except (ValueError, IndexError, IllegalMoveError) as e :
                self.handleError(e)
                continue
            break
        return (X, Y)

    def lireCaseUI (self, Color=HUMAIN, placer="PLACER") :
        """ Lecture d'une case (x, y) dans la console """
        # On récupère le vecteur correspondant à la couleur
        VC = self.__Grille.getVector(Color)
        VV = self.__Grille.getVector(VIDE)

        while True:
            try:
                print("*"*3 + placer + "*"*3, end='\t')
                print("Waiting for human player ...", end='\t\n')
                self.__Application.wait_variable(self.__Application.getCaseJoueeVariable())

                def stringToTuple(s): # s est de la forme d'un tuple
                    try :
                        sTuple = s[1:-1].split(', ') # [1:-1] pour enlever les parenthèses
                    except (AttributeError, IndexError) :
                        print("ERROR : Oops! An internal error occurred...")
                        print("\tDEBUG : error while trying to convert string to tuple")
                    return sTuple

                (X, Y) = stringToTuple(self.__Application.getCaseJoueeVariable().get())
                # DEBUG: print("X=%s, Y=%s"%(X,Y))

                # Transformons en tuple d'int
                (X, Y) = (int(X), int(Y))
                if placer == "PLACER" and (X, Y) not in VV : raise IllegalMoveError # Vérifions que la case à placer est bien disponible
                elif placer == "LIBERER" and (X, Y) not in VC : raise IllegalMoveError # Vérifions que la case à libérer est bien libérable

            except (ValueError, TypeError, IndexError, IllegalMoveError) as e :
                self.handleError(e)
                continue
            break
        return (X, Y)

    def selectionnerModeJeu(self):
        while True :
            print("Q : Which mode do you wanna play ? ", end='\t\n')

            if not self.__isConsoleActive :
                # Attendons d'avoir choisi un mode de jeu
                self.__Application.wait_variable(self.__Application.getModeJeuVariable())
                    # ... et notons-le
                self.__ModeJeu = self.__Application.getModeJeuVariable().get()
            else :
                try:
                    # On affiche les modes existants
                    for (mode, text) in MODES :
                        print("\t%d : %s"%(mode, text))

                    # quel mode ?
                    self.__ModeJeu = int(input("? "))

                    # Confirmation
                    print("INFO : Vous avez selectionné le mode " + str(self.__ModeJeu))
                except (ValueError, TypeError, IndexError) as e :
                    self.handleError(e)
                    continue
            break

    def handleError(self, error) :
        """ Error handling function """
        type_err = type(error)
        if type_err == ValueError :
            print("ERROR : Oops!  That was no valid number.  Try again...")
        elif type_err == TypeError :
            print("ERROR : Oops! Cannot convert to int. Try again...")
        elif type_err == IndexError :
            print("ERROR : Oops!  That number was out of bounds.  Try again...")
        elif type_err == IllegalMoveError :
            print("ERROR : Oops! That was an illegal move. Try again...")
        else :
            print("ERROR : Oops! An error occurred but idk why. Try again...")
        print("ERROR : %s, %s"%(type_err, error))
        print("DEBUG : Handling error in handleError function...")
        # DEBUG: traceback.print_exc()


    # =============================================================================
    #                       Fonctions pour jouer un coup
    # =============================================================================
    # def placer_pion_random(self, Color):
    #     """ Place un pion au hasard dans la grille après l'avoir enlevé """
    #     # TODO: effacer cette fonction qui est passée dans Tour
    #     # On récupère le vecteur correspondant à la couleur
    #     VC = self.__Grille.getVector(Color)
    #     VV = self.__Grille.getVector(VIDE)
    #
    #     # S'il y a plus de __nbPions pions Color, on libère un pion de la grille...
    #     if len(VC) >= self.__nbPions :
    #         VV.append(VC.pop(random.randint(0, len(VC)-1)))
    #
    #     # ... et on positionne un nouveau pion
    #     VC.append(VV.pop(random.randint(0, len(VV)-1)))

    def placer_pion(self, Color) :
        """ Place un pion """
        if Color == HUMAIN :
            self.placer_pion_humain(Color)
        else :
            self.placer_pion_machine(Color)

        # Changeons et effaçons les textes des boutons
        if not self.__isConsoleActive : self.updateButtonText(Color)

    def placer_pion_humain(self, Color):
        """ Permet au joueur humain de placer un pion """
        # On récupère le vecteur correspondant à la couleur
        VC = self.__Grille.getVector(Color)
        VV = self.__Grille.getVector(VIDE)

        # Tuple des 2 fonctions à utiliser en fonction de __isConsoleActive
        lire = (self.lireCaseUI, self.lireCaseConsole)

        # S'il y a plus de __nbPions pions Color, on libère un pion de la grille...
        if len(VC) >= self.__nbPions :
            # On récupère les coordonnées d'une case au clavier (dans la console)
                # lireCaseConsole contrôle aussi la possibilité de jouer ce coup
            VV.append(VC.pop(VC.index(lire[self.__isConsoleActive](Color=Color, placer="LIBERER"))))

        # ... et on positionne un nouveau pion
        VC.append(VV.pop(VV.index(lire[self.__isConsoleActive](Color=Color, placer="PLACER"))))

    def placer_pion_machine(self, Color):
        """ Joue le tour de la machine """
        tour = self.__TAB_TOUR[self.__ModeJeu](self.__Grille, Color)
        tour.jouerUnTour()
        del tour

    def placer_pion_2machines(self, Color):
        """ Joue le tour de la machine contre elle même """
        tour = self.__TAB_TOUR[self.__ModeJeu][Color](self.__Grille, Color) # le changement avec précédemment est que __TAB_TOUR contient pour ce type de partie des tuples de 2 tours
        tour.jouerUnTour()
        del tour

    # =============================================================================
    #                       Fontions pour lancer le jeu
    # =============================================================================
    def jouer(self):
        """ Procédure de jouer (boucle principale) """
        # TODO: màj avec Tour
        print("INFO : Let's play !")
        # Choisissons une couleur
        color = self.__colorInit

        # Init des conditions de fin de boucle
        self.__forceStop = False
        self.__inGame = True

        while self.__inGame :
            try :
                # FORCE STOP (ou pas...)
                if self.__forceStop :
                    return

                # Fonction Jouer
                self.__TAB_PLACER_PION[self.__ModeJeu](color)
                self.__inGame = not(self.__Grille.gagnant(color))
                self.checkRepetition()

                self.__Grille.afficherGrilleConsole()

                if self.__inGame :
                    color = not(color) # changeColor
            except FinDuJeuParRepetitionError :
                print("ERROR : Oops! Feels something like Déjà Vu...")
                break
            except Exception :
                print("ERROR : Unknown error, shutting down...")
                traceback.print_exc()
                self.__Application.quit()
                break

        print("-------- %s a gagné ! ---------"%UI[color])

    # =============================================================================
    #                               get...()
    # =============================================================================
    def getDim (self):
        return self.__dim


# # =============================================================================
# #                           Classe Tk Error Catcher
# # =============================================================================
#
# class TkErrorCatcher:
#     """
#     In some cases tkinter will only print the traceback. Enables the program to catch tkinter errors normally
#     """
#
#     def __init__(self, func, subst, widget):
#         self.func = func
#         self.subst = subst
#         self.widget = widget
#
#     def __call__(self, *args):
#         try:
#             if self.subst:
#                 args = self.subst(*args)
#             return self.func(*args)
#         except SystemExit as msg:
#             raise SystemExit(msg)
#         except Exception as err:
#             raise err
