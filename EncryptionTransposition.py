import random

def cargar_clave_transposicion():
    with open("clave_transposicion.key", "r") as archivo_clave:
        clave = archivo_clave.read()
    return clave

def genera_clave_transposicion(longitud):
    numeros = list(range(1, longitud + 1))
    random.shuffle(numeros)
    clave = " ".join(map(str, numeros))
    with open("clave_transposicion.key", "w") as archivo_clave:
        archivo_clave.write(clave)

def encriptar_transposicion(nom_archivo, clave):
    with open(nom_archivo, "r") as archivo:
        mensaje = archivo.read()
    #transposicion
    mensaje_encriptado = "".join([mensaje[int(posicion) - 1] for posicion in clave.split()])
    
    with open(nom_archivo, "w") as archivo:
        archivo.write(mensaje_encriptado)

def ajustar_clave_segun_longitud_mensaje(nom_archivo):
    # longitud del mensaje original
    with open(nom_archivo, "r") as archivo:
        longitud_mensaje = len(archivo.read())

    # Genera una clave de la misma longitud que el mensaje
    genera_clave_transposicion(longitud_mensaje)
    clave_transposicion = cargar_clave_transposicion()

    # Encripta el mensaje con la clave
    encriptar_transposicion(nom_archivo, clave_transposicion)

def desencriptar_transposicion(nom_archivo, clave):
    # Lee el archivo y aplica la desencriptación por transposición a los datos
    with open(nom_archivo, "r") as archivo:
        mensaje_encriptado = archivo.read()

    permutacion_inversa = {int(posicion): i + 1 for i, posicion in enumerate(clave.split())}
    mensaje_desencriptado = "".join([mensaje_encriptado[permutacion_inversa[i] - 1] for i in range(1, len(mensaje_encriptado) + 1)])

    with open(nom_archivo, "w") as archivo:
        archivo.write(mensaje_desencriptado)


#encriptar
ajustar_clave_segun_longitud_mensaje("../archivoTest.txt")


#desencriptar prueba
#clave = cargar_clave_transposicion()

