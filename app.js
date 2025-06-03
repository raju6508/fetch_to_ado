const express = require("express");
const mysql = require("mysql");
const axios = require("axios");
const bodyParser = require("body-parser");

const app = express();
const port = 5008;

app.use(bodyParser.json());

// ========== Logging ==========
const log = (message, ...args) => console.log(`[INFO] ${message}`, ...args);

// ========== DB FETCH LOGIC ==========
function fetchCnNumbersFromDb() {
  return new Promise((resolve, reject) => {
    log("Connecting to MySQL...");
    const connection = mysql.createConnection({
      host: "localhost",
      user: "root",
      password: "Raj6508$",
      database: "my_database",
    });

    connection.connect((err) => {
      if (err) {
        console.error("DB connection failed:", err);
        return reject(err);
      }

      connection.query("SELECT cn_number FROM cn_numbers", (error, results) => {
        connection.end();
        if (error) {
          console.error("Query error:", error);
          return reject(error);
        }
        const cnList = results.map((row) => row.cn_number);
        log("Fetched CN Numbers:", cnList);
        resolve(cnList);
      });
    });
  });
}

// ========== API 1: Just fetch and return CN Numbers ==========
app.get("/update-cn", async (req, res) => {
  try {
    const cnList = await fetchCnNumbersFromDb();
    res.json({ cn_numbers: cnList, count: cnList.length });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ========== API 2: Push CN Numbers to Azure ==========
app.all("/push_cn_to_azure", async (req, res) => {
  try {
    const cnList = await fetchCnNumbersFromDb();
    if (!cnList.length) {
      return res
        .status(204)
        .json({ status: 204, message: "No CN numbers found in DB." });
    }

    const pat =
      "6NCXxGTik8TfqIKyRPxNknb43CwIF4QzQhjYhv5DlDqhieEPJjdjJQQJ99BFACAAAAAAAAAAAAASAZDOK6f3";
    const processId = "7aa2bde1-c4dd-442a-9932-9f852f40cb54";
    const witRef = "Demo_basic_process.Demo_work_item_type";
    const fieldRef = "Custom.cnumber";

    const url = `https://dev.azure.com/rajalluri/_apis/work/processes/${processId}/workItemTypes/${witRef}/fields/${fieldRef}?api-version=7.1-preview.2`;

    const headers = {
      "Content-Type": "application/json",
      Authorization: "Basic " + Buffer.from(`:${pat}`).toString("base64"),
    };

    const response = await axios.patch(
      url,
      { allowedValues: cnList },
      { headers }
    );

    log("Azure DevOps Response Code:", response.status);
    log("Azure DevOps Response Body:", response.data);

    res.json({
      status: response.status,
      message: "CN Number picklist updated successfully.",
      response: response.data,
    });
  } catch (error) {
    console.error("Azure DevOps update failed:", error);
    res.status(500).json({ status: 500, error: error.message });
  }
});

// ========== API 3: Update CName Text Field ==========
app.all("/update-cname-text", async (req, res) => {
  try {
    const cnList = await fetchCnNumbersFromDb();
    if (!cnList.length) {
      return res
        .status(204)
        .json({ status: 204, message: "No CN numbers found in DB." });
    }

    const firstValue = cnList[0];

    const pat =
      "6NCXxGTik8TfqIKyRPxNknb43CwIF4QzQhjYhv5DlDqhieEPJjdjJQQJ99BFACAAAAAAAAAAAAASAZDOK6f3";
    const processId = "7aa2bde1-c4dd-442a-9932-9f852f40cb54";
    const witRef = "Demo_basic_process.Demo_work_item_type";
    const fieldRef = "Custom.cname";

    const url = `https://dev.azure.com/rajalluri/_apis/work/processes/${processId}/workItemTypes/${witRef}/fields/${fieldRef}?api-version=7.1-preview.2`;

    const headers = {
      "Content-Type": "application/json",
      Authorization: "Basic " + Buffer.from(`:${pat}`).toString("base64"),
    };

    const response = await axios.patch(
      url,
      { defaultValue: firstValue },
      { headers }
    );

    log("Azure DevOps Response Code:", response.status);
    log("Azure DevOps Response Body:", response.data);

    res.json({
      status: response.status,
      message: "CName text field updated successfully.",
      default_value_set: firstValue,
      response: response.data,
    });
  } catch (error) {
    console.error("Azure DevOps update failed:", error);
    res.status(500).json({ status: 500, error: error.message });
  }
});

// ========== Start Server ==========
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
