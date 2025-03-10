import openai   #Used fo implementing AI
import requests  #Used for making HTTP request to download and open pages
from bs4 import BeautifulSoup  #Used for extracting data from web pages
import pdfplumber #Used to extract pdf file
import os  #Used for file and directory management
import re  #Used for regular expression for searching patterns in text
import time   #Used for API's limitation

openai.api_key = "OPENAI_API_KEY"
drive_folder_path = "drive folder path"

#Defining the urls
news_url = "https://www.aramco.com/en/news-media/news/2025/aramco-announces-full-year-2024-results"
pdf_url = "https://www.aramco.com/-/media/publications/corporate-reports/annual-reports/saudi-aramco-ara-2024-english.pdf"

#This is a function to analyze text using OpenAI GPT-3.5
def openai_analyze(text, retries=5, delay=5):
  for attempting in range(retries):
    try:
      response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[{"role": "system", "content": "You are an AI that summarizes key qualitative and quantitative insights."},
                    {"role": "user", "content": f"Analyze the following content and summarize key insights:\n\n{text}"}],
          temperature=0.7,
          max_tokens=200
      )
      return response["choices"][0]["message"]["content"].strip()
    except openai.error.RateLimitError:
      print(f"API rate limit exceeded. Retrying in {delay} seconds... (attempting {attempting+1}/{retries})")
      time.sleep(delay)
  return "Error: Rate limit exceeded after multiple retries."

#Function to scrape Aramco announcination and extract data
def scrape_aramco_news_with_regex(url):
  response = requests.get(url)
  content = response.text

#Function to extract the headline and date of the web page
  headline = re.findall(r'<h1.*?>(.*?)</h1>', content)
  date = re.findall(r'(\d{4}-\d{2}-\d{2})', content)

#Function to exctract the body content of the webpage
  soup = BeautifulSoup(content, 'html.parser')
  paragraphs = soup.find_all('p')
  body = ' '.join([p.get_text() for p in paragraphs if p.get_text().strip()])

#Function to extract revenue and percentage from the webpage
  revenue = re.findall(r'\$\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?(?:billion|million)?', content)
  percentages = re.findall(r'\d{1,3}(?:\.\d+)?%', content)

  headline = headline[0] if headline else "There is no headline"
  date = date[0] if date else "There is no date to be found"


  return {
      'headline': headline,
      'date': date,
      'content': body,
      'revenue': revenue,
      'percentages': percentages
      }


#This part is to extract text from the PDF report
def extract_aramco_pdf(url, drive_folder_path):
  response = requests.get(url)
  pdf_path = os.path.join(drive_folder_path, 'saudi-aramco-ara-2024-english.pdf')
  with open(pdf_path, "wb") as file:
    file.write(response.content)
  with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
  return text

#This function works to extract numerical quantitative data from the PDF file
def extract_quantitative_data_from_pdf(pdf_text):
  revenue = re.findall(r'\$\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?(?:billion|million)?', pdf_text)
  percentages = re.findall(r'\d{1,3}(?:\.\d+)?%', pdf_text)

  return {
      'revenue': revenue,
      'percentages': percentages
  }

#This function works to extract qualitative data from the PDF file
def extract_qualitative_insights_from_pdf(pdf_text):
  sustainability = re.findall(r'(sustainability|carbon capture|green energy|renewable|ESG|climate strategy).*?\.', pdf_text, re.IGNORECASE)
  strategy = re.findall(r'(strategic growth|market expansion|investment|long-term plan|diversification).*?\.', pdf_text, re.IGNORECASE)
  innovation = re.findall(r'(technology|innovation|research|development|AI|automation).*?\.', pdf_text, re.IGNORECASE)

  return {
      'sustainability': sustainability,
      'strategy': strategy,
      'innovation': innovation
  }

#This is where the result are shown in the output
news_data = scrape_aramco_news_with_regex(news_url)
print('\nNews data:')
print(f"Headline: {news_data['headline']}")
print(f"Date: {news_data['date']}")
print(f"Content: {news_data['content']}")
print(f"Revenue: {', '.join(news_data['revenue']) if news_data['revenue'] else 'no revenue found'}")
print(f"Percentages: {', '.join(news_data['percentages']) if news_data['percentages'] else 'No percentages found'}")
print()
print()
news_analysis = openai_analyze(news_data['content'])
print('News Analysis (OpenAI GPT-3.5):', news_analysis)
print()
print()
pdf_text = extract_aramco_pdf(pdf_url, drive_folder_path)
print('PDF Text Extracted (first 500 characters):', pdf_text[:500])
print()
print()
pdf_quant_data = extract_quantitative_data_from_pdf(pdf_text)
print("Quantitative Data from PDF:")
print(f"Revenue: {' '.join(pdf_quant_data['revenue']) if pdf_quant_data['revenue'] else 'No revenue data'}")
print(f"Percentages: {' '.join(pdf_quant_data['percentages']) if pdf_quant_data['percentages'] else 'No percentages data'}")
print()
print()
pdf_qualitative_data = extract_qualitative_insights_from_pdf(pdf_text)
print("\n Qualitative Insights from PDF")
print(f"Sustainability: {' '.join(pdf_qualitative_data['sustainability']) if pdf_qualitative_data['sustainability'] else 'No sustainability insights'}")
print(f"Strategy: {' '.join(pdf_qualitative_data['strategy']) if pdf_qualitative_data['strategy'] else 'No strategy insights'}")
print(f"Innovation: {' '.join(pdf_qualitative_data['innovation']) if pdf_qualitative_data['innovation'] else 'No innovation insights'}")
print()
print()
pdf_analysis = openai_analyze(pdf_text)
print('PDF Analysis (Qualitative, OpenAI GPT-3.5):', pdf_analysis)
