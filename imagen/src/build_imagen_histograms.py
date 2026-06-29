import os
import glob
import json
from tqdm import tqdm
from VisualQuantizer import VisualQuantizer

def procesar_y_guardar(carpeta_imagenes, ruta_codebook, archivo_salida):
    print("1. Levantando el motor de cuantización...")
    # Usamos la ruta absoluta calculada dinámicamente para el codebook
    quantizer = VisualQuantizer(ruta_codebook, k_clusters=1000)
    
    # Construimos el patrón de búsqueda usando os.path.join
    patron_busqueda = os.path.join(carpeta_imagenes, "*.jpg")
    image_paths = glob.glob(patron_busqueda)
    print(f"\n2. Iniciando procesamiento de {len(image_paths)} imágenes...")
    
    procesados = 0
    errores = 0

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        for path in tqdm(image_paths, desc="Extrayendo vectores", unit="img"):
            try:
                nombre_archivo = os.path.basename(path)
                
                # Extracción matemática
                vector_histograma = quantizer.image_to_histogram(path)
                
                # Validar contrato dimensional
                if len(vector_histograma) != 1000:
                    errores += 1
                    continue
                    
                # Estructuramos el dato en un diccionario
                dato = {
                    "nombre_archivo": nombre_archivo,
                    "ruta_original": os.path.abspath(path),  # Guardamos la ruta absoluta real
                    "histograma": vector_histograma
                }
                
                # Convertimos a JSON y escribimos la línea
                f.write(json.dumps(dato) + "\n")
                procesados += 1
                
            except Exception as e:
                errores += 1
                continue
                
    print("\n=== RESUMEN DE EXTRACCIÓN ===")
    print(f"Vectores guardados exitosamente en '{archivo_salida}': {procesados}")
    print(f"Errores/Archivos corruptos: {errores}")

if __name__ == "__main__":
    # 1. Obtener el directorio donde se encuentra este script actual (raiz del script)
    IMAGEN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # -> imagen/
    
    # 2. Configurar rutas relativas usando os.path.join para evitar problemas entre Windows/Linux
    # Ejemplo: Si tu codebook está en una carpeta llamada 'modelos' al lado del script
    CARPETA_CODEBOOK = os.path.join(IMAGEN_DIR, "data", "codebook") 
    RUTA_CODEBOOK = os.path.join(CARPETA_CODEBOOK, "codebook_kmeans.npy")
    
    # Guardamos el .jsonl en la misma carpeta del script
    ARCHIVO_SALIDA = os.path.join(IMAGEN_DIR, "data","processed" "vectores_fashion.jsonl")
    
    # Mantenemos la ruta fija del dataset en tu sistema
    CARPETA_IMAGENES = os.path.join(IMAGEN_DIR,"data","raw","fashion-dataset","fashion-dataset","images")
    
    # Validamos que el codebook realmente exista antes de arrancar todo el proceso
    if not os.path.exists(RUTA_CODEBOOK):
        print(f"Error: No se encontró el codebook en la ruta: {RUTA_CODEBOOK}")
        print("Por favor, verifica la ubicación del archivo.")
    else:
        procesar_y_guardar(CARPETA_IMAGENES, RUTA_CODEBOOK, ARCHIVO_SALIDA)