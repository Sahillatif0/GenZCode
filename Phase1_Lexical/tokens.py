"""Token types for GenZ/Brainrot language."""

from enum import Enum, auto
from typing import Optional


class TokenType(Enum):
    """All token types for the GenZ language."""

    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENT = auto()

    # Keywords
    LOWKEY = auto()      # variable declaration
    NUM = auto()         # numeric type
    TXT = auto()         # string type
    SUS = auto()         # if
    DEADASS = auto()     # else
    KEEP_YAPPING = auto()  # while
    SPILL_TEA = auto()   # print
    VIBE_CHECK = auto()  # function
    SLAY = auto()        # return
    BOUNCE = auto()      # break (leave the situation)
    BESTIE = BOUNCE       # alias for bounce
    NEXT_UP = auto()     # continue (next iteration)
    ITS_GIVING = NEXT_UP  # alias for next_up
    NO_CAP = auto()      # true
    FR_FR = auto()       # false
    RATIO = auto()       # switch
    BET = auto()         # case
    NVM = auto()         # default (nvm, that's it)
    TUNG_TUNG_TUNG_SAHUR = auto()
    BALLERINA_CAPPUCCINA = auto()
    SKIBIDI_TOILET = auto()
    SKIBIDI = auto()
    FANUM_TAX = auto()
    RIZZ = auto()
    OHIO = auto()
    MEWING = auto()
    GRIMACE_SHAKE = auto()
    GOON = auto()
    EDGE = auto()
    YAPPING_THROUGH = auto()  # for loop

    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    PERCENT = auto()     # %
    ASSIGN = auto()      # =
    EQ = auto()          # ==
    NEQ = auto()         # !=
    LT = auto()          # <
    GT = auto()          # >
    LTE = auto()         # <=
    GTE = auto()         # >=
    AND = auto()         # &&
    OR = auto()          # ||
    NOT = auto()         # !

    # Punctuation
    LBRACE = auto()      # {
    RBRACE = auto()       # }
    LPAREN = auto()      # (
    RPAREN = auto()       # )
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    SEMI = auto()         # ;
    COMMA = auto()        # ,
    COLON = auto()        # :

    # Special
    EOF = auto()
    COMMENT = auto()     # // ... (ignored)


KEYWORDS = {
    'lowkey': TokenType.LOWKEY,
    'num': TokenType.NUM,
    'txt': TokenType.TXT,
    'sus': TokenType.SUS,
    'deadass': TokenType.DEADASS,
    'keep_yapping': TokenType.KEEP_YAPPING,
    'spill_tea': TokenType.SPILL_TEA,
    'vibe_check': TokenType.VIBE_CHECK,
    'slay': TokenType.SLAY,
    'bounce': TokenType.BOUNCE,
    'bestie': TokenType.BOUNCE,
    'next_up': TokenType.NEXT_UP,
    'its_giving': TokenType.NEXT_UP,
    'no_cap': TokenType.NO_CAP,
    'fr_fr': TokenType.FR_FR,
    'ratio': TokenType.RATIO,
    'bet': TokenType.BET,
    'nvm': TokenType.NVM,
    'tung_tung_tung_sahur': TokenType.TUNG_TUNG_TUNG_SAHUR,
    'ballerina_cappuccina': TokenType.BALLERINA_CAPPUCCINA,
    'skibidi_toilet': TokenType.SKIBIDI_TOILET,
    'skibidi': TokenType.SKIBIDI,
    'fanum_tax': TokenType.FANUM_TAX,
    'rizz': TokenType.RIZZ,
    'ohio': TokenType.OHIO,
    'mewing': TokenType.MEWING,
    'grimace_shake': TokenType.GRIMACE_SHAKE,
    'goon': TokenType.GOON,
    'edge': TokenType.EDGE,
    'yapping_through': TokenType.YAPPING_THROUGH,
}


class Token:
    """Represents a single token in the source code."""

    def __init__(
        self,
        type: TokenType,
        lexeme: str,
        literal: Optional[object] = None,
        line: int = 0,
        column: int = 0,
    ):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.lexeme}', {self.literal})"