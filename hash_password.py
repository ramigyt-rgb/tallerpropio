import getpass
import bcrypt

password = getpass.getpass("Contraseña nueva: ").encode("utf-8")
confirm = getpass.getpass("Repetir contraseña: ").encode("utf-8")
if password != confirm:
    raise SystemExit("Las contraseñas no coinciden.")
print("\nPegá este valor en [auth] password_hash:\n")
print(bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode("utf-8"))
