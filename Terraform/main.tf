provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_pubsub_topic" "stock_topic" {
  name = "stock_prices"
}

resource "google_bigquery_dataset" "stock_dataset" {
  dataset_id = "stock_data"
  location   = var.location
  project    = var.project_id
}

resource "google_bigquery_table" "agg_table" {
  dataset_id = google_bigquery_dataset.stock_dataset.dataset_id
  table_id   = "stock_prices_agg"
  project    = var.project_id

  schema = jsonencode([
    {
      name = "symbol"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "window_start"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "window_end"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "avg_price"
      type = "FLOAT"
      mode = "REQUIRED"
    }
  ])
}

resource "google_storage_bucket" "dataflow_bucket" {
  name          = "bkt-stock"  # <<< CHANGE if needed
  location      = var.region
  force_destroy = true
}
