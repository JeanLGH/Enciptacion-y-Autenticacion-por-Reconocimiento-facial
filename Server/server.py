import cv2
import os
import time
import socket
import struct
import random

def cargar_clave_transposicion():
    with open("clave_transposicion.key", "r") as archivo_clave:
        clave = archivo_clave.read()
    return clave

def decrypt_transposicion(nom_archivo, clave):
    with open(nom_archivo, "r") as archivo:
        mensaje_encriptado = archivo.read()

    #diccionario de mapeo inverso para la permutación
    permutacion_inversa = {int(posicion): i + 1 for i, posicion in enumerate(clave.split())}
    #transposicion inversa
    mensaje_desencriptado = "".join([mensaje_encriptado[permutacion_inversa[i] - 1] for i in range(1, len(mensaje_encriptado) + 1)])

    with open(nom_archivo, "w") as archivo:
        archivo.write(mensaje_desencriptado)

def recibir_archivo_y_desencriptar(archivo_path, conn, addr, clave_transposicion):
    with open(archivo_path, 'wb') as file:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            file.write(data)
    
    #1) recibir archivo 2) desencriptar
    decrypt_transposicion(archivo_path, clave_transposicion)

    print(f"Archivo recibido y desencriptado correctamente desde {addr}")

def receive_file_size(sck: socket.socket):
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()
    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    filesize = struct.unpack(fmt, stream)[0]
    return filesize

def receive_file(sck: socket.socket, filename, clave_transposicion):
    filesize = receive_file_size(sck)
    with open(filename, "wb") as f:
        received_bytes = 0
        while received_bytes < filesize:
            chunk = sck.recv(1024)
            if chunk:
                f.write(chunk)
                received_bytes += len(chunk)

    print("Archivo recibido.")

    # verificar las dos condiciones
    if autenticacion_facial() and verificar_clave(clave_transposicion):
        decrypt_transposicion(filename, clave_transposicion)
        print("Mensaje desencriptado.")

def autenticacion_facial():
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('../Downloads/Video.mp4')
    dataPath = '../Documentos/Reconocimiento facial/Data'
    imagePaths = os.listdir(dataPath)

    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read('modeloLBPHFace.xml')

    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')

    authenticated = False

    start_time = time.time()#start tiempo

    while time.time() - start_time < 4:
        ret, frame = cap.read()
        if ret == False:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = gray.copy()

        faces = faceClassif.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            rostro = auxFrame[y:y+h, x:x+w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            result = face_recognizer.predict(rostro)

            if result[1] < 70:  #umbral valido
                cv2.putText(frame, '{}'.format(imagePaths[result[0]]), (x, y-25), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                authenticated = True
                break
            else:
                cv2.putText(frame, 'Desconocido', (x, y-20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                authenticated = False

        cv2.imshow('frame', frame)
        k = cv2.waitKey(1)
        if k == 27:
            break
        #solo si es la persona Correcta (sarah)
        if authenticated:
            if time.time() - start_time > 2:
                break

    cap.release()
    cv2.destroyAllWindows()

    return authenticated

def verificar_clave(clave_transposicion):
    clave = input("Ingrese la clave de desencriptación por transposición: ")
    #ambos deben saber la contraseña
    return clave == clave_transposicion

with socket.create_server(("0.0.0.0", 6190)) as server:
    print("Esperando al cliente...")
    conn, address = server.accept()
    print(f"{address[0]}:{address[1]} conectado.")
    print("Recibiendo archivo...")

    clave_transposicion = cargar_clave_transposicion()
    receive_file(conn, "archivoRecibido.txt", clave_transposicion)

print("Conexión cerrada.")
