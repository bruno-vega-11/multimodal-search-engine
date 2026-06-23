import cv2
import numpy as np
import glob
import os
import torch
import kornia.feature as KF
from tqdm import tqdm

def extract_and_save_sift_gpu(
    image_folder: str,
    output_prefix: str,
    images_per_chunk: int = 3500,
    batch_size: int = 64,       
    img_size: tuple = (256, 256),
):
    device = torch.device("cuda")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    detector = KF.ScaleSpaceDetector(num_features=500).to(device)
    descriptor = KF.SIFTDescriptor(patch_size=41).to(device)

    image_paths = glob.glob(os.path.join(image_folder, "*.jpg"))
    print(f"Total imágenes: {len(image_paths)}")

    all_descriptors = []
    chunk_id = 1
    processed = 0

    def flush_chunk():
        nonlocal chunk_id, all_descriptors
        if all_descriptors:
            chunk_matrix = np.vstack(all_descriptors)
            np.save(f"{output_prefix}_parte{chunk_id}.npy", chunk_matrix)
            print(f"  → parte{chunk_id}  shape={chunk_matrix.shape}")
            all_descriptors = []
            chunk_id += 1

    for i in tqdm(range(0, len(image_paths), batch_size), unit="batch"):
        batch_paths = image_paths[i:i + batch_size]
        batch_imgs = []

        for path in batch_paths:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, img_size)
            tensor = torch.from_numpy(img).float() / 255.0
            batch_imgs.append(tensor)

        if not batch_imgs:
            continue

        batch_tensor = torch.stack(batch_imgs).unsqueeze(1).to(device)  

        with torch.no_grad():
            lafs, _ = detector(batch_tensor)
            patches = KF.extract_patches_from_pyramid(batch_tensor, lafs, 41)
            B, N, C, H, W = patches.shape
            descs = descriptor(patches.view(B * N, C, H, W)).view(B, N, -1)

        descs_np = descs.cpu().numpy()  
        del batch_tensor, lafs, patches, descs
        torch.cuda.empty_cache()

        for d in descs_np:
            all_descriptors.append(d)
            processed += 1
            if processed % images_per_chunk == 0:
                flush_chunk()

    flush_chunk()
    print(f"Listo. {chunk_id - 1} archivos .npy generados.")

if __name__ == "__main__":
    CARPETA_IMAGENES = "/workspace/images"
    extract_and_save_sift_gpu(CARPETA_IMAGENES, "sift_descriptors")