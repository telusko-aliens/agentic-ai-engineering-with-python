from typing import Literal
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class ConvertInput(BaseModel):
    """Input required by the currency conversion tool."""

    # amount must be a number and must be greater than 0
    amount: float = Field(
        description="How many rupees to convert",
        gt=0
    )

    # Only these three values are allowed.
    # JPY, INR, etc. will be rejected.
    currency: Literal["USD", "EUR", "GBP"] = Field(
        description="Currency to convert into"
    )


    # create tools

@tool(
    "convert_from_rupees",
    args_schema=ConvertInput
)
def convert_from_rupees(amount: float, currency: str) -> str:
    """Convert an amount in Indian rupees into another currency."""

    rates = {
        "USD": 0.012,
        "EUR": 0.011,
        "GBP": 0.0094
    }

    return f"{amount} rupees is about {amount * rates[currency]:.2f} {currency}"

# print("args", convert_from_rupees.args)
print(
    convert_from_rupees.invoke(
        {
            "amount": 5000,
            "currency": "USD"
        }
    )
)
print()

# for bad_input in [
#     {"amount": -100, "currency": "USD"},
#     {"amount": 500, "currency": "JPY"}
# ]:
#     try:
#         convert_from_rupees.invoke(bad_input)

#     except Exception as error:
#         print(
#             "Rejected",
#             bad_input,
#             "because of",
#             type(error).__name__
#         )

model=ChatOpenAI(model="gpt-4o-mini")


model_with_tools=model.bind_tools(
    [
        convert_from_rupees
    ]
)

print(model_with_tools.invoke("Tell me about AI in 1 line").content)

