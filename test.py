import re
import json
import unittest

from typing import Union, Dict, Any, List, Type, Final
from unittest import mock

from jsonschema import validate, ValidationError
from main import (
    input_output_validation,
    InputParameterVerificationError,
    ResultVerificationError,
    RepeatTimesValueError,
)

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]
success_validation: Final = lambda *args, **kwargs: True
fail_validation: Final = lambda *args, **kwargs: False
pattern: Final = re.compile("123")


def load_json(path: str) -> JSON:
    """Загружает данные из json-файла."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def json_input_validation(data: JSON) -> bool:
    """Проверки входные параметры."""
    schema: JSON = load_json("goods.schema.json")

    try:
        validate(data, schema)
        return True
    except ValidationError:
        return False


def str_result_validation(data: str) -> bool:
    """Проверки выходные параметры."""
    return bool(pattern.match(data))


class TestInputValidation(unittest.TestCase):
    """Тестирует параметр input_validation."""

    valid_json: Final = load_json("test_valid.json")
    invalid_json: Final = load_json("test_invalid.json")

    def test_valid_json(self) -> None:
        """Позитивный тест параметра input_validation."""

        @input_output_validation(json_input_validation, success_validation)
        def json_func(_: JSON) -> None:
            pass

        json_func(self.valid_json)

    def test_invalid_json(self) -> None:
        """Негативный тест параметра input_validation."""

        @input_output_validation(json_input_validation, success_validation)
        def json_func(_: JSON) -> None:
            pass

        self.assertRaises(InputParameterVerificationError, json_func, self.invalid_json)


class TestResultValidation(unittest.TestCase):
    """Тестирует параметр result_validation."""

    valid_str: Final = "123"
    invalid_str: Final = "abc"

    def test_valid_str(self) -> None:
        """Позитивный тест параметра result_validation."""

        @input_output_validation(success_validation, str_result_validation)
        def str_func(_: str) -> str:
            return _

        str_func(self.valid_str)

    def test_invalid_str(self) -> None:
        """Негативный тест параметра result_validation."""

        @input_output_validation(success_validation, str_result_validation)
        def str_func(_: str) -> str:
            return _

        self.assertRaises(ResultVerificationError, str_func, self.invalid_str)


class TestOnFailRepeatTimes(unittest.TestCase):
    """Тестирует параметр on_fail_repeat_times."""

    results: Final = ["abc", "abc", "abc", "123"]

    def test_zero_on_fail_repeat_times(self) -> None:
        """Негативный тест параметра on_fail_repeat_times."""

        @input_output_validation(success_validation, success_validation, on_fail_repeat_times=0)
        def empty_func() -> None:
            pass

        self.assertRaises(RepeatTimesValueError, empty_func)

    def test_repeat_times_2(self) -> None:
        """Тестирует завершение по параметру on_fail_repeat_times."""
        results_iter = iter(self.results)

        @input_output_validation(success_validation, success_validation, on_fail_repeat_times=2)
        def iter_func() -> str:
            return next(results_iter)

        iter_func()

    def test_repeat_times_4(self) -> None:
        """Тестирует параметр on_fail_repeat_times на границе."""
        results_iter = iter(self.results)

        @input_output_validation(success_validation, success_validation, on_fail_repeat_times=4)
        def iter_func() -> str:
            return next(results_iter)

        iter_func()

    def test_repeat_times_10(self) -> None:
        """Тестирует завершение раньше обнуления параметра on_fail_repeat_times."""
        results_iter = iter(self.results)

        @input_output_validation(success_validation, success_validation, on_fail_repeat_times=10)
        def iter_func() -> str:
            return next(results_iter)

        iter_func()


class TestDefaultBehavior(unittest.TestCase):
    """Тестирует параметр default_behavior."""

    def test_default_behavior(self) -> None:
        """Позитивный тест параметра default_behavior."""
        default_behavior = mock.Mock()

        @input_output_validation(success_validation, fail_validation, default_behavior=default_behavior)
        def empty_func() -> None:
            pass

        empty_func()
        default_behavior.assert_called()


if __name__ == "__main__":
    unittest.main()
