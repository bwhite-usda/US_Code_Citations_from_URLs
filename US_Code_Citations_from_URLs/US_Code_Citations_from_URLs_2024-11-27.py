import requests
import random
import PyPDF2
import re
import pandas as pd
import time
import logging
from fake_useragent import UserAgent
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import Timeout, ConnectionError

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to download PDF with retries, dynamic headers, and better error handling
def download_pdf(url, filename):
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Use a random User-Agent to simulate human browsing
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Referer': 'https://www.fsis.usda.gov/'
    }
    session.headers.update(headers)

    try:
        logging.info(f"Attempting to download: {url}")
        response = session.get(url, timeout=120)  # Increased timeout to 120 seconds
        response.raise_for_status()  # Raise an error for bad status codes
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        logging.info(f"Successfully downloaded: {url}")
    except (Timeout, ConnectionError) as e:
        logging.error(f"Error downloading {url}: {e}")
        time.sleep(10)  # Wait for 10 seconds before retrying
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False
    return True

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        logging.info(f"Text extracted from {pdf_path}")
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
    return text

# Function to find U.S. Code citations in text
def find_us_code_citations(text):
    pattern = (
        r'\b(?:\d{1,2}\sU\.S\.C\.|\d{1,2}\sUSC|\d{1,2}\sU\.S\.\sCode|\d{1,2}\sU\.S\.\sC\.|\d{1,2}\sUS\sCode|chapter\s\d+\sof\stitle\s\d+,\sUnited\sStates\sCode|\d+\w+\sof\stitle\s\d+,\sUnited\sStates\sCode)\s?'
        r'[\d\w\-\–]*\b'
    )
    citations = re.findall(pattern, text)
    logging.info(f"Found {len(citations)} U.S. Code citations")
    return citations

