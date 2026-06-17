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
