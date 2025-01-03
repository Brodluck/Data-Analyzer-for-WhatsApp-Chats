# Data Analyzer for WhatsApp Chats

## Overview
This is a Python project for the computer science subject Python in the Enterprise. The main purpose of the project is to create a web application using the Streamlit framework, to analyze and synthesize data from exported WhatsApp chats. Additionally, it involves the use of a chatbot employing LLM for further analysis and engaging activities with the data.

## Features
- Chat data visualization and analysis
- Message search functionality
- Interactive AI chatbot using Groq API
- Support for both iPhone and Android WhatsApp chat formats
- Message statistics and user analytics
- Universal chat parser supporting both iOS and Android export formats

## Technology Stack

- **Programming Language:** Python
- **Framework:** Streamlit
- **AI Model:** Groq API (llama-3.3-70b-versatile)
- **Libraries:** Matplotlib, Pandas
- **Data Extraction:** Custom WhatsApp chat parser with cross-platform support

## Chat Parser
The application includes a robust chat parser that automatically detects and processes WhatsApp chat exports from both iOS and Android devices. This ensures compatibility regardless of the source device:
- **iOS Format:** Handles the specific timestamp and message format used in iPhone exports `[DD/MM/YY, HH:mm:ss]`
- **Android Format:** Processes Android's export format `DD/MM/YY, HH:mm -`
- **Multi-line Messages:** Properly handles messages that span multiple lines
- **Special Messages:** Filters system messages and media placeholders

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/brodluck/Data-Analyzer-for-WhatsApp-Chats.git
   ```

2. **Install Dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Setting up Groq API Token**
   ```bash
   nano ~/.bashrc
   ```
   Add the following line:
   ```bash
   export GROQ_API_KEY='your_api_key'
   ```
   Save and exit (Ctrl+X, then Y)
   
   Then reload your environment:
   ```bash
   source ~/.bashrc
   ```

4. **Run the Application:**
   ```bash
   streamlit run server.py 
   ```

## Contributors

- [Antonio Murillo Sevillano](https://github.com/murisevi)
- [Enmanuel De Abreu](https://github.com/brodluck)
- [Jorge Álvarez Fernández](https://github.com/joregete)
- [Julio Ribas de Novales](https://github.com/jRibasN)

## License

No license
