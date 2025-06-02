from flask import Flask, json, jsonify
import mysql.connector
import base64
import os
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== DB FETCH LOGIC ==========
def fetch_cn_numbers_from_db():
    try:
        logger.info("Connecting to MySQL...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Raj6508$",
            database="my_database"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT cn_number FROM cn_numbers")
        cn_list = [row[0] for row in cursor.fetchall()]
        conn.close()
        logger.info("Fetched CN Numbers: %s", cn_list)
        return cn_list
    except Exception as e:
        logger.error("Database error: %s", str(e))
        return []

# ========== API 1: Just fetch and return CN Numbers ==========
@app.route("/update-cn", methods=["GET"])
def get_cn_numbers():
    cn_list = fetch_cn_numbers_from_db()
    return jsonify({
        "cn_numbers": cn_list,
        "count": len(cn_list)
    })




@app.route("/push_cn_to_azure", methods=["GET","POST"])
def push_cn_to_azure():
    cn_list = fetch_cn_numbers_from_db()
    if not cn_list:
        return jsonify({
            "status": 204,
            "message": "No CN numbers found in DB."
        })
    try:
        # Azure DevOps API setup
        pat = "6NCXxGTik8TfqIKyRPxNknb43CwIF4QzQhjYhv5DlDqhieEPJjdjJQQJ99BFACAAAAAAAAAAAAASAZDOK6f3"
        process_id = "7aa2bde1-c4dd-442a-9932-9f852f40cb54"
        wit_ref = "Demo_basic_process.Demo_work_item_type"
        field_ref = "Custom.cnumber"
        url = f"https://dev.azure.com/rajalluri/_apis/work/processes/{process_id}/workItemTypes/{wit_ref}/fields/{field_ref}?api-version=7.1-preview.2"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f':{pat}'.encode()).decode()}"
        }
        body = { "allowedValues": cn_list }
        logger.info("Sending PATCH to Azure DevOps...")
        response = requests.patch(url, headers=headers, json=body)
        logger.info("Azure DevOps Response Code: %s", response.status_code)
        logger.info("Azure DevOps Response Body: %s", response.text)
        return jsonify({
            "status": response.status_code,
            "message": "CN Number picklist updated successfully.",
            "response": response.text
        })
    except Exception as e:
        logger.error("Azure DevOps update failed: %s", str(e))
        return jsonify({
            "status": 500,
            "error": str(e)
        })


@app.route("/update-cname-text", methods=["GET", "POST"])
def update_cname_text_field():
    cn_list = fetch_cn_numbers_from_db()
    if not cn_list:
        return jsonify({
            "status": 204,
            "message": "No CN numbers found in DB."
        })

    first_value = cn_list[0]  # pick the first CN number

    try:
        # Azure DevOps API setup
        pat = "6NCXxGTik8TfqIKyRPxNknb43CwIF4QzQhjYhv5DlDqhieEPJjdjJQQJ99BFACAAAAAAAAAAAAASAZDOK6f3"
        process_id = "7aa2bde1-c4dd-442a-9932-9f852f40cb54"
        wit_ref = "Demo_basic_process.Demo_work_item_type"
        field_ref = "Custom.cname"  # Text field

        url = f"https://dev.azure.com/rajalluri/_apis/work/processes/{process_id}/workItemTypes/{wit_ref}/fields/{field_ref}?api-version=7.1-preview.2"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f':{pat}'.encode()).decode()}"
        }

        body = {
            "defaultValue": first_value  # This sets the default value for the field
        }

        logger.info("Sending PATCH to Azure DevOps to update Text field...")
        response = requests.patch(url, headers=headers, json=body)
        logger.info("Azure DevOps Response Code: %s", response.status_code)
        logger.info("Azure DevOps Response Body: %s", response.text)

        return jsonify({
            "status": response.status_code,
            "message": "CName text field updated successfully.",
            "default_value_set": first_value,
            "response": response.text
        })

    except Exception as e:
        logger.error("Azure DevOps update failed: %s", str(e))
        return jsonify({
            "status": 500,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True, port=5008)
