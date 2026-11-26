from abc import ABC, abstractmethod
from enum import Enum

DICE_FACES_DESCENDING = [6, 5, 4, 3, 2, 1]
YATZY_BONUS_SCORE = 50
STRAIGHT_DISTINCT_COUNT = 5
SMALL_STRAIGHT_EXCLUDED_FACE = 6
LARGE_STRAIGHT_EXCLUDED_FACE = 1
PAIR_SIZE = 2
TWO_PAIRS_COUNT = 2
FULL_HOUSE_PAIR_COUNT = 2
FULL_HOUSE_TRIPLE_COUNT = 3


class YatzyCategory(Enum):
    CHANCE = 0
    YATZY = 1
    ONES = 2
    TWOS = 3
    THREES = 4
    FOURS = 5
    FIVES = 6
    SIXES = 7
    PAIR = 8
    THREE_OF_A_KIND = 9
    FOUR_OF_A_KIND = 10
    SMALL_STRAIGHT = 11
    LARGE_STRAIGHT = 12
    TWO_PAIRS = 13
    FULL_HOUSE = 14


class CategoryScorer(ABC):
    @abstractmethod
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        raise NotImplementedError


class ChanceScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        return sum(dice)


class YatzyBonusScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        return YATZY_BONUS_SCORE if 5 in dice_frequencies.values() else 0


class SingleFaceScorer(CategoryScorer):
    def __init__(self, face: int) -> None:
        self.face = face

    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        return dice_frequencies[self.face] * self.face


class HighestOfKindScorer(CategoryScorer):
    def __init__(self, required_count: int, stop_on_first: bool) -> None:
        self.required_count = required_count
        self.stop_on_first = stop_on_first

    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        total = 0
        for face in DICE_FACES_DESCENDING:
            if dice_frequencies[face] >= self.required_count:
                total = face * self.required_count
                if self.stop_on_first:
                    break
        return total


class StraightScorer(CategoryScorer):
    def __init__(self, excluded_face: int) -> None:
        self.excluded_face = excluded_face

    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        single_count = sum(1 for freq in dice_frequencies.values() if freq == 1)
        if single_count == STRAIGHT_DISTINCT_COUNT and dice_frequencies[self.excluded_face] == 0:
            return sum(dice)
        return 0


class TwoPairsScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        paired_faces = [face for face in DICE_FACES_DESCENDING if dice_frequencies[face] >= PAIR_SIZE]
        if len(paired_faces) == TWO_PAIRS_COUNT:
            return sum(face * PAIR_SIZE for face in paired_faces)
        return 0


class FullHouseScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        frequencies = dice_frequencies.values()
        if FULL_HOUSE_PAIR_COUNT in frequencies and FULL_HOUSE_TRIPLE_COUNT in frequencies:
            return sum(dice)
        return 0


CATEGORY_SCORERS: dict[YatzyCategory, CategoryScorer] = {
    YatzyCategory.CHANCE: ChanceScorer(),
    YatzyCategory.YATZY: YatzyBonusScorer(),
    YatzyCategory.ONES: SingleFaceScorer(1),
    YatzyCategory.TWOS: SingleFaceScorer(2),
    YatzyCategory.THREES: SingleFaceScorer(3),
    YatzyCategory.FOURS: SingleFaceScorer(4),
    YatzyCategory.FIVES: SingleFaceScorer(5),
    YatzyCategory.SIXES: SingleFaceScorer(6),
    YatzyCategory.PAIR: HighestOfKindScorer(required_count=PAIR_SIZE, stop_on_first=True),
    YatzyCategory.THREE_OF_A_KIND: HighestOfKindScorer(required_count=3, stop_on_first=False),
    YatzyCategory.FOUR_OF_A_KIND: HighestOfKindScorer(required_count=4, stop_on_first=False),
    YatzyCategory.SMALL_STRAIGHT: StraightScorer(excluded_face=SMALL_STRAIGHT_EXCLUDED_FACE),
    YatzyCategory.LARGE_STRAIGHT: StraightScorer(excluded_face=LARGE_STRAIGHT_EXCLUDED_FACE),
    YatzyCategory.TWO_PAIRS: TwoPairsScorer(),
    YatzyCategory.FULL_HOUSE: FullHouseScorer(),
}


class Yatzy:
    def score(self, dice, category: YatzyCategory) -> int:
        dice_frequencies = self._count_dice_frequencies(dice)
        scorer = CATEGORY_SCORERS.get(category)
        if scorer is None:
            return 0
        return scorer.score(dice, dice_frequencies)

    def _count_dice_frequencies(self, dice) -> dict[int, int]:
        frequencies = {face: 0 for face in DICE_FACES_DESCENDING}
        for die in dice:
            frequencies[die] += 1
        return frequencies
