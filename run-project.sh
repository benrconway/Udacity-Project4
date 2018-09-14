pip install --user flask==0.9
rm itemcatalogue.db
rm models.pyc
python models.py
python seed_data.py
python views.py
