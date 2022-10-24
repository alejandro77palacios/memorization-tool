# %% Bibliotecas
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

# %% Crear base de datos
Base = declarative_base()


class Flashcard(Base):
    __tablename__ = 'flashcard'
    id = Column(Integer, primary_key=True)
    pregunta = Column(String)
    respuesta = Column(String)
    caja = Column(Integer)


engine = create_engine('sqlite:///flashcard.db?check_same_thread=False')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# %% Variables globales
menus = {'principal': ['Add flashcards', 'Practice flashcards', 'Exit'],
         'agregar_tarjetas': ['Add a new flashcard', 'Exit'],
         'practicar': ['press "y" to see the answer:', 'press "n" to skip:', 'press "u" to update:'],
         'actualizar': ['press "d" to delete the flashcard:', 'press "e" to edit the flashcard:'],
         'aprendido': ['press "y" if your answer is correct:', 'press "n" if your answer is wrong:']
         }

instrucciones_practica = 'Please press "y" to see the answer or press "n" to skip:'


# %% Funciones
def validar_entrada(entrada):
    try:
        entrada = int(entrada)
    except ValueError:
        print(f'{entrada} is not an option')
        return None
    return entrada


def mostrar_menu(menu, conteo=True):
    for i in range(len(menu)):
        if conteo:
            opcion = f'{i + 1}. {menu[i]}'
        else:
            opcion = menu[i]
        print(opcion)


def procesar_tarjeta():
    pregunta = input('\nQuestion:\n')
    while pregunta == '' or pregunta == ' ':
        pregunta = input('Question:\n')
    respuesta = input('Answer:\n')
    while respuesta == '' or respuesta == ' ':
        respuesta = input('Answer:\n')
    query = session.query(Flashcard).all()
    registro_nuevo = Flashcard(id=len(query) + 1, pregunta=pregunta, respuesta=respuesta, caja=1)
    session.add(registro_nuevo)
    session.commit()


def agregar_tarjetas():
    print()
    mostrar_menu(menus['agregar_tarjetas'])
    eleccion = validar_entrada(input())
    if eleccion is None:
        agregar_tarjetas()
    else:
        if eleccion == 1:
            procesar_tarjeta()
            agregar_tarjetas()
        elif eleccion == 2:
            main()
        else:
            print(f'{eleccion} is not an option')
            agregar_tarjetas()


def eliminar_tarjeta(tarjeta):
    query = session.query(Flashcard)
    query_filter = query.filter(Flashcard.id == tarjeta.id)
    query_filter.delete()
    session.commit()


def editar_tarjeta(tarjeta):
    print(f'current question: {tarjeta.pregunta}')
    nueva_pregunta = input('please write a new question:\n')
    if nueva_pregunta == '' or nueva_pregunta == ' ':
        nueva_pregunta = tarjeta.pregunta
    print(f'current answer: {tarjeta.respuesta}')
    nueva_respuesta = input('please write a new answer:\n')
    if nueva_respuesta == '' or nueva_respuesta == ' ':
        nueva_respuesta = tarjeta.respuesta
    query = session.query(Flashcard)
    query_filter = query.filter(Flashcard.id == tarjeta.id)
    query_filter.update({'pregunta': nueva_pregunta,
                         'respuesta': nueva_respuesta})
    session.commit()


def actualizar_tarjeta(tarjeta):
    mostrar_menu(menus['actualizar'], conteo=False)
    eleccion = input()
    if eleccion == 'd':
        eliminar_tarjeta(tarjeta)
    elif eleccion == 'e':
        editar_tarjeta(tarjeta)


def leitner(tarjeta):
    mostrar_menu(menus['aprendido'], conteo=False)
    eleccion = input()
    if eleccion == 'y':
        if tarjeta.caja == 3:
            eliminar_tarjeta(tarjeta)
        else:
            query = session.query(Flashcard)
            query_filter = query.filter(Flashcard.id == tarjeta.id)
            query_filter.update({'caja': tarjeta.caja + 1})
            session.commit()
    elif eleccion == 'n':
        query = session.query(Flashcard)
        query_filter = query.filter(Flashcard.id == tarjeta.id)
        query_filter.update({'caja': 1})
        session.commit()



def practicar():
    tarjetas = session.query(Flashcard).all()
    if len(tarjetas) == 0:
        print('\nThere is no flashcard to practice!\n')
    else:
        for tarjeta in tarjetas:
            print(f'\nQuestion: {tarjeta.pregunta}')
            mostrar_menu(menus['practicar'], conteo=False)
            eleccion = input()
            if eleccion == 'y':
                print(f'\nAnswer: {tarjeta.respuesta}')
                leitner(tarjeta)
            elif eleccion == 'n':
                continue
            elif eleccion == 'u':
                actualizar_tarjeta(tarjeta)
    main()


# %% Main
def main():
    mostrar_menu(menus['principal'])
    eleccion = validar_entrada(input())
    if eleccion is None:
        main()
    else:
        match eleccion:
            case 1:
                agregar_tarjetas()
            case 2:
                practicar()
            case 3:
                print('\nBye!')
            case _:
                print(f'{eleccion} is not an option')
                main()


main()
