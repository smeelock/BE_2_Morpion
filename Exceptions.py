# =============================================================================
#                       Exceptions relatives au jeu
# =============================================================================


class FinDuJeuParRepetitionError(Exception):
    """ Raised when the game finds itself in the exact same position as it once was before """
    pass

class IllegalMoveError (Exception):
    """ Raised when trying to make an illegal move """
    pass

class depthError(Exception):
    """" Raised when MinMax algorithm exceeds maximum depth or is too low """
    pass

# class NewGameException(Exception):
#     """ Raised when new game is requested """
#     pass
#
# class KillGameException(Exception):
#     """ Raised when trying to kill the game """
#     pass
