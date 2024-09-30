# import the necessary packages
import os
import sys

import jwt
import psycopg2
import requests
from imutils import paths

API_PREDICT_PATH = "/predict"
API_INFO_PATH = "/info"

DATASET_PATH = "./dataset/"

DB_TABLE_NAME = "evaluation_predictions"


def main():
    ml_models_apis = sys.argv[1:]

    # DATABASE CONNECTION
    # ------------------
    connection = psycopg2.connect(
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT")),
    )
    cursor = connection.cursor()
    jwt_token = jwt.encode(payload={}, key=os.environ["JWT_SECRET"])
    headers = {"Authorization": f"Bearer {jwt_token}"}
    jwt.decode(
        jwt_token,
        key=os.environ["JWT_SECRET"],
        algorithms=[
            "HS256",
        ],
    )
    # ------------------
    insert_row_data = []

    for api in ml_models_apis:
        try:
            response = requests.get(api + API_INFO_PATH, headers=headers).json()
        except requests.HTTPError:
            print(f"Can't communicate with {api}. Skipping.")
            continue
        model_info = response["model_info"]

        print(model_info["id"])

        cursor.execute(
            "SELECT 1 FROM evaluation_predictions WHERE model_id = %s;",
            (model_info["id"],),
        )
        if cursor.rowcount:
            print(
                f"Model {model_info['id']} is already tested. See table {DB_TABLE_NAME} for results."
            )
        else:
            print(f"Testing {model_info['id']}. Please wait...")

            model_labels = model_info["possible_labels"].split(",")

            for label in model_labels:
                label_path = DATASET_PATH + label
                if os.path.isdir(label_path):
                    image_paths = list(paths.list_images(label_path))

                    for image_path in image_paths:
                        with open(image_path, "rb") as image:
                            payload = {"image": image}
                            r = requests.post(
                                api + API_PREDICT_PATH, files=payload, headers=headers
                            ).json()

                        if r["success"]:
                            prediction = r["key_prediction_label"]
                            confidence = round(r["confidence"], 2)
                            correct = int(label == prediction)

                            prediction_info = (
                                model_info["id"],
                                prediction,
                                confidence,
                                label,
                                correct,
                                image_path,
                            )
                            insert_row_data.append(prediction_info)
                        else:
                            print("Request failed")
                else:
                    print(f"We don't seem to have any validation data for {label}!")

                print(f"Finished adding valuation for {label}")

        print(f"Finished adding valuation for {model_info['id']}")

    print("Finished evaluation all models. Dumping all data.")
    insert_query = """INSERT INTO evaluation_predictions(id,
                                                model_id,
                                                predicted_label,
                                                prediction_certainty,
                                                real_lavel,
                                                predicted_correctly,
                                                input_dir) 
                                                VALUES(DEFAULT, %s,%s,%s,%s,%s,%s);"""
    cursor.executemany(insert_query, insert_row_data)
    print("Closing all connections.")

    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
