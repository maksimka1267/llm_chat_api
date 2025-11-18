import decimal
from openai import OpenAI

from .config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def calc_message_cost(prompt_tokens: int, completion_tokens: int) -> decimal.Decimal:
    from .config import settings as s
    cost = (
        decimal.Decimal(prompt_tokens) / 1000 * s.INPUT_PRICE_PER_1K +
        decimal.Decimal(completion_tokens) / 1000 * s.OUTPUT_PRICE_PER_1K
    )
    return cost.quantize(decimal.Decimal("0.000001"))
