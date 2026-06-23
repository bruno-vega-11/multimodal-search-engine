import numpy as np
from VisualQuantizer import VisualQuantizer

def auditar_codebook_real(ruta_npy):
    print("=== 1. AUDITORÍA FÍSICA DEL ARCHIVO ===")
    
    codebook = np.load(ruta_npy)
    
    forma = codebook.shape
    print(f"Forma de la matriz: {forma}")
    if forma == (1000, 128):
        print("Correcto: Tienes 1000 centroides de 128 dimensiones (SIFT).")
    else:
        print("CUIDADO: La dimensionalidad no cuadra.")

    if np.isnan(codebook).any() or np.isinf(codebook).any():
        print("CUIDADO: El entrenamiento falló. Hay valores nulos o infinitos en la matriz.")
    else:
        print("Correcto: La matriz está matemáticamente limpia.")
        
    centroides_en_cero = np.all(codebook == 0, axis=1).sum()
    if centroides_en_cero > 0:
         print(f"ADVERTENCIA: Tienes {centroides_en_cero} centroides 'muertos' (todo ceros).")
    else:
         print("Correcto: Todos los clusters tienen información visual aprendida.")

def prueba_de_similitud_visual(ruta_npy, img_camisa1, img_camisa2, img_zapato):
    print("\n=== 2. AUDITORÍA LÓGICA ===")
    
    motor = VisualQuantizer(ruta_npy, k_clusters=1000)
    
    print("Cuantizando imágenes...")
    vec_camisa1 = np.array(motor.image_to_histogram(img_camisa1))
    vec_camisa2 = np.array(motor.image_to_histogram(img_camisa2))
    vec_zapato = np.array(motor.image_to_histogram(img_zapato))
    
    dist_camisas = np.linalg.norm(vec_camisa1 - vec_camisa2)
    dist_camisa_zapato = np.linalg.norm(vec_camisa1 - vec_zapato)
    dist_camisa_zapato2 = np.linalg.norm(vec_camisa2 - vec_zapato)

    
    print(f"\nDistancia [Camisa 1 <-> Camisa 2]: {dist_camisas:.2f}")
    print(f"Distancia [Camisa 1 <-> Zapato]  : {dist_camisa_zapato:.2f}")
    print(f"Distancia [Camisa 1 <-> Zapato]  : {dist_camisa_zapato2:.2f}")
    
    
if __name__ == "__main__":
    ARCHIVO_REAL = "codebook_kmeans.npy"
    
    auditar_codebook_real(ARCHIVO_REAL)
    
    ruta_a = "1163.jpg" #Polo
    ruta_b = "1164.jpg" #Polo
    ruta_c = "1550.jpg" #zapato
    
    prueba_de_similitud_visual(ARCHIVO_REAL, ruta_a, ruta_b, ruta_c)