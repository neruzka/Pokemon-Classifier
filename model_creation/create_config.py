import configparser
import os
import uuid


def get_possible_labels(dataset_path):
    dataset_paths = sorted(
        list([name for name in os.listdir(dataset_path) if not name.startswith(".")])
    )
    labels = "".join(dataset_paths)
    return labels


def create_config(
    dataset_path="./dataset/", model_path="./", lb_path="./", output_path="./"
):
    config = configparser.ConfigParser()

    config["Paths"] = {
        "dataset": dataset_path,
        "model": model_path,
        "labelbin": lb_path,
        "output": output_path,
    }
    config["Model"] = {
        "id": str(uuid.uuid4()),
        "model": "Smaller VGGNet",
        "classifying": "Pokemon",
        "possible_labels": get_possible_labels(config["Paths"]["dataset"]),
    }

    # Write the configuration to a file
    with open("config.ini", "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    create_config()
