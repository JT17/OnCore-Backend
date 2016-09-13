"""
Common functions used across the API.
"""

GUAT_COUNTRY_CODE = '502'


def sanitize_phone_number(number):
    if len(number) == 8:
        new_number = GUAT_COUNTRY_CODE + str(number)
    else:
        new_number = str(number)
    return int(new_number)


def get_form_data(request, debug=False):
    """Returns the request's json"""
    if debug:
        return request

    if request.get_json() is None:
        return request.form
    return request.get_json()
