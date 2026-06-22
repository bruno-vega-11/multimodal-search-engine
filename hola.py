import kagglehub

path = kagglehub.dataset_download(
    "paramaggarwal/fashion-product-images-dataset"
)

print(path)