# Flask Web Application

This is a simple Flask web application that serves an index page with HTML, CSS, and JavaScript.

## Project Structure

```
flask-web-app
├── app.py
├── templates
│   └── index.html
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository** (if applicable):
   ```
   git clone <repository-url>
   cd flask-web-app
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the Flask application, execute the following command:
```
python app.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## Usage

Once the application is running, navigate to the index page to see the content rendered from `index.html`. The page includes styles from `style.css` and interactivity from `main.js`.