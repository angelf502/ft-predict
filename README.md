# FT-Predict

FT-Predict is a CLI-based tool designed to generate football match predictions for major European competitions.
By analyzing key metrics such as injury reports, head-to-head records, and historical performance the tool provides probabilistic outcomes for Home and Away wins to help inform your strategy.

## Features

*   **Multi-League Support:** Covers top-tier European football leagues.
*   **Data-Driven Analysis:** Considers injuries and historical context, not just standing tables.
*   **Redis Caching:** Optimized performance using Redis to handle data fetching.
*   **Customizable Logic:** Adjustable probability parameters to fine-tune prediction algorithms.

## Disclaimer
This tool is for educational and entertainment purposes only, sports outcomes are inherently unpredictable. I´m not responsible for any financial losses incurred from using these predictions for betting.

## Prerequisites

Before running the application, you need to set up the infrastructure.

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
1. Select a Competition: The CLI will present a menu of available leagues. Select the one you want to analyze.
![Menu Selection](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgwpru6jFDs-OBs1XQ23JmsHAM2YhgvY73Vjxpc1DnGsqajQFIPHDBs-x2m-MPjS7JOEYt2kUjey-gk5PFYZQ-396F00Wdvp1hGrDEquN_ta09m3USn-ETdCWUmc-khSOlYQs8eNPcnzSOREihv6medLMTmTkDmBINTGW2Gea7GichPMA3nRAcFTqLgEkbT/s192/menu.PNG)

2. Choose Teams: Once the data is fetched and cached, a list of upcoming matches or available teams will appear.
![Team List](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjV06RXMUkKlh_ZGf1II8W8bbbK1lYhJYtL4rQIIJMEFaXrxGcZO2wM_XNKMBmdTS1S-Pz8aSkNUYo0XizabVKtEf2YifjozCzMdq_h2n2QSYd6nmKzYKcRwszwK-symsvrGPT_u-Jcnuj9D9ZyxMBrV4tNQTScLWK2_98w6TrRd1ecpdZhZZWjpb-yBSyp/s378/list.PNG)

3. View Analysis: The tool outputs a detailed breakdown, including Home/Away win percentages and critical context like player injuries and H2H stats to ensure the prediction is as accurate as possible.
![Prediction Results](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiUTqRUtBttMMT4SAfpvP1Fsw5Z-Upqz1Z-VQKQSl2BC-vZbrLEQ3ceoyazJcuet-GUk0tPOjO6BUjDX7kcqF06fWQEDXoYUmZ5VGtG3ZUOa954OK_GMAVhNx0eOqef234gS-Fd8faBXjekPtt83hTlVDh271nsbl_Bgx3JCUgmWD9MjP2SsfHZH-WWARAp/s491/result.PNG)

### Customization
This project uses a heuristic probability model. By default, the logic may favor Home advantage based on historical statistical averages.
> [!IMPORTANT]
> You can adjust the weights and probability logic by modifying src/probability.py to better fit your own prediction models or updated statistical trends.