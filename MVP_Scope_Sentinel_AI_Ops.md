# Sentinel AI Ops MVP Scope

**Core Focus:** Predicting *high disk usage* on a simulated server and communicating this prediction as a **notification to a technician** (via AWS SNS email) and as a **suggestion from a simulated Copilot chatbot** (via Amazon Lex).

**Prototype MVP Features (What it WILL do):**
*   **Sample Data:** A `.csv` file mimicking server metrics (timestamp, server ID, disk usage %, hour, dayofweek).
*   **S3 Data Lake:** An Amazon S3 bucket (`sentinel-ops-data-lake-satya`) to store this sample data.
*   **Prediction Model (Lightweight):** A simple, pure-Python model implemented directly within AWS Lambda to classify disk usage as 'normal' or 'high' based on a threshold.
*   **Prediction Trigger & Notification Lambda:** An AWS Lambda function (`SentinelOpsPredictNotify`) that:
    *   Simulates receiving new disk usage data for a server.
    *   Performs the lightweight prediction.
    *   Sends an alert/notification via AWS SNS (`sentinel-ops-alerts-topic`) if high disk usage is predicted.
*   **Technician Prediction Output (Simulated Copilot):** Since Amazon Lex is not available in `us-east-2`, we will demonstrate the prediction output directly via Lambda's test results. In a full solution, this would integrate with an available chatbot service or a custom web chat UI.
*   **Command Center Mockup:** A static image or very basic HTML page displaying a few key metrics (e.g., count for "Predicted Issues").

**Prototype Out-of-Scope Features (What it WILL NOT do for MVP):**
*   Real-time data streaming or complex ingestion pipelines.
*   Fully automated remediation actions (e.g., automatically resizing disks, rebooting servers).
*   Full integration with actual RMM/PSA tools.
*   Complex, dynamic UI dashboards beyond a static mock.
*   Prediction of multiple issue types (focus only on high disk usage).
*   Advanced security threat prediction or detailed resource optimization.
*   Client-facing portal functionality.
*   Full Amazon Lex chatbot integration (due to regional unavailability in `us-east-2`).
*   Loading an `scikit-learn` model from S3 within Lambda (due to size limits).