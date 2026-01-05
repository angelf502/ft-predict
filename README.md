# FT-Predict

FT-Predict is a CLI-based tool designed to generate football match predictions for major European competitions.
By analyzing key metrics—such as injury reports, head-to-head records, and historical performance—the tool provides probabilistic outcomes for Home and Away wins to help inform your strategy.

## Features

*   **Multi-League Support:** Covers top-tier European football leagues.
*   **Data-Driven Analysis:** Considers injuries and historical context, not just standing tables.
*   **Redis Caching:** optimized performance using Redis to handle data fetching.
*   **Customizable Logic:** Adjustable probability parameters to fine-tune prediction algorithms.

## Disclaimer
This tool is for educational and entertainment purposes only. Sports outcomes are inherently unpredictable. I´m not responsible for any financial losses incurred from using these predictions for betting.

## Prerequisites

Before running the application, you need to set up the infrastructure. This project relies on Redis for data persistence and caching.

### Docker Setup

1.  **Build the image:**
    ```bash
    docker build -t redis-ft-predict .
    ```

2.  **Run the container:**
    Ensure you define the path to your persistent volume.
    ```bash
    docker run -d -p 6379:6379 --name redis-container -v /path/to/persistent-volume:/data redis-ft-predict
    ```

### Configuration

Once the Redis container is running, verify that your application can connect to it. Open `tools/cache_redis.py` and configure the host IP address if your Docker container is not running on localhost or requires a specific bridge network IP.

## Installation

It is recommended to run this project within a virtual environment to manage dependencies cleanly.

1.  **Create the virtual environment:**
    ```bash
    python -m venv .venv
    ```

2.  **Activate the environment:**
    *   **Linux/macOS:**
        ```bash
        source .venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        .\.venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the predictor, run the main entry point:

```bash
python main.py
```
## Workflow
1. Select a Competition: The CLI will present a menu of available leagues. Select the one you wish to analyze.
![Menu Selection](https://drive.google.com/file/d/1fe1N1nXUOSZLLsny_cLCwf2Uz1farT3a/view?usp=drive_link)

2. Choose Teams: Once the data is fetched and cached, a list of upcoming matches or available teams will appear.
![Team List](https://drive.google.com/file/d/1bgudzdwYorKtVE19BS8z0kI9kg5hD9c-/view?usp=drive_link)

3. View Analysis: The tool outputs a detailed breakdown, including Home/Away win percentages and critical context like player injuries and H2H stats to ensure the prediction is as accurate as possible.
![Prediction Results](https://drive.google.com/file/d/18IfCL3mLgk39ofzHeFUtLsk3z30vqWpf/view?usp=sharing)

### Customization
Tuning the Algorithm This project uses a heuristic probability model. By default, the logic may favor Home advantage based on historical statistical averages.
> [!IMPORTANT]
> You can adjust the weights and probability logic by modifying src/probability.py to better fit your own prediction models or updated statistical trends.