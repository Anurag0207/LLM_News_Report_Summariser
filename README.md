
---

# News Content Summarizer and Analyzer


This Streamlit web application serves as a content summarizer and analyzer, allowing users to input URLs of news articles, process them to extract information, and query the processed data to get answers.

## Features

- **Input URLs**: Users can input up to three URLs of news articles through the sidebar.
- **Process URLs**: Clicking on the "Process URLs" button fetches the content from the provided URLs and prepares it for analysis.
- **Question Answering**: Users can input a question related to the processed news data, and the application uses AI to generate an answer.
- **Display Answers and Sources**: The app displays the generated answer along with the sources used to generate the answer.
- **Summary Generation**: If available, the app also displays a summary of the processed news data.

## Technologies Used

- **Streamlit**: Front-end framework used for building and serving the web application.
- **Python Libraries**:
  - **LangChain**: Python library for natural language processing tasks such as text splitting, embeddings, and vector stores.
  - **OpenAI**: Integration for AI-based language models and question answering.
  - **FAISS**: Library for efficient similarity search and clustering of dense vectors.
  - **dotenv**: Library for loading environment variables from a `.env` file.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/news-content-summarizer.git
   cd news-content-summarizer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Your Environment**:
   - Create a `.env` file in the project root.
   - Add your OpenAI API key to the `.env` file:
     ```plaintext
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. **Run the Application**:
   ```bash
   streamlit run main.py
   ```

2. **Access the Application**:
   - Open your web browser and go to [http://localhost:8501](http://localhost:8501) to view and interact with the application.

3. **Using the Application**:
   - Input URLs of news articles into the sidebar and click "Process URLs" to fetch and analyze the content.
   - Enter a question related to the news data to get an AI-generated answer.
   - View the answer, sources, and summary (if available) displayed by the application.

## Project Structure

- **`main.py`**: Main Python script containing the Streamlit application code.
- **`requirements.txt`**: List of Python dependencies required for the application.
- **`faiss_store_openai.pkl`**: Pickle file storing the FAISS index for efficient data retrieval.
- **`.env`**: Configuration file for storing your OpenAI API key securely.

## Troubleshooting

- **Missing Dependencies**: If encountering errors related to missing dependencies, ensure all required libraries are installed using `pip install -r requirements.txt`.
- **Data Loading Issues**: If the application fails to load data from provided URLs, check network connectivity and URL validity.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please submit an issue or a pull request.

