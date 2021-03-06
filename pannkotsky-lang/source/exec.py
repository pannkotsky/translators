from inspect import getfullargspec
from typing import List


class Jump(Exception):
    pass


class Executor:
    OPERATIONS_MAP = {
        ':=': '_assign',
        '+': '_add',
        '-': '_subtract',
        '*': '_multiply',
        '/': '_divide',
        '^': '_to_power',
        '<': '_lt',
        '>': '_gt',
        '<=': '_lte',
        '>=': '_gte',
        '==': '_eq',
        '!=': '_ne',
        'var': '_declare_ident',
        'print': '_print',
        'input': '_input',
        'label': '_declare_label',
        'goto': '_goto',
        'goto_if_not': '_goto_if_not',
    }

    def __init__(self, tokens: List[str]):
        self._tokens = tokens
        self._current_token_index = 0
        self._idents_registry = {}
        self._output = []

    def execute(self):
        execution_stack = []

        while True:
            try:
                token = self._tokens[self._current_token_index]
            except IndexError:
                break
            execution_stack.append(token)

            if token in self.OPERATIONS_MAP:
                # in case of operation extract the amount of arguments it requires
                # and perform operation
                operation, args = self._get_operation(execution_stack)
                try:
                    res = operation(*args)
                except Jump:
                    continue

                # if operation returns some result put it back to stack
                if res is not None:
                    execution_stack.append(res)

            self._current_token_index += 1

        return self._output

    def _get_operation(self, execution_stack: List):
        """ Returns method by operation name and args it requires. """

        operation_name = self.OPERATIONS_MAP[execution_stack.pop()]
        operation = getattr(self, operation_name)
        signature = getfullargspec(operation)
        numargs = len(signature.args) - 1  # exclude 'self' arg

        assert len(execution_stack) >= numargs

        args = []
        for _ in range(numargs):
            args = [execution_stack.pop()] + args

        return operation, args

    def _get_value(self, arg, target_type=None):
        if arg in self._idents_registry:
            return self._idents_registry[arg]
        return self._cast_value(arg, target_type)

    @staticmethod
    def _cast_value(value, target_type=None):
        if target_type is not None:
            return target_type(value)

        # if we support more types in future, add type autodetection
        return int(value)

    ############### Operations ###############

    def _goto(self, token_index: str):
        self._current_token_index = self._cast_value(token_index, int)
        raise Jump

    def _goto_if_not(self, condition: bool, token_index: str):
        assert isinstance(condition, bool)
        if not condition:
            self._goto(token_index)

    def _declare_ident(self, ident: str) -> str:
        self._idents_registry[ident] = None
        return ident

    def _assign(self, ident: str, value) -> str:
        self._idents_registry[ident] = self._get_value(value)
        return ident

    def _print(self, arg):
        self._output.append(self._get_value(arg))

    def _input(self):
        while True:
            inp = input("Enter integer number: ")
            try:
                return int(inp)
            except ValueError:
                print(f"{inp} is not a valid integer number")

    def _add(self, v1, v2):
        return self._get_value(v1, int) + self._get_value(v2, int)

    def _subtract(self, v1, v2):
        return self._get_value(v1, int) - self._get_value(v2, int)

    def _multiply(self, v1, v2):
        return self._get_value(v1, int) * self._get_value(v2, int)

    def _divide(self, v1, v2):
        return self._get_value(v1, int) // self._get_value(v2, int)

    def _to_power(self, value, power):
        return self._get_value(value, int) ** self._get_value(power)

    def _lt(self, v1, v2) -> bool:
        return self._get_value(v1, int) < self._get_value(v2, int)

    def _lte(self, v1, v2) -> bool:
        return self._get_value(v1, int) <= self._get_value(v2, int)

    def _gt(self, v1, v2) -> bool:
        return self._get_value(v1, int) > self._get_value(v2, int)

    def _gte(self, v1, v2) -> bool:
        return self._get_value(v1, int) >= self._get_value(v2, int)

    def _eq(self, v1, v2) -> bool:
        return self._get_value(v1, int) == self._get_value(v2, int)

    def _ne(self, v1, v2) -> bool:
        return self._get_value(v1, int) != self._get_value(v2, int)
