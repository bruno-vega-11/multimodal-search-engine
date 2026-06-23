import subprocess
import sys
import os

def run_script(script_path, cwd=None):
    """Ejecuta un script de Python y verifica si terminó con éxito."""
    print(f"==================================================")
    print(f"Ejecutando: {script_path}...")
    print(f"==================================================")
    
    # Ejecuta el script capturando la salida en tiempo real
    result = subprocess.run([sys.executable, script_path], cwd=cwd)
    
    if result.returncode != 0:
        print(f"ERROR: El script {script_path} falló. Abortando pipeline.")
        sys.exit(1)
    print(f"¡Éxito al ejecutar {script_path}!\n")

def main():
    print("Pipeline automático\n")

    # -------------------------------------------------------------------------
    # PASO 1: Descargar los datasets (Scripts en la raíz)
    # -------------------------------------------------------------------------
    print("--- FASE 1: DESCARGA DE DATASETS ---")
    run_script("download_text_dataset.py")
    #run_script("download_images_dataset.py")
    # Si tienes un download_audio_dataset.py, lo agregas aquí
    
    # -------------------------------------------------------------------------
    # PASO 2: Procesamiento y construcción de índices por modalidad
    # Aquí asumimos nombres lógicos para los scripts internos de cada carpeta.
    # Usamos el parámetro 'cwd' para que Python sepa que debe pararse en esa carpeta.
    # -------------------------------------------------------------------------
    print("--- FASE 2: PROCESAMIENTO E INDEXACIÓN ---")
    
    # Subpipeline de Texto
    print("Procesando Texto...")
    run_script("src/main.py",cwd="texto")
    run_script("src/build_index.py",cwd="texto")
    run_script("src/build_dictionary.py",cwd="texto")
    run_script("src/build_norms.py",cwd="texto")
    #run_script("src/load_to_postgres.py",cwd="texto")

    # Subpipeline de Imagen
    print("Procesando Imágenes (SIFT)...")
    # run_script("src/extraer_sift.py", cwd="imagen")
    
    # Subpipeline de Audio
    print("Procesando Audios (MFCC)...")
    # run_script("src/extraer_mfcc.py", cwd="audio")

    # -------------------------------------------------------------------------
    # PASO 3: Inserción en la Base de Datos (Scripts en la raíz)
    # -------------------------------------------------------------------------
    print("--- FASE 3: INSERCIÓN EN POSTGRESQL ---")
    # Nota: Asegúrate de que Docker esté prendido antes de llegar aquí
    #run_script("insert_text_dataset.py")
    #run_script("insert_image_dataset.py")
    #run_script("insert_audio_dataset.py")

    print("¡PIPELINE TERMINADO CON ÉXITO! Base de datos lista para producción.")
    print("Ahora puedes ejecutar: uvicorn backend:app --reload")

if __name__ == "__main__":
    main()