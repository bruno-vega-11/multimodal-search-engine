import kagglehub

path = kagglehub.dataset_download(
    "paramaggarwal/fashion-product-images-dataset",
    output_dir=r"E:\Dataset-Visual-E-commerce"
)

print("Dataset descargado en:", path)
