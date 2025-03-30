import modules.rmp_scraperv2 as rmp_scraper
import pdfplumber 
import re
from pprint import pp
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["tamu_gpa"]
gpa_collection = db["gpa_distribution"]
ratings_collection = db["professor_ratings"]

