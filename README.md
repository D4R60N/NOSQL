# NOSQL MongoDB

spouštění přes ./scripts/init.sh
import do MongoDB přes ./python/import.py
analýza dat přes ./python/analyze.py

data jsou ve složce ./import
dotazy jsou ve složce ./dotazy

možná bude nutné provést
find . -type f -print0 | xargs -0 dos2unix

potřebné python knihovny
pip install pymongo
pip install pandas
pip install matplotlib

