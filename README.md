# Financial Data System

### Overview

A Django-based backend system that integrates with a public financial API to fetch, store, and analyze historical stock data. This project includes implementing a basic backtesting module for investment strategies, machine learning-based predictions, and report generation, all deployed on a cloud platform.

## Features

1. **Fetch Financial Data**
   - Integrates with the Alpha Vantage API to retrieve daily stock prices for a specific stock symbol (e.g., AAPL) over the past two years.
   - Data fetched includes: Open price, Close price, High price, Low price, and Volume.
   - Financial data is stored in a PostgreSQL database using Django ORM, optimized for querying.

2. **Backtesting Module**
   - Implements a simple backtesting strategy that simulates buying and selling based on stock price movement relative to moving averages (e.g., 50-day and 200-day averages).
   - Users can input parameters such as initial investment amount.
   - Generates performance metrics including total return, max drawdown, and number of trades.

3. **Machine Learning Integration**
   - Uses a pre-trained model (e.g., linear regression) to predict future stock prices based on historical data.
   - Predictions for the next 30 days are generated and stored alongside actual stock data for comparison.

4. **Report Generation**
   - Generates reports based on backtesting results or ML predictions.
   - Includes key financial metrics and visual comparisons between actual and predicted stock prices.
   - Reports are available in PDF format or as JSON responses through an API.

5. **Deployment**
   - Fully Dockerized setup for easy deployment.
   - Hosted on AWS, using AWS RDS (PostgreSQL) for database storage.
   - GitHub Actions are used to automate deployment with a CI/CD pipeline.

## Getting Started

### Prerequisites

- **Docker**: Ensure Docker and Docker Compose are installed.
- **API Key**: Obtain an Alpha Vantage API key from [Alpha Vantage](https://www.alphavantage.co/documentation/).
- **AWS Account**: Needed for cloud deployment.
- **Python Environment**: Python 3.12 or later.

### Local Setup

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/django-financial-backend.git
   cd django-financial-backend
   ```

2. **Create `.env` File**
   - Create a `.env` file in the root directory and add the following:
     ```env
     ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
     DATABASE_NAME=django_db
     DATABASE_USER=django_user
     DATABASE_PASSWORD=your_password
     DATABASE_HOST=db
     DATABASE_PORT=5432
     SECRET_KEY=your_secret_key
     DEBUG=True
     ALLOWED_HOSTS=*
     ```

3. **Build and Run Docker Containers**
   - Use Docker Compose to build and run the project:
     ```sh
     docker compose up -d --build
     ```

4. **Run Migrations**
   - Apply database migrations to set up the schema:
     ```sh
     docker compose exec web python manage.py migrate
     ```

5. **Seed Data (Fetch Financial Data)**
   - Fetch financial data to populate the database:
     ```sh
     curl http://127.0.0.1:8000/fetch/AAPL/
     ```

### Running Tests

- Run the unit tests to validate the backtesting and data fetching functionality:
  ```sh
  docker compose exec web python manage.py test
  ```

## Deployment

### AWS Deployment Steps

1. **Create AWS RDS Instance**
   - Set up a PostgreSQL instance on AWS RDS and note the connection details.

2. **Configure AWS CLI**
   - Install and configure the AWS CLI tool:
     ```sh
     aws configure
     ```

3. **Update Environment Variables**
   - Update your `.env` file with the RDS connection details.

4. **CI/CD Pipeline**
   - The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automates deployment:
     - Builds the Docker image.
     - Pushes the image to Docker Hub.
     - Deploys to AWS ECS.

## Endpoints

- **Fetch Financial Data**: `/fetch/<symbol>/`
  - Fetches and stores stock price data for the given symbol.
- **Backtesting**: `/backtest/<symbol>/<initial_investment>/`
  - Runs a backtesting strategy and returns performance results.
- **Predict Stock Prices**: `/predict/<symbol>/`
  - Predicts future stock prices using a pre-trained model.
- **Generate Report**: `/report/<symbol>/`
  - Generates a report in PDF format or as JSON.

## Key Technologies

- **Django**: Python web framework used for backend development.
- **PostgreSQL**: Database to store historical financial data.
- **Docker**: Containerization to ensure consistent deployments.
- **AWS**: Used for deployment (ECS for hosting, RDS for the database).
- **GitHub Actions**: Automates build, test, and deployment processes.

