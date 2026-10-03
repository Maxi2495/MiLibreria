from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.models.catalogo import Libro

def test():
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).first()
        libro = db.query(Libro).first()
        print(" Conexión exitosa a la base de datos.")
        if usuario:
            print(f" Usuario encontrado: {usuario.nombre} {usuario.apellido} ({usuario.email})")
        if libro:
            print(f" Libro encontrado: {libro.titulo} (ISBN: {libro.isbn})")
    except Exception as e:
        print(f" Error de conexión: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test()