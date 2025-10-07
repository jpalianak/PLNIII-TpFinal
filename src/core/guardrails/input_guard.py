from guardrails.hub import RegexMatch
from guardrails import OnFailAction
from .base_guard import BaseGuard

class InputGuard(BaseGuard):
    def __init__(self):
        validators = [
            RegexMatch(
                regex=r"^(?!.*(```|<script>|System:|User:|Assistant:)).*$",
                on_fail=OnFailAction.EXCEPTION
            )
        ]
        super().__init__(validators=validators)