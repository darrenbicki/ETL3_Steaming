# 📊 ETL3 Streaming Pipeline

## 📌 Overview
This project implements a **real-time ETL (Extract–Transform–Load) streaming pipeline** on **Google Cloud Platform (GCP)** using:

- **Cloud Run / Cloud Function** → Publishes stock price events into Pub/Sub  
- **Pub/Sub** → Message broker for streaming stock data  
- **Dataflow (Apache Beam)** → Processes stock data in real time and computes rolling averages  
- **BigQuery** → Stores aggregated results for analytics  
- **Airflow** → Orchestrates and validates the pipeline end-to-end  
- **Terraform** → Provisions infrastructure as code  

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[Cloud Run / Function<br/>Stock Publisher] -->|Publishes JSON| B[Pub/Sub Topic]
    B --> C[Dataflow<br/>(Apache Beam Pipeline)]
    C -->|Aggregated stock prices| D[BigQuery Table<br/>stock_data.stock_prices_agg]
    D --> E[Airflow DAG<br/>Validation & Orchestration]
    E -->|Monitors freshness| D
# ETL3_Steaming
