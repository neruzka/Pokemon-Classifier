# Pokemon Classifier Tester
## The problem
As part of the technical task, I wanted to explore a setting in which we validate live ML models with specific data. While the model provided does not retrain automatically, we often update our models with new data and might not think about a change in their performance clasifying previously easy to identify categories. For this purpose I built a prediction collection layer. This allows us to test different live models with specific data and evaluate their performance by storing the predictions in a database.

## Project structure
The project is split into four main parts.
* model_creation - this holds all the necessary parts to train a new model. The structure of this section remains mostly true to kjaisingh's implementation found in this [github repo](https://github.com/kjaisingh/Pokemon-Classifier). The main changes include:
    * Library updates - Since the original project is now 6 years old, I needed to update a lot of keras imports. 
    * create_config.py - I added a create_config function (found in create_config.py) which I call at the end of train.py allowing ease later in the server setup for each different ML model
* trained_models - this holds all the trained models that are ready to classify different pokemon. Each model (ml_original, ml_ditto, ml_ditto_and_mimikyu) was trained on a different set of pokemon. Each folder is a containerised model. Within each folder is also the ml_server.py file, which works as a flask server that responds to the appropriate requests. 
* db_scripts - this folder simple scripts that aid in postgres table operations that need to be run from the cmd
* data_collector - this is the layer that given a ML server, checks if we have already tested, and if not - asks it to classify preset data (adjusted to it's categories).


## How to run it
In order to run this project on your machine, please run these commands:
```
docker compose up -d
setup_db.sh
```
This sets up the models and initializes the database for the first time.

In order to run the data_collector and evaluate the modesl run:
```
docker compose exec data_collector python data_collector.py http://ml_original:8080 http://ml_ditto:8080 http://ml_ditto_and_mimikyu:8080
```

You can then access and connect to the db with 
```
./connect_to_db.sh
```
Or with any db tool of your choice with the credentials from the scripts.

The data collector will not run for models it has already evaluated so if you wish to clear the DB to run again use
```
./destroy_db.sh
```
## Future improvements
The hope would be to get this set up in k8s and host it on gcp. Automate the deploy of new models with a deploy hook of some kind. I would have loved to also automatically check for new information on the db to run an analytics script comparing the different models. Distribute credentials with a proper secret manager.
