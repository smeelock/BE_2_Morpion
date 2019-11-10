import numpy as np
import random
import time

from Grille import *
# from Exceptions import depthError

MAX, MIN = True, False
MAXIMUM_DEPTH = 4

# =============================================================================
#                               Interface Tour
# =============================================================================
class Tour :
    def __init__(self, Grille, Color):
        self._Grille = Grille
        self._Color = Color

    def getColor(self):
        return self._Color

    def jouerUnTour(self):
        pass

# =============================================================================
#                       Classe Tour pour Random
# =============================================================================
class TourRandom(Tour):
    def __init__(self, Grille, Color):
        super().__init__(Grille, Color)

    def jouerUnTour(self):
        """ Place un pion au hasard dans la grille après l'avoir enlevé """
        # On récupère le vecteur correspondant à la couleur
        VC = self._Grille.getVector(self._Color)
        VV = self._Grille.getVector(VIDE)

        # S'il y a plus de __nbPions pions Color, on libère un pion de la grille...
        if len(VC) >= self._Grille.getNbPions() :
            VV.append(VC.pop(random.randint(0, len(VC)-1)))

        # ... et on positionne un nouveau pion
        VC.append(VV.pop(random.randint(0, len(VV)-1)))

# =============================================================================
#                       Classe Tour pour Best First
# =============================================================================
class TourBestFirst(Tour):
    def __init__(self, Grille, Color):
        super().__init__(Grille, Color)

    def trouverProchaineCase(self):
        """ Trouve la case la plus prometteuse à partir de fonctionEvaluation """
        VV = self._Grille.getVector(VIDE)
        if len(VV) == self._Grille.getDim()**2:       # les 2 listes VB et VN sont vides
            nextCase = random.choice(VV)
        else :
            scores = [self._Grille.evaluation(self._Color, case) for case in VV]

            indice = scores.index(max(scores))  # on récupère l'indice du score maximal
            nextCase = VV[indice]

        return nextCase

    def supprimerCase(self):
        """ Trouve la pire des cases pour le joueur color à partir de fonctionEvaluation """
        lst = self._Grille.getVector(self._Color)

        scores = [self._Grille.evaluation(self._Color, case) for case in lst]

        indice = scores.index(min(scores))  # on récupère l'indice du score minimal (la plus mauvaise case)
        caseASupprimer = lst[indice]
        return caseASupprimer

    def jouerUnTour(self):
        """ Jouer un tour """
        # On récupère le vecteur correspondant à la couleur
        VC = self._Grille.getVector(self._Color)
        VV = self._Grille.getVector(VIDE)

        # S'il y a plus de __nbPions pions Color, on libère le pire pion de la grille...
        if len(VC) >= self._Grille.getNbPions():
            caseASupprimer = self.supprimerCase()
            VV.append(VC.pop(VC.index(caseASupprimer)))

        # ... et on positionne un nouveau pion (le meilleur)
        nextCase = self.trouverProchaineCase()
        VC.append(VV.pop(VV.index(nextCase)))


