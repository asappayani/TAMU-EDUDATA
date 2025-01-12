import pdfplumber 
import pandas as pd
from pprint import pp

with pdfplumber.open("grd20243EN.pdf") as pdf:
    p0 = pdf.pages[0]
    data = p0.extract_text(keep_blank_chars=True, layout=True)

    print(data)
    #df = pd.DataFrame(data[])

