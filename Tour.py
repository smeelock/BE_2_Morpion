import numpy as np
import random

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

    def plateauxSuccesseursMoinsDe_NbPions(self, Color):
        """ Génère tous les successeur du plateau où on n’a pas encore joué nbPions pions """
        # On récupère le vecteur correspondant à la couleur
        VC = self._Grille.getVector(Color)
        VV = self._Grille.getVector(VIDE)

        liste = []
        N, nbPions = self._Grille.getDim(), self._Grille.getNbPions()

        for case in VV :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(self._Grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="PLACER") # on effectue le mvt
            liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def plateauxSuccesseursDeja_nbPions(self, Color):
        """ Génère tous les plateaux possibles où on enlève un pion playingColor et on le place dans une case vide (autre que celle qu’on vient de vider) """
        # On récupère le vecteur correspondant à la couleur
        VC = self._Grille.getVector(Color)
        VV = self._Grille.getVector(VIDE)

        liste = []
        N, nbPions = self._Grille.getDim(), self._Grille.getNbPions()

        for case in VC :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(self._Grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="LIBERER") # on enlève ce pion

            for caseVide in VV :
                if caseVide != case:
                    newGrille.echangerCase(case, Color, placer="PLACER")
                    liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def minMax(self, profondeur, mode, playingColor):
        """ MinMax """
        # Condition d'arrêt de l'appel récursif :
        oldColor = not(playingColor)
        if not self._Grille.isEmpty():
            if profondeur == 0 or self._Grille.gagnant(oldColor): # plateau gagnant ou profondeur max atteinte
                return (self._Grille, self._Grille.valeurPlateau(oldColor))

        # Initialisation des variables utiles
        minScore = np.inf
        maxScore = -np.inf
        meilleureCaseAJouer = None
        listePlateauxSuccesseurs = []

        VC = self._Grille.getVector(playingColor)

        # Récupération des plateaux successeurs
        if len(VC) < self._Grille.getNbPions():
            listePlateauxSuccesseurs = self.plateauxSuccesseursMoinsDe_NbPions(playingColor)
        else:
            listePlateauxSuccesseurs = self.plateauxSuccesseursDeja_nbPions(playingColor)

        # Calcul des valeurs de ces plateaux par appels successifs de minMax
        for plateau in listePlateauxSuccesseurs: # ~foreach child of node DO :
            plateau_renvoye_par_minMax, score = self.minMax(profondeur-1, not(mode), not(playingColor)) # not() pour changer de min à max et blanc à noir

            # Màj des scores calculés par minMax
            if mode == MAX:
                if score > maxScore:
                    bestScore = score
                    bestPlateau = plateau_renvoye_par_minMax
                    maxScore = bestScore

            else:
                if score < minScore:
                    bestScore = score
                    bestPlateau = plateau_renvoye_par_minMax
                    minScore = bestScore
        return (bestPlateau, bestScore)

    def jouerUnTour(self, profondeur=6):
        """ Jouer un tour """
        # profondeur = 6
        mode = MAX
        newPlateau, valeurPlateau = self.minMax(profondeur, mode, self._Color)
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

    def plateauxSuccesseursMoinsDe_NbPions(self, Color):
        """ Génère tous les successeur du plateau où on n’a pas encore joué nbPions pions """
        # On récupère le vecteur correspondant à la couleur
        VC = self._Grille.getVector(Color)
        VV = self._Grille.getVector(VIDE)

        liste = []
        N, nbPions = self._Grille.getDim(), self._Grille.getNbPions()

        for case in VV :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(self._Grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="PLACER") # on effectue le mvt
            liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def plateauxSuccesseursDeja_nbPions(self, Color):
        """ Génère tous les plateaux possibles où on enlève un pion playingColor et on le place dans une case vide (autre que celle qu’on vient de vider) """
        # On récupère le vecteur correspondant à la couleur
        VC = self._Grille.getVector(Color)
        VV = self._Grille.getVector(VIDE)

        liste = []
        N, nbPions = self._Grille.getDim(), self._Grille.getNbPions()

        for case in VC :
            newGrille = Grille(N, nbPions) # on __init__ une nouvelle grille
            newGrille.resetGrille(self._Grille) # on y copie la grille actuelle
            newGrille.echangerCase(case, Color, placer="LIBERER") # on enlève ce pion

            for caseVide in VV :
                if caseVide != case:
                    newGrille.echangerCase(case, Color, placer="PLACER")
                    liste.append(newGrille) # on l'ajoute à la liste des mvts possibles

        return liste

    def alphaBeta(self, profondeur, mode, playingColor, alpha, beta):
        """ Alpha Beta : improvement of minmax algorithm
            -------------
            alpha : minimum score assured for maximizing player
            beta : maximum score assured for minimizing player
        """
        # L'objectif est d'écarter des branches qui n'influencerons pas la décision finale
        # https://en.wikipedia.org/wiki/Alpha–beta_pruning

        # Condition d'arrêt de l'appel récursif (idem minMax):
        oldColor = not(playingColor)
        if not self._Grille.isEmpty():
            if profondeur == 0 or self._Grille.gagnant(oldColor): # plateau gagnant ou profondeur max atteinte
                return (self._Grille, self._Grille.valeurPlateau(oldColor))

        # Initialisation des variables utiles
        minScore = np.inf
        maxScore = -np.inf
        meilleureCaseAJouer = None
        listePlateauxSuccesseurs = []

        VC = self._Grille.getVector(playingColor)

        # Récupération des plateaux successeurs
        if len(VC) < self._Grille.getNbPions():
            listePlateauxSuccesseurs = self.plateauxSuccesseursMoinsDe_NbPions(playingColor)
        else:
            listePlateauxSuccesseurs = self.plateauxSuccesseursDeja_nbPions(playingColor)

        # Calcul des valeurs de ces plateaux par appels successifs de minMax
        for plateau in listePlateauxSuccesseurs: # ~foreach child of node DO :
            plateau_renvoye_par_alphaBeta, score = self.alphaBeta(profondeur-1, not(mode), not(playingColor), alpha, beta) # not() pour changer de min à max et blanc à noir

            # Màj des scores calculés par minMax et condition d'arrêt AlphaBeta
            if mode == MAX:
                if score > maxScore:
                    bestScore = score
                    bestPlateau = plateau_renvoye_par_alphaBeta
                    maxScore = bestScore

                alpha = np.max(alpha, score)
                if alpha >= beta : # Condition d'arrêt AlphaBeta
                    break # beta cut-off

            else:
                if score < minScore:
                    bestScore = score
                    bestPlateau = plateau_renvoye_par_alphaBeta
                    minScore = bestScore

                beta = np.min(beta, score)
                if alpha >= beta : # Condition d'arrêt AlphaBeta
                    break # alpha cut-off

        return (bestPlateau, bestScore)

    def jouerUnTour(self, profondeur=6):
        """ Jouer un tour """
        pass
