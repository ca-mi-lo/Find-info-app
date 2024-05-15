# Find Info App

**Find Info App** is an experimental application for finding and summarizing 
information from a document. Currently, it only supports files in PDF format.

Features:

- Uses natural language processing (NLP) to extract keywords and concepts.
- Generates concise and informative summaries of documents.
- Still under development, constantly improving its capabilities.

Potential Uses:

- Students: Quickly summarize research papers or textbooks.
- Everyone: Get a quick overview of a document without reading the whole thing.

Limitations:

- Only supports PDF files.
- Summarization accuracy varies depending on document complexity.

Future Plans:

- Add support for additional file formats.
- Improve the summarization algorithm for more accurate and informative summaries.

## Run the Application

### Generate Translation Messages Binary
To create the translation message binaries, execute the following command:

```
msgfmt -o locale/es/LC_MESSAGES/messages.mo locale/es/LC_MESSAGES/messages.po
```

### Install Application for Development

To install the application for development, first, ensure you have 
[Poetry](https://python-poetry.org/) installed. Then, clone the repository:

```
git clone 
```

Navigate to the cloned repository and run `poetry install`. Afterward, you 
can run the application:

```
poetry run GOOGLE_API_KEY=your_api_key streamlit run app.py
```

Before running the application, make sure to obtain a Google API key 
from [Google Developers Console](https://makersuite.google.com/app/apikey) 
and define it as an environmental variable (replace `your_api_key` with your 
actual API key). This key is required for certain features of the application 
to function properly.

## Development

### Update translation files

English is the default application language. Spanish is also available as an 
option for application messages.

Messages for Spanish, or potentially new languages, are generated using
[xgettext](https://www.gnu.org/software/gettext/) and its 
[Python API](https://docs.python.org/3/library/gettext.html). Therefore, UI 
translatable labels must be written as `_("Label text")`. 

To update the pot translation template, execute the following command:

```
xgettext --output=locale/messages.pot app.py
```

Later, merge the new messages template with the previously translated file using:

```
msgmerge locale/es/LC_MESSAGES/messages.po locale/messages.pot -o locale/es/LC_MESSAGES/messages.po
```
