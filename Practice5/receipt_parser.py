# #1
# import re

# txt = "The rain in Spain"
# x = re.search("^The.*Spain$", txt)

# print(x)

# #2

# txt = "The rain in Spain"
# x = re.findall("Portugal", txt)
# print(x)

# #3

# txt = "The rain in Spain"
# x = re.search("\s", txt)

# print("The first white-space character is located in position:", x.start())

# #4
# txt = "The rain in Spain"
# x = re.split("\s", txt)
# print(x)

# #5
# txt = "The rain in Spain"
# x = re.sub("\s", "9", txt)
# print(x)



#tasks

import re
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


MONEY_RE = re.compile(r"\b\d{1,3}(?:[ \u00A0]\d{3})*,\d{2}\b")  # 1 200,00 / 51,00
ITEM_BLOCK_RE = re.compile(
    r"(?ms)^\s*(\d+)\.\s*\n"           # номер позиции "1."
    r"(.*?)\n"                         # название (может быть многострочным)
    r"\s*(\d+,\d{3})\s*x\s*"            # qty: 2,000
    r"(\d{1,3}(?:[ \u00A0]\d{3})*,\d{2})\s*\n"  # unit price: 1 200,00
    r"\s*(\d{1,3}(?:[ \u00A0]\d{3})*,\d{2})",   # line total: 308,00
    re.MULTILINE
)

TOTAL_RE = re.compile(r"(?im)^\s*ИТОГО:\s*(\d{1,3}(?:[ \u00A0]\d{3})*,\d{2})\s*$")
DATETIME_RE = re.compile(r"(?im)^\s*Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})\s*$")
PAYMENT_RE = re.compile(r"(?im)^\s*(Банковская\s+карта|Наличные|Kaspi|Visa|Mastercard|Card|Cash)\s*:\s*$")
BIN_RE = re.compile(r"(?im)^\s*БИН\s+(\d{12})\s*$")


def money_to_decimal(s: str) -> Decimal:
    """
    '1 200,00' -> Decimal('1200.00')
    """
    s_norm = s.replace("\u00A0", " ").replace(" ", "").replace(",", ".")
    try:
        return Decimal(s_norm)
    except InvalidOperation:
        return Decimal("0.00")


def main():
    # Можно поменять путь на свой:
    path = Path("raw.txt")

    # Если файла нет, вставь текст прямо сюда (для теста)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError("Файл raw.txt не найден рядом с receipt_parser.py")

    # 1) Все цены (как в тексте, с повторами)
    all_prices = MONEY_RE.findall(text)

    # 2) Товары (позиции)
    items = []
    for m in ITEM_BLOCK_RE.finditer(text):
        idx = int(m.group(1))
        name_raw = m.group(2)
        qty = m.group(3)
        unit_price = m.group(4)
        line_total = m.group(5)

        # Почистим название: убрать лишние переводы строк/пробелы
        name = re.sub(r"\s+", " ", name_raw).strip()

        items.append({
            "index": idx,
            "name": name,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total
        })

    # 3) Итог из чека
    total_match = TOTAL_RE.search(text)
    total_receipt = total_match.group(1) if total_match else None

    # 3b) Итог посчитанный
    total_calc = sum(money_to_decimal(it["line_total"]) for it in items)

    # 4) Дата/время
    dt_match = DATETIME_RE.search(text)
    datetime_str = None
    if dt_match:
        datetime_str = f"{dt_match.group(1)} {dt_match.group(2)}"

    # 5) Способ оплаты
    pay_match = PAYMENT_RE.search(text)
    payment_method = pay_match.group(1) if pay_match else None

    # Доп: БИН
    bin_match = BIN_RE.search(text)
    bin_value = bin_match.group(1) if bin_match else None

    # 6) Структурированный JSON
    result = {
        "bin": bin_value,
        "datetime": datetime_str,
        "payment_method": payment_method,
        "prices_found": all_prices,                     # все суммы (с повторами)
        "unique_prices_found": sorted(set(all_prices)), # уникальные суммы
        "items": items,
        "total_found": total_receipt,
        "total_calculated": f"{total_calc:.2f}"
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()