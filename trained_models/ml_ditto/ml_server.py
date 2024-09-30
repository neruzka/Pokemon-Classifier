# import the necessary packages
import configparser
import os
import pickle

import cv2
import flask
import jwt
import numpy as np
from keras.src.saving import load_model
from keras.src.utils import img_to_array

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
model_path = "./classifier_model.keras"
lb_path = "./lb.pickle"
model = None
lb = None


def jwt_valid(auth_header):
    if auth_header is not None:
        try:
            jwt_token = auth_header.split(" ")[1]
            jwt.decode(
                jwt_token,
                key=os.environ["JWT_SECRET"],
                algorithms=[
                    "HS256",
                ],
            )
            return True
        except jwt.InvalidSignatureError:
            pass
    return False


def preload_model():
    global model
    global lb

    model = load_model(model_path)
    lb = pickle.loads(open(lb_path, "rb").read())


def prepare_image(image, target):

    # resize the input image and preprocess it
    nparr = np.fromstring(image, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    image = cv2.resize(image, target)
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)

    # return the processed image
    return image


@app.route("/info", methods=["GET"])
def info():
    auth_token = flask.request.headers.get("Authorization")
    if auth_token is None or not jwt_valid(auth_token):
        return flask.Response("", status=403)
    data = {"success": False}

    config = configparser.ConfigParser()
    config.read("config.ini")

    data["model_info"] = dict(config["Model"])

    data["success"] = True

    return flask.jsonify(data)


@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}
    auth_token = flask.request.headers.get("Authorization")
    if not jwt_valid(auth_token):
        return flask.Response("", status=403)

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()

            # preprocess the image and prepare it for classification
            try:
                image = prepare_image(image, target=(96, 96))
            except:
                print("Bad image. Try another.")
                return flask.jsonify(data)
            # predict
            prob = model.predict(image)[0]

            idx = np.argmax(prob)
            label = lb.classes_[idx]
            confidence = prob[idx].item()

            data["key_prediction_label"] = label
            data["confidence"] = float(confidence * 100)
            data["all_predictions"] = []

            # loop over the results and add them to the list of
            # returned predictions
            for idx in range(len(prob)):
                temp_label = lb.classes_[idx]
                temp_conf = prob[idx].item()
                r = {"label": temp_label, "probability": float(temp_conf * 100)}
                data["all_predictions"].append(r)

            # indicate that the request was a success
            data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(data)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(
        (
            "* Loading Keras model and Flask starting server..."
            "please wait until server has fully started"
        )
    )
    preload_model()
    port = 8080
    app.run(port=port)
else:
    preload_model()
    gunicorn_app = app
