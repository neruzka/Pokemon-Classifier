CREATE TABLE evaluation_predictions(
                        id SERIAL PRIMARY KEY,
                        model_id VARCHAR NOT NULL,
                        predicted_label VARCHAR NOT NULL,
                        prediction_certainty REAL NOT NULL,
                        real_lavel VARCHAR NOT NULL,
                        predicted_correctly INT NOT NULL,
                        input_dir VARCHAR NOT NULL
                        );