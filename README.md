# ETL3 Streaming Pipeline

##  Overview
This project implements a **real-time ETL (Extract–Transform–Load) streaming pipeline** on **Google Cloud Platform (GCP)** using:

- generates random stock trade events by picking a stock ticker (AAPL, GOOGL, MSFT, AMZN) and assigning it a random price.
-- Each event looks like:

     {
  "symbol": "AAPL",
  "price": 1345.22,
  "timestamp": 1692623430.45
}
- **Cloud Run / Cloud Function** → Publishes stock price events into Pub/Sub  
- **Pub/Sub** → Message broker for streaming stock data  
- **Dataflow (Apache Beam)** → Processes stock data in real time and computes rolling averages  
- **BigQuery** → Stores aggregated results for analytics  
- **Airflow** → Orchestrates and validates the pipeline end-to-end  
- **Terraform** → Provisions infrastructure as code  

---

## Architecture

![ETL3 Streaming](https://github.com/user-attachments/assets/32408787-6c39-4cb0-ac43-4508f3d7a578)


## Repository Structure

<img width="747" height="330" alt="image" src="https://github.com/user-attachments/assets/7517987e-55a3-4ef9-8c8f-16569eb0ec48" />



## System Design

### 1. Prerequisites

Terraform
Google Cloud SDK
Apache Beam
Airflow

Enable GCP APIs:
Dataflow API
Pub/Sub API
BigQuery API
Cloud Run API

### 2. Provision Infrastructure with Terraform

cd Terraform/
terraform init
terraform apply


This sets up:

Pub/Sub topic (stock_prices)
BigQuery dataset & table (stock_data.stock_prices_agg)
Required service accounts & permissions

### 3. Deploy Stock Publisher (Cloud Run)

gcloud builds submit --tag gcr.io/$PROJECT_ID/stock-publisher ./CloudRun
gcloud run deploy stock-publisher \
  --image gcr.io/$PROJECT_ID/stock-publisher \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

### 4. Run Airflow DAG

Copy stock_streaming_pipeline.py to your Airflow dags/ folder.

The DAG performs:
Calls Cloud Run / Function to publish stock events.
Submits Dataflow job (dataflow_job.py).
Runs a BigQuery check to validate recent data.
Trigger DAG via Airflow UI or CLI:
airflow dags trigger stock_streaming_pipeline

### 5. Monitor

Dataflow job logs: GCP Dataflow Console

BigQuery results:
SELECT *
FROM `PROJECT_ID.stock_data.stock_prices_agg`
ORDER BY window_end DESC
LIMIT 10;

### Key Components

CloudRun/main.py
Publishes random stock prices into Pub/Sub:

record = {
    'symbol': random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN']),
    'price': round(random.uniform(100, 1500), 2),
    'timestamp': time.time()
}
publisher.publish(topic_path, json.dumps(record).encode('utf-8'))

========================================================================

dataflow_job.py
Beam pipeline:

Reads from Pub/Sub
Parses JSON → windows into 1-minute intervals
Aggregates average price per symbol
Writes results to BigQuery

=======================================================================

stock_streaming_pipeline.py
Airflow DAG flow:

Publish stock data → Cloud Function (HttpOperator)
Run Dataflow job → DataflowCreatePythonJobOperator
Check BigQuery → BigQueryCheckOperator

### Cleanup

Destroy resources:
cd Terraform/
terraform destroy

