import os
import kagglehub

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR,"text-dataset")

path = kagglehub.dataset_download(
    "notshrirang/spotify-million-song-dataset",
    output_dir=OUTPUT_DIR
)

print("Dataset descargado en :", path)