# URLs of the PDFs
urls = [
    "https://www.usda.gov/sites/default/files/documents/usda-dept-quick-start-guide-20180412.pdf",
    "https://www.usda.gov/sites/default/files/documents/usda-departmental-directives-checklist.pdf",
    "https://www.usda.gov/sites/default/files/documents/RD_WebsiteContentInventory2005_v02.pdf",
    "https://www.usda.gov/sites/default/files/documents/ppd.pdf",
    "https://www.usda.gov/sites/default/files/documents/GIPSA_WebsiteContentInventory2004_v01.pdf",
    "https://www.usda.gov/sites/default/files/documents/directives-by-number-current-opi.pdf",
    "https://www.rd.usda.gov/files/ilin1780guide11C.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/FSISDirective4630.2Rev3Leave.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/FSIS-Directive-4335.8.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/FSIS_Directive_3410.3_Reimbursement_Allowance_Table.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/7150.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/67-23.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/6100.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/5000.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/4610.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/4451.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/29-20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/13000.7.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/13000.6.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/1040.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/documents/10240.6.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-07/10800.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-05/12600.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-03/4300.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-03/13000.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-03/10800.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-03/10800.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-03/10240.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2022-02/10800.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-12/9910.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-11/34_IM_Non-Food-Safety-Consumer-Protection-Tasks-10222021.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/Tracked-changes-5000.1-Rev.6_0.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/9900.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/7520.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/6030.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/5030.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/5000.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/5000.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-10/3900.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-09/8010.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-09/7120.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-08/5100.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-08/4810.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-06/FSIS_Directive-7221.1-Rev_2_Prior_Labeling_Approval_0.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-06/6100.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-06/5620.1_0.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-06/23-21.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-05/8080.3_1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-05/5740.1_0.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-04/10800.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-03/7320.1_0.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-03/6900.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-03/4610.6.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-03/2680.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-03/10250.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/FSIS%20Directive%203800.2%20POV%20Reimbursement%20%28Reimbursement%20for%20Use%20of%20Privately%20Owned%20Vehicles%29.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/FSIS%20Directive%203800.1%20Temporary%20Duty%20Travel%20within%20Conus.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/9900.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/9900.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/9900.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/9510.1-tracked.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/9500.8.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/7235.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/5030.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/4630.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/10250.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2021-02/10230.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/PHVt-Processing_7000_Directive.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4792.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4791.6%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4791.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4791.13.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4791.12.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4791.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4771.1%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4735.9%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4735.7.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4735.4%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4735.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4630.7%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4630.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4610.9.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4610.5%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4610.1%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4551.1%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4550.7%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/4550.4%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/14000.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/12700.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/12600.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/12600.1.Amendment%202.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/10300.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/10240.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/10240.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/10100.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/10010.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-08/10010.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9900.6.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9900.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9500.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9040.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9030.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9010.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9000.8.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9000.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/9000.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/8410.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/8080.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/8010.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/8010.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7700.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7530.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7530.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7355.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7320.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7310.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7230.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7160.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7150.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7111.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7010.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7000.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/7000.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6900.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6810.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6700.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6600.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6500.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6420.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6420.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6410.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6410.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6400.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6300.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6240.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6210.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6120.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6100.6.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6100.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6100.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6090.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/6020.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5930.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5730.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5710.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5600.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5500.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5420.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5220.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5220.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5110.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5100.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5100.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5020.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5010.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.8.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.7.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.6.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/5000.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4530.3%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4451.3%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4430.5.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4430.3%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4410.1%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4339.3%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4338.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4335.8%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4335.1%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4315.3%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4315.2%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4306.2%20.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4300.10.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/4200.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3830.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3820.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3810.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3730.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3700.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3530.4.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/3410.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/2450.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/2410.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1520.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1310.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1306.7.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1306.22.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1306.18.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/13000.3.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/13000.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/13000.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1240.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1230.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1210.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1090.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1060.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/1010.2.pdf",
    "https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/10010.1.pdf",
    "https://www.fsis.usda.gov/sites/default/files/import/QA_6100.4.pdf",
    "https://www.fsis.usda.gov/shared/training/5500.2.pdf",
    "https://www.fs.usda.gov/t-d/pubs/ppt_html/htm05672C04/document/cpl2-103.pdf",
    "https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5394817.pdf",
    "https://www.aphis.usda.gov/sites/default/files/mrp-5400-2.pdf",
    "https://www.aphis.usda.gov/sites/default/files/mrp-5101-1.pdf",
    "https://www.aphis.usda.gov/sites/default/files/mrp-4550-2.pdf",
    "https://www.aphis.usda.gov/sites/default/files/mrp-4413-1.pdf",
    "https://www.aphis.usda.gov/sites/default/files/mrp-3020-1.pdf",
    "https://www.aphis.usda.gov/sites/default/files/hspd-9.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-402-3.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-3575-1.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-3440-2.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-3330-1.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-3140-2.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-2150-1.pdf",
    "https://www.aphis.usda.gov/sites/default/files/aphis-1040-3.pdf",
    "https://www.aphis.usda.gov/sites/default/files/4.115.pdf",
    "https://www.aphis.usda.gov/sites/default/files/4.101.pdf",
    "https://www.aphis.usda.gov/sites/default/files/3.115.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.627.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.510.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.450.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.430.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.401.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.215.pdf",
    "https://www.aphis.usda.gov/sites/default/files/2.101.pdf",
    "https://www.aphis.usda.gov/sites/default/files/1.210.pdf",
    "https://www.aphis.usda.gov/sites/default/files/1.205.pdf",
    "https://www.aphis.usda.gov/library/directives/pdf/APHIS_6901_1.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/MRP4531_1.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/Financial%20Guidelines%20For%20Cooperative%20Grading%20Programs.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGISDirective9180_74.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9290_18.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_78.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_72.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_67.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_65.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_61.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_53.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_49.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_47.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_40.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_38.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_35.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9180_17.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9170_13.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9160_5.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9160_3.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9100_7.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9070_6.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9070_5.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS9060_2.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/FGIS4735_2.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/AMS%20Records%20Management%20Program.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/AMS%20Directive%203130.9.pdf",
    "https://www.ams.usda.gov/sites/default/files/media/22203AMSDebtManagementDirective.pdf",
    "https://directives.nrcs.usda.gov/sites/default/files2/1715860582/Part%20503%20Subpart%20A%20-%20General.pdf",
]

# Process each URL
results = []
for url in urls:
    # Extract the filename from the URL
    filename = url.split("/")[-1]
    
    # Download the PDF
    if download_pdf(url, filename):
        # Extract text from the PDF
        text = extract_text_from_pdf(filename)
        
        # Find U.S. Code citations
        citations = find_us_code_citations(text)
        
        # Store results
        results.append({"filename": filename, "citations": citations})
    
    # Random delay between requests to mimic human behavior
    time.sleep(random.uniform(2, 5))

# Save results to a CSV file
df = pd.DataFrame(results)
df.to_csv("us_code_citations.csv", index=False)
logging.info("Results saved to us_code_citations.csv")
