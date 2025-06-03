USE my_database;

CREATE TABLE cn_numbers (
  id INT AUTO_INCREMENT PRIMARY KEY,
    cn_number VARCHAR(100) NOT NULL
);

INSERT INTO cn_numbers (cn_number) VALUES ('CN001'), ('CN002'), ('CN003');

select * from my_database.cn_numbers;


Node js configuration details:

npm init -y
npm install express mysql axios body-parser


to run node js: node app.js

To Fetch CN numbers : http://localhost:5008/update-cn
To Push picklist to Azure: http://localhost:5008/push_cn_to_azure
To Update default text field: http://localhost:5008/update-cname-text