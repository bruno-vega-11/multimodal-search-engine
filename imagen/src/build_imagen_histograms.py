import os
import glob
import json
from tqdm import tqdm
from VisualQuantizer import VisualQuantizer

def procesar_y_guardar(carpeta_imagenes, ruta_codebook, archivo_salida):
    quantizer = VisualQuantizer(ruta_codebook, k_clusters=1000)
    
    patron_busqueda = os.path.join(carpeta_imagenes, "*.jpg")
    image_paths = glob.glob(patron_busqueda)
    
    procesados = 0
    errores = 0

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        for path in tqdm(image_paths, desc="Extrayendo vectores", unit="img"):
            try:
                nombre_archivo = os.path.basename(path)
                vector_histograma = quantizer.image_to_histogram(path)
                if len(vector_histograma) != 1000:
                    errores += 1
                    continue
                dato = {
                    "nombre_archivo": nombre_archivo,
                    "ruta_original": os.path.abspath(path),
                    "histograma": vector_histograma
                }
                
                f.write(json.dumps(dato) + "\n")
                procesados += 1
                
            except Exception as e:
                errores += 1
                continue
                
    print("\n=== RESUMEN DE EXTRACCIÓN ===")
    print(f"Vectores guardados exitosamente en '{archivo_salida}': {procesados}")
    print(f"Errores/Archivos corruptos: {errores}")

if __name__ == "__main__":
    IMAGEN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

    CARPETA_CODEBOOK = os.path.join(IMAGEN_DIR, "data", "codebook") 
    RUTA_CODEBOOK = os.path.join(CARPETA_CODEBOOK, "codebook_kmeans.npy")
    
    ARCHIVO_SALIDA = os.path.join(IMAGEN_DIR, "data","processed" "vectores_fashion.jsonl")
    
    CARPETA_IMAGENES = os.path.join(IMAGEN_DIR,"data","raw","fashion-dataset","fashion-dataset","images")
    
    if not os.path.exists(RUTA_CODEBOOK):
        print(f"Error: No se encontró el codebook en la ruta: {RUTA_CODEBOOK}")
        print("Por favor, verifica la ubicación del archivo.")
    else:
        procesar_y_guardar(CARPETA_IMAGENES, RUTA_CODEBOOK, ARCHIVO_SALIDA)
