from abc import ABC, abstractmethod
from enum import Enum


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


DICE_VALUES = [6, 5, 4, 3, 2, 1]


class CategoryScorer(ABC):
    @abstractmethod
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        raise NotImplementedError


class ChanceScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        return sum(dice)


class YatzyBonusScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        return 50 if 5 in dice_frequencies.values() else 0


class FaceScorer(CategoryScorer):
    def __init__(self, face: int) -> None:
        self.face = face

    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        return dice_frequencies[self.face] * self.face


class HighestOfKindScorer(CategoryScorer):
    def __init__(self, min_count: int, stop_on_first: bool) -> None:
        self.min_count = min_count
        self.stop_on_first = stop_on_first

    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        total = 0
        for value in DICE_VALUES:
            if dice_frequencies[value] >= self.min_count:
                total = value * self.min_count
                if self.stop_on_first:
                    break
        return total


class StraightScorer(CategoryScorer):
    def __init__(self, excluded_face: int) -> None:
        self.excluded_face = excluded_face

    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        distinct_singles = sum(1 for freq in dice_frequencies.values() if freq == 1)
        if distinct_singles == 5 and dice_frequencies[self.excluded_face] == 0:
            return sum(dice)
        return 0


class TwoPairsScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        matching_faces = [value for value in DICE_VALUES if dice_frequencies[value] >= 2]
        if len(matching_faces) == 2:
            return sum(value * 2 for value in matching_faces)
        return 0


class FullHouseScorer(CategoryScorer):
    def score(self, dice, dice_frequencies: dict[int, int]) -> int:
        frequencies = dice_frequencies.values()
        if 2 in frequencies and 3 in frequencies:
            return sum(dice)
        return 0


CATEGORY_SCORERS: dict[YatzyCategory, CategoryScorer] = {
    YatzyCategory.CHANCE: ChanceScorer(),
    YatzyCategory.YATZY: YatzyBonusScorer(),
    YatzyCategory.ONES: FaceScorer(1),
    YatzyCategory.TWOS: FaceScorer(2),
    YatzyCategory.THREES: FaceScorer(3),
    YatzyCategory.FOURS: FaceScorer(4),
    YatzyCategory.FIVES: FaceScorer(5),
    YatzyCategory.SIXES: FaceScorer(6),
    YatzyCategory.PAIR: HighestOfKindScorer(min_count=2, stop_on_first=True),
    YatzyCategory.THREE_OF_A_KIND: HighestOfKindScorer(min_count=3, stop_on_first=False),
    YatzyCategory.FOUR_OF_A_KIND: HighestOfKindScorer(min_count=4, stop_on_first=False),
    YatzyCategory.SMALL_STRAIGHT: StraightScorer(excluded_face=6),
    YatzyCategory.LARGE_STRAIGHT: StraightScorer(excluded_face=1),
    YatzyCategory.TWO_PAIRS: TwoPairsScorer(),
    YatzyCategory.FULL_HOUSE: FullHouseScorer(),
}


class Yatzy:
    def score(self, dice, category: YatzyCategory) -> int:
        dice_frequencies = self._calculate_frequencies(dice)
        scorer = CATEGORY_SCORERS.get(category)
        if scorer is None:
            return 0
        return scorer.score(dice, dice_frequencies)

    def _calculate_frequencies(self, dice) -> dict[int, int]:
        frequencies = {value: 0 for value in DICE_VALUES}
        for die in dice:
            frequencies[die] += 1
        return frequencies
