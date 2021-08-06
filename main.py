from typing import Callable, Any


class InputParameterVerificationError(Exception):
    """Ошибка входных параметров."""

    def __init__(self, message: str):
        """Конструктор класса."""
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"InputParameterVerificationError: {self.message}"


class ResultVerificationError(Exception):
    """Ошибка выходных параметров."""

    def __init__(self, message: str):
        """Конструктор класса."""
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"ResultVerificationError: {self.message}"


class RepeatTimesValueError(Exception):
    """Ошибка значения количества повторов."""

    def __init__(self, message: str):
        """Конструктор класса."""
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"RepeatTimesValueError: {self.message}"


def input_output_validation(
    input_validation: Callable[..., bool],
    result_validation: Callable[..., bool],
    on_fail_repeat_times: int = 1,
    default_behavior: Callable[[], None] = None,
) -> Callable:
    """
    Универсальный декоратор для валидации входных и выходных параметров функции.

    Принимает параметры для декоратор.
    """

    def create_decorator(func: Callable) -> Callable:
        """Создает декоратор."""

        def decorator(*args: Any, **kwargs: Any) -> Any:
            """Декоратор, который подменяет исходную функцию."""
            if on_fail_repeat_times == 0:
                raise RepeatTimesValueError("Значение параметра on_fail_repeat_times не должно быть равным нулю.")

            if not input_validation(*args, **kwargs):
                raise InputParameterVerificationError(f"неверные параметры {str(*args)} {str(**kwargs)}")

            success = False
            attempts = on_fail_repeat_times
            result = None

            while not success and attempts != 0:
                result = func(*args, **kwargs)
                success = result_validation(result)
                attempts -= 1

            if not success:
                if default_behavior:
                    default_behavior()
                else:
                    raise ResultVerificationError(f"неверный результат {str(result)}")

            return result

        return decorator

    return create_decorator
