# Dashboard UI

This project is a minimalist dashboard UI designed to display the initial response, rewritten response (if any), input question, sentiment, and the success status of the self-check from a chatbot application.

## Project Structure

```
dashboard-ui
├── src
│   ├── App.jsx
│   ├── components
│   │   ├── Dashboard.jsx
│   │   └── ResponseCard.jsx
│   ├── styles
│   │   └── main.css
│   └── index.js
├── public
│   └── index.html
├── package.json
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd dashboard-ui
   ```
3. Install the dependencies:
   ```
   npm install
   ```

## Usage

To start the development server, run:
```
npm start
```

This will launch the application in your default web browser.

## Features

- Displays the initial response from the chatbot.
- Shows the rewritten response if the initial response fails the self-check.
- Presents the user's input question.
- Analyzes and displays the sentiment of the user's question.
- Indicates the success status of the self-check process.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.