import os
import kagglehub

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR,"imagen","data","raw")

path = kagglehub.dataset_download(
    "paramaggarwal/fashion-product-images-dataset",
    output_dir=OUTPUT_DIR,
    force_download=True
)

print("Dataset descargado en:", path)