# =============================================================================
#                       Classe Tour pour MinMax
# =============================================================================
class TourMinMax(Tour):
    def __init__(self, Grille, Color, maximumDepth=MAXIMUM_DEPTH):
        super().__init__(Grille, Color)
        self.__maximumDepth = maximumDepth
        self.__mode = MAX

    def getMaxDepth(self):
        return self.__maximumDepth

    def plateauxSuccesseursMoinsDe_NbPions(self, grille, Color):
        """ Génère tous les successeur du plateau où on n’a pas encore joué nbPions pions """
        # On récupère le vecteur correspondant à la couleur
        VC = grille.getVector(Color)
        VV = grille.getVector(VIDE)

        liste = []
        N, nbPions = grille.getDim(), grille.getNbPions()

        for case in VV :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="PLACER") # on effectue le mvt
            liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def plateauxSuccesseursDeja_nbPions(self, grille, Color):
        """ Génère tous les plateaux possibles où on enlève un pion playingColor et on le place dans une case vide (autre que celle qu’on vient de vider) """
        # On récupère le vecteur correspondant à la couleur
        VC = grille.getVector(Color)
        VV = grille.getVector(VIDE)

        liste = []
        N, nbPions = grille.getDim(), grille.getNbPions()

        for case in VC :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="LIBERER") # on enlève ce pion

            for caseVide in VV :
                if caseVide != case:
                    newGrille.echangerCase(case, Color, placer="PLACER")
                    liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def minMax(self, grille, profondeur, mode, playingColor):
        """ MinMax """
        # print("DEBUG: playingColor {}".format(playingColor))
        # print("DEBUG: profondeur {}".format(profondeur))
        # Condition d'arrêt de l'appel récursif :
        oldColor = not(playingColor)
        if not grille.isEmpty():
            if profondeur == 0 or grille.gagnant(oldColor): # plateau gagnant ou profondeur max atteinte
                return (grille, grille.valeurPlateau(oldColor))

        # Initialisation des variables utiles
        minScore = np.inf
        maxScore = -np.inf
        meilleureCaseAJouer = None
        listePlateauxSuccesseurs = []

        VC = grille.getVector(playingColor)

        # Récupération des plateaux successeurs
        if len(VC) < grille.getNbPions():
            listePlateauxSuccesseurs = self.plateauxSuccesseursMoinsDe_NbPions(grille, playingColor)
        else:
            listePlateauxSuccesseurs = self.plateauxSuccesseursDeja_nbPions(grille, playingColor)

        # Calcul des valeurs de ces plateaux par appels successifs de minMax
        for plateau in listePlateauxSuccesseurs: # ~foreach child of node DO :
            plateau_renvoye_par_minMax, score = self.minMax(plateau, profondeur-1, not(mode), not(playingColor)) # not() pour changer de min à max et blanc à noir

            # Màj des scores calculés par minMax
            if mode == MAX:
                if score > maxScore:
                    bestScore = score
                    bestPlateau = plateau
                    maxScore = bestScore

            else:
                if score < minScore:
                    bestScore = score
                    bestPlateau = plateau
                    minScore = bestScore
        return (bestPlateau, bestScore)

    def jouerUnTour(self, profondeur=2):
        """ Jouer un tour """
        # Si l'ordi est premier à jouer, jouer au centre par défaut (à cause de RecursionError...)
        if self._Grille.isEmpty():
            N = self._Grille.getDim()
            self._Grille.echangerCase((N//2, N//2), self._Color, placer="PLACER")
            return

        # Jouons avec minMax
        timeInit = time.time()
        mode = MAX
        newPlateau, valeurPlateau = self.minMax(self._Grille, profondeur, mode, self._Color)
        print("INFO: minMax computed in {}s".format(time.time() - timeInit))
        newPlateau.afficherGrilleConsole()
        self._Grille.resetGrille(newPlateau)

# =============================================================================
#                       Classe Tour pour Alpha Beta
# =============================================================================
class TourAlphaBeta(Tour):
    # Idem minMax MAIS alpha beta change ...
    def __init__(self, Grille, Color, maximumDepth=MAXIMUM_DEPTH):
        super().__init__(Grille, Color)
        self.__maximumDepth = maximumDepth
        self.__mode = MAX

    def getMaxDepth(self):
        return self.__maximumDepth

    def plateauxSuccesseursMoinsDe_NbPions(self, grille, Color):
        """ Génère tous les successeur du plateau où on n’a pas encore joué nbPions pions """
        # On récupère le vecteur correspondant à la couleur
        VC = grille.getVector(Color)
        VV = grille.getVector(VIDE)

        liste = []
        N, nbPions = grille.getDim(), grille.getNbPions()

        for case in VV :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="PLACER") # on effectue le mvt
            liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def plateauxSuccesseursDeja_nbPions(self, grille, Color):
        """ Génère tous les plateaux possibles où on enlève un pion playingColor et on le place dans une case vide (autre que celle qu’on vient de vider) """
        # On récupère le vecteur correspondant à la couleur
        VC = grille.getVector(Color)
        VV = grille.getVector(VIDE)

        liste = []
        N, nbPions = grille.getDim(), grille.getNbPions()

        for case in VC :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="LIBERER") # on enlève ce pion

            for caseVide in VV :
                if caseVide != case:
                    newGrille.echangerCase(case, Color, placer="PLACER")
                    liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def alphaBeta(self, Grille, profondeur, mode, playingColor, alpha, beta):
        """ Alpha Beta : improvement of minmax algorithm
            -------------
            alpha : minimum score assured for maximizing player
            beta : maximum score assured for minimizing player
        """
        # L'objectif est d'écarter des branches qui n'influencerons pas la décision finale
        # https://en.wikipedia.org/wiki/Alpha–beta_pruning
        # alpha/beta cut-off : il est inutile de poursuivre l'évaluation des child de cette branche
        #                      car on a prouvé qu'elle était (strictement) moins bien qu'au moins une autre (alpha >= beta)

        # Condition d'arrêt de l'appel récursif (idem minMax):
        oldColor = not(playingColor)
        if not Grille.isEmpty():
            if profondeur == 0 or Grille.gagnant(oldColor): # plateau gagnant ou profondeur max atteinte
                return (Grille, Grille.valeurPlateau(oldColor))

        # Initialisation des variables utiles
        minScore = np.inf
        maxScore = -np.inf
        meilleureCaseAJouer = None
        listePlateauxSuccesseurs = []

        VC = Grille.getVector(playingColor)

        # Récupération des plateaux successeurs
        if len(VC) < Grille.getNbPions():
            listePlateauxSuccesseurs = self.plateauxSuccesseursMoinsDe_NbPions(Grille, playingColor)
        else:
            listePlateauxSuccesseurs = self.plateauxSuccesseursDeja_nbPions(Grille, playingColor)

        # Calcul des valeurs de ces plateaux par appels successifs de minMax
        for plateau in listePlateauxSuccesseurs: # ~foreach child of node DO :
            plateau_renvoye_par_alphaBeta, score = self.alphaBeta(grille, profondeur-1, not(mode), not(playingColor), alpha, beta) # not() pour changer de min à max et blanc à noir

            # Màj des scores calculés par minMax et condition d'arrêt AlphaBeta
            if mode == MAX:
                if score > maxScore:
                    bestScore = score
                    bestPlateau = plateau_renvoye_par_alphaBeta
                    maxScore = bestScore

                alpha = max(alpha, score)
                if alpha >= beta : # Condition d'arrêt AlphaBeta
                    break # beta cut-off

            else:
                if score < minScore:
                    bestScore = score
                    bestPlateau = plateau_renvoye_par_alphaBeta
                    minScore = bestScore

                beta = min(beta, score)
                if alpha >= beta : # Condition d'arrêt AlphaBeta
                    break # alpha cut-off

        return (bestPlateau, bestScore)

    def jouerUnTour(self, profondeur=6):
        """ Jouer un tour """
        # Si l'ordi est premier à jouer, jouer au centre par défaut (à cause de RecursionError...)
        if self._Grille.isEmpty():
            N = self._Grille.getDim()
            self._Grille.echangerCase((N//2, N//2), self._Color, placer="PLACER")
            return

        # Jouons avec Alpha Beta
        timeInit = time.time()
        mode = MAX
        alpha = -np.inf
        beta = np.inf
        newPlateau, valeurPlateau = self.alphaBeta(self._Grille, profondeur, mode, self._Color, alpha, beta)
        print("INFO: Alpha Beta computed in {}s".format(time.time() - timeInit))
        self._Grille.resetGrille(newPlateau)
