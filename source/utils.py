import re

def get_text(selector, trim=False, default=None):
    '''
    Returns stripped text from the selector, or default if empty.
    '''
    value = selector.get()
    if value is None:
        return default
    return value.strip() if trim else value

def join_fields(fields, separator="|", default=None):
    '''
    Joins a field list into a single string with the given separator, or default if empty.
    '''
    return separator.join(fields) if fields else default

def split_first(text, separator, default=None):
    '''
    Returns the first part of a string split by separator, or default if empty.
    '''
    return text.split(separator)[0] if text else default

def parse_value(value, default=None, to_int=False):
    '''
    Removes currency symbols, percent signs, separators... Returns int, float or default.
    '''
    if not value:
        return default
    match = re.search(r"\d+(\.\d+)?", str(value).replace(".", "").replace(",", "."))
    if not match:
        return default
    try:
        return int(match.group()) if to_int else float(match.group())
    except (ValueError, TypeError):
        return default

def set_price(app, original_price, discount_price, discount_percent):
    '''
    Assigns price-related fields to the app item.
    '''
    app.original_price = parse_value(original_price)
    app.discount_price = parse_value(discount_price)
    app.discount_percent = parse_value(discount_percent, to_int=True)