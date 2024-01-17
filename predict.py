import os
from ultralytics import YOLO
import shutil

def run_inference(source_path, result_folder):
    result_image_names = []

    # Laad het YOLO-model
    model = YOLO('Coral3.pt')

    # Voer de voorspelling uit op de invoerbron
    results = model.predict(source_path, show_conf=True, save=True, show_labels=True, save_dir=os.path.join(os.path.abspath(result_folder)))
    

    result_subfolder = 'runs/detect'
    result_folders = [f for f in os.listdir(result_subfolder) if f.startswith("predict")]

    if result_folders:
        for result_folder_name in result_folders:
            result_image_name = os.path.basename(source_path)
            result_image_path_source = os.path.join(result_subfolder, result_folder_name, result_image_name)
            result_image_path_destination = os.path.join(result_folder, result_folder_name)

            if os.path.exists(result_image_path_source):
                # Gebruik de oorspronkelijke bestandsnaam in plaats van de naam van de predict-map
                result_image_name_dest = os.path.join(result_folder, result_image_name)
                shutil.move(result_image_path_source, result_image_name_dest)
                result_image_names.append(result_image_name)

    return result_image_names
