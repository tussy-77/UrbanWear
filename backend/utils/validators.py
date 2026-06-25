def validate_password(password: str) -> str | None:
    """Returns a Spanish error message if the password is invalid, None if valid."""
    if len(password) < 8:
        return 'La contraseña debe tener al menos 8 caracteres'
    if not any(c.isupper() for c in password):
        return 'La contraseña debe incluir al menos una letra mayúscula'
    if not any(c.islower() for c in password):
        return 'La contraseña debe incluir al menos una letra minúscula'
    if not any(c.isdigit() for c in password):
        return 'La contraseña debe incluir al menos un número'
    return None


ADDRESS_FIELD_LIMITS = {
    'department': (100, True),
    'city':       (100, True),
    'address':    (255, True),
    'extra':      (255, False),
    'barrio':     (100, False),
    'receiver':   (100, False),
}


def validate_address(data: dict) -> str | None:
    """Returns a Spanish error message if the address payload is invalid, None if valid."""
    for field, (max_len, required) in ADDRESS_FIELD_LIMITS.items():
        value = data.get(field)

        if value in (None, ''):
            if required:
                return f'El campo "{field}" es obligatorio'
            continue

        if not isinstance(value, str):
            return f'El campo "{field}" tiene un formato inválido'

        if len(value.strip()) == 0 and required:
            return f'El campo "{field}" es obligatorio'

        if len(value) > max_len:
            return f'El campo "{field}" no puede superar los {max_len} caracteres'

    return None
