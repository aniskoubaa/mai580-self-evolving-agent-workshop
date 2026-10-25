from tools.tool import Tool


class CurrencyConvert(Tool):
    """A distractor: it sounds useful but these claims have no amounts."""
    name = "currency_convert"
    description = "converts an amount of money between currencies"

    def run(self, claim):
        return "currency_convert: this claim has no amount to convert"
