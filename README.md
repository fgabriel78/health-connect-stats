# Health Connect Stats (via Fitbit)

A Python application that retrieves and calculates activity statistics (daily steps, weekly/monthly averages) from the Fitbit API (which acts as a gateway for Google Health Connect data).

## Features

- **Daily Stats**: Fetches step count for the current day.
- **Historical Analysis**: Calculates generic weekly and monthly averages based on the last 30 days of data.
- **Secure Authentication**: Uses OAuth 2.0 with PKCE (via standard Authorization Code flow) and token automatic refreshing.
- **Robust Configuration**: Uses `pydantic` for strict configuration validation.
- **Best Practices**: Implements connection pooling, type hinting, and structured logging.

## Prerequisites

- Python 3.8+
- A [Fitbit Developer Account](https://dev.fitbit.com/) to obtain API credentials.

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create a Fitbit App**:
    - Go to [Manage My Apps](https://dev.fitbit.com/apps/new) on the Fitbit Developer portal.
    - Register a new application.
    - **Redirect URL**: Set to `http://localhost:8080`.
    - **OAuth 2.0 Application Type**: Select "Personal".

2.  **Setup `config.json`**:
    - Copy the sample configuration file:
      ```bash
      cp config.sample.json config.json
      # OR on Windows
      copy config.sample.json config.json
      ```
    - Edit `config.json` and fill in your credentials:
      ```json
      {
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uri": "http://localhost:8080",
        "token_file": "token.json"
      }
      ```

## Usage

Run the application using Python:

```bash
python main.py
```

### First Run
On the first run, the application will open your default web browser to authorize access to your Fitbit data. Log in and grant the requested permissions. 
Once successful, the access token will be saved to `token.json` for future use.

## Testing

This project includes a suite of unit tests. To run them:

```bash
python -m unittest discover tests
```

## Project Structure

- `main.py`: Application entry point.
- `api_client.py`: Handles interactions with the Fitbit Web API.
- `auth.py`: Manages OAuth 2.0 authentication and token refreshing.
- `stats.py`: Contains logic for calculating activity statistics.
- `config.py`: Pydantic settings definition for configuration validation.
- `exceptions.py`: Custom exception classes.
- `tests/`: Directory containing unit tests.

## Troubleshooting

- **Token Expired**: The application automatically refreshes tokens. If you encounter persistent auth errors, delete `token.json` to trigger a fresh login flow.
- **Config Error**: Ensure `config.json` exists and contains valid JSON matching the structure in `config.sample.json`.
