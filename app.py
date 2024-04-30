import requests
from bs4 import BeautifulSoup
import json
from groq import Groq
import streamlit as st

# Constants
LLAMA_MODEL = "llama3-70b-8192"
BASE_URL = "https://www.sikhnet.com/hukam/personal/"

# System message setup
SYSTEM_MESSAGE = {
    "role": "system",
    "content": ("You are an expert and wise bot who is great in understanding and explaining gurbani "
                "hukamnamas in detail. You will be given Hukamnama. You have to explain the hukamnama by "
                "very closely related to their query, explain from the guru's perspective and provide guidance to the user.")
}

client = None

def get_chat_response(english_text, user_prompt):
    if not client:
        return "Please enter a valid API key int the sidebar on the left to continue."
    messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": english_text},
        {"role": "user", "content": user_prompt}
    ]
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=LLAMA_MODEL,
        temperature=0.5,
        max_tokens=1024,
        top_p=1
    )
    return chat_completion.choices[0].message.content

def scrape_hukamnama(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup.find_all('script'):
                if 'jQuery.extend(Drupal.settings' in script.text:
                    data_str = script.text[script.text.find('{'):script.text.rfind('}') + 1]
                    data_json = json.loads(data_str)
                    return {
                        'gurmukhi': data_json['hukam']['shabad_lines']['gurmukhi'],
                        'english': data_json['hukam']['shabad_lines']['english']
                    }
            return "Data not found."
        return f"Failed to retrieve data. Status code: {response.status_code}"
    except Exception as e:
        return str(e)

def format_english_translation(english_lines):
    return '\n'.join(f'• {line}' for line in english_lines)

def main():
    global client  

    st.title("Hukamnama Interpreter")
    # Display the sidebar with instructions and the option to enter API key
    with st.sidebar:
        st.title('Hukamnama Interpreter')
        st.markdown('''
    📜 **Welcome to the Hukamnama Interpreter!** 🕊️

    - This application provides explanations of Hukamnamas tailored to personal queries.
    - Designed to help users gain deeper insights into Sikh teachings and apply them in their daily lives.
    - We understand the importance of Hukamnamas in Sikhism and aim to provide personalized interpretations but the explanation might not be fully accurate as gurbani is very deep and complex.
    
    This application accepts Hukamnama URLs from [SikhNet](https://www.sikhnet.com) and provides personalized interpretations based on user prompts.
    
    Visit [SikhNet - Take a Personal Hukam](https://www.sikhnet.com/hukam/personal?gad_source=1&gclid=CjwKCAjwrcKxBhBMEiwAIVF8rNRrcM0Up7TdXJfZ43usPpdl0NPDbT-QIC3YGCI0ALk81S-cbdER5BoCAAsQAvD_BwE) to get your Hukamnama URL.

    Made with ❤️ by [Gursahib Singh](https://www.linkedin.com/in/gursahibsingh07/)
    ''')
        
        # Enter API key here
        api_key = st.text_input('Enter your API key:', type='password')
        if api_key.startswith('gsk_'):  # Example prefix, adjust based on your API key structure
            client = Groq(api_key=api_key)
            st.success('API Key accepted. You can now use the application.', icon='👉')
        else:
            st.warning('Please enter a valid API key to continue. \nGrab you key from [groq](https://console.groq.com/keys)', icon='⚠️')

    url_input = st.text_input("Enter the Hukamnama URL:", "")
    user_prompt = st.text_area("Describe your reason for seeking the Hukamnama:", "")

    if url_input:
        if BASE_URL in url_input:
            st.success("Valid URL provided.")
            if st.button("Interpret Hukamnama"):
                data = scrape_hukamnama(url_input)
                if isinstance(data, dict):
                    english_formatted = format_english_translation(data['english'])
                    response = get_chat_response(english_formatted, user_prompt)
                    st.markdown("### Formatted English Translation:")
                    st.markdown(english_formatted)
                    st.markdown("### Personal Interpretation for You:")
                    st.markdown(response)
                else:
                    st.error(data)
        else:
            st.error("Please grab the hukamnama from the correct page and then paste it here to understand.")

if __name__ == "__main__":
    # App title
    st.set_page_config(page_title="Hukamnama Interpreter", page_icon="📜")

    main()
