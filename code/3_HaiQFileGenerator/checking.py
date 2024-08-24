def contar_saltos_linea(archivo):
    with open(archivo, 'rb') as file:
        contenido = file.read()

    # Contar saltos de línea en formato Windows (\r\n)
    saltos_windows = contenido.count(b'\r\n')
    # Contar saltos de línea en formato Unix (\n) sin \r antes
    saltos_unix = contenido.count(b'\n') - saltos_windows

    return saltos_windows, saltos_unix

# Reemplaza 'tu_archivo.txt' con la ruta de tu archivo
archivo = 'tu_archivo.txt'
saltos_windows, saltos_unix = contar_saltos_linea(archivo)

print(f"Saltos de línea en formato Windows (\\r\\n): {saltos_windows}")
print(f"Saltos de línea en formato Unix (\\n): {saltos_unix}")

if saltos_windows > 0 and saltos_unix == 0:
    print("El archivo tiene saltos de línea en formato Windows.")
elif saltos_windows == 0 and saltos_unix > 0:
    print("El archivo tiene saltos de línea en formato Unix.")
elif saltos_windows > 0 and saltos_unix > 0:
    print("El archivo tiene una mezcla de saltos de línea en formato Windows y Unix.")
else:
    print("El archivo no tiene saltos de línea.")
