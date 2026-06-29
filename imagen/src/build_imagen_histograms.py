import os
import glob
import json
from tqdm import tqdm
from VisualQuantizer import VisualQuantizer  # Al estar en la misma carpeta src, se importa directo

def main():
    RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
    
    RUTA_RAIZ_IMAGEN = os.path.dirname(RUTA_SRC)
    
    CARPETA_IMAGENES = os.path.join(
        RUTA_RAIZ_IMAGEN, "data", "raw", "fashion-dataset", "fashion-dataset", "images"
    )
    
    RUTA_SALIDA_JSON = os.path.join(
        RUTA_RAIZ_IMAGEN, "data", "processed", "image_histograms.json"
    )
    
    RUTA_CODEBOOK = os.path.join(RUTA_RAIZ_IMAGEN, "data","codebook","codebook_kmeans.npy")
    
    os.makedirs(os.path.dirname(RUTA_SALIDA_JSON), exist_ok=True)

    print("\n[1/3] Levantando el motor de cuantización visual...")
        
    quantizer = VisualQuantizer(RUTA_CODEBOOK, k_clusters=1000)
    
    print("\n[2/3] Escaneando directorio de imágenes...")
    if not os.path.exists(CARPETA_IMAGENES):
        print(f"[ERROR] No se encontró la carpeta de imágenes en: {CARPETA_IMAGENES}")
        return

    image_paths = glob.glob(os.path.join(CARPETA_IMAGENES, "*.jpg"))
    total_imagenes = len(image_paths)
    print(f"      Se encontraron {total_imagenes} imágenes para procesar.")

    print("\n[3/3] Iniciando extracción SIFT y generación de histogramas...")
    histograms_dataset = {}
    errores = 0

    # Procesamiento pesado en disco
    for path in tqdm(image_paths, desc="Procesando imágenes", unit="img"):
        try:
            nombre_archivo = os.path.basename(path)
            # image_to_histogram devuelve una lista de 1000 números
            vector_histograma = quantizer.image_to_histogram(path)
            
            if len(vector_histograma) != 1000:
                errores += 1
                continue
            
            # Guardamos la ruta de forma relativa al proyecto para que no se rompa en otra PC
            ruta_relativa_img = os.path.relpath(path, RUTA_RAIZ_IMAGEN)
            
            histograms_dataset[nombre_archivo] = {
                "ruta_original": ruta_relativa_img,
                "histograma": list(vector_histograma)
            }
                
        except Exception:
            errores += 1
            continue

    print(f"\n Procesamiento finalizado. Exitosos: {len(histograms_dataset)} | Errores: {errores}")
    
    # Guardar el resultado en un JSON limpio
    print(f"Guardando histogramas en: {RUTA_SALIDA_JSON}...")
    with open(RUTA_SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(histograms_dataset, f, indent=2)
        
    print("[OK] Archivo de histogramas generado exitosamente.")

if __name__ == "__main__":
    main()