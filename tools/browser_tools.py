import json
import requests
import streamlit as st
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html
from bs4 import BeautifulSoup

def _is_visible(element):
    """Helper function to check if an HTML element is visible."""
    from bs4.element import Comment
    if isinstance(element, Comment):
        return False
    parent = element.parent.name
    return parent not in ['style', 'script', 'head', 'title', 'meta', '[document]']
class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(website):
    """Useful to scrape and summarize a website content"""
    # url = f"https://chrome.browserless.io/content?token={st.secrets['BROWSERLESS_API_KEY']}"
    # payload = json.dumps({"url": website})
    # headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
    # response = requests.request("POST", url, headers=headers, data=payload)
    # elements = partition_html(text=response.text)
    # content = "\n\n".join([str(el) for el in elements])
    # content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
    # Fetch website content
    try:
        response = requests.get(website, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch website content: {e}"

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    text_elements = soup.find_all(text=True)
    visible_texts = filter(_is_visible, text_elements)
    content = "\n".join(t.strip() for t in visible_texts if t.strip())
    content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
    
    # max_chunk_length = 1024  # Token limit for the summarizer
    # chunks = [content[i:i + max_chunk_length] for i in range(0, len(content), max_chunk_length)]
    summaries = []
    for chunk in content:
      agent = Agent(
          role='Principal Researcher',
          goal=
          'Do amazing researches and summaries based on the content you are working with',
          backstory=
          "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
          allow_delegation=False)
      task = Task(
          agent=agent,
          description=
          f'Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
      )
      summary = task.execute()
      summaries.append(summary)
    return "\n\n".join(summaries)