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


class Yatzy:
    def score(self, dice, category: YatzyCategory) -> int:
        dice_frequencies = self._calculate_frequencies(dice)

        match category:
            case YatzyCategory.CHANCE:
                return sum(dice)

            case YatzyCategory.YATZY:
                return 50 if 5 in dice_frequencies.values() else 0

            case YatzyCategory.ONES:
                return self._score_face(dice_frequencies, 1)

            case YatzyCategory.TWOS:
                return self._score_face(dice_frequencies, 2)

            case YatzyCategory.THREES:
                return self._score_face(dice_frequencies, 3)

            case YatzyCategory.FOURS:
                return self._score_face(dice_frequencies, 4)

            case YatzyCategory.FIVES:
                return self._score_face(dice_frequencies, 5)

            case YatzyCategory.SIXES:
                return self._score_face(dice_frequencies, 6)

            case YatzyCategory.PAIR:
                return self._score_highest_of_kind(dice_frequencies, min_count=2, stop_on_first=True)

            case YatzyCategory.THREE_OF_A_KIND:
                return self._score_highest_of_kind(dice_frequencies, min_count=3, stop_on_first=False)

            case YatzyCategory.FOUR_OF_A_KIND:
                return self._score_highest_of_kind(dice_frequencies, min_count=4, stop_on_first=False)

            case YatzyCategory.SMALL_STRAIGHT:
                return self._score_straight(dice, dice_frequencies, excluded_face=6)

            case YatzyCategory.LARGE_STRAIGHT:
                return self._score_straight(dice, dice_frequencies, excluded_face=1)

            case YatzyCategory.TWO_PAIRS:
                return self._score_two_pairs(dice_frequencies)

            case YatzyCategory.FULL_HOUSE:
                return self._score_full_house(dice, dice_frequencies)

        return 0

    def _calculate_frequencies(self, dice) -> dict[int, int]:
        frequencies = {value: 0 for value in DICE_VALUES}
        for die in dice:
            frequencies[die] += 1
        return frequencies

    def _score_face(self, dice_frequencies: dict[int, int], face: int) -> int:
        return dice_frequencies[face] * face

    def _score_highest_of_kind(
        self, dice_frequencies: dict[int, int], min_count: int, stop_on_first: bool
    ) -> int:
        score = 0
        for value in DICE_VALUES:
            if dice_frequencies[value] >= min_count:
                score = value * min_count
                if stop_on_first:
                    break
        return score

    def _score_straight(
        self, dice, dice_frequencies: dict[int, int], excluded_face: int
    ) -> int:
        distinct_singles = sum(1 for freq in dice_frequencies.values() if freq == 1)
        if distinct_singles == 5 and dice_frequencies[excluded_face] == 0:
            return sum(dice)
        return 0

    def _score_two_pairs(self, dice_frequencies: dict[int, int]) -> int:
        matching_faces = [value for value in DICE_VALUES if dice_frequencies[value] >= 2]
        if len(matching_faces) == 2:
            return sum(value * 2 for value in matching_faces)
        return 0

    def _score_full_house(self, dice, dice_frequencies: dict[int, int]) -> int:
        frequencies = dice_frequencies.values()
        if 2 in frequencies and 3 in frequencies:
            return sum(dice)
        return 0
