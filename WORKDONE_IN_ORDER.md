#### **Phase 1: ETL Architecture \& Full Historical Load**

#### 

##### Defined the Scope: Established the target extraction zone to cover the core NCR rental market: Noida, New Delhi, Gurgaon, Ghaziabad, and Faridabad.

##### 

##### Built the Extractor: Wrote a Python web scraper utilizing requests and BeautifulSoup to parse MagicBricks HTML tags (mb-srp\_\_card) and extract property titles, raw prices, and square footage.

##### 

##### Implemented Dynamic Navigation: Engineered an infinite while loop with an auto-stop condition (if len(listings) == 0: break) to dynamically handle the varying number of listing pages across different cities without hardcoding limits.

##### 

##### Transformed the Data: Utilized pandas to clean raw price strings (handling "Lac" and "₹" conversions), calculate PRICE\_PER\_SQFT, and append a SCRAPED\_AT timestamp to establish the Historical Snapshot Model.

##### 

##### Configured Database Connections: Integrated snowflake.connector alongside write\_pandas for Snowflake, and sqlalchemy for Neon (PostgreSQL), strictly mapping credentials to a local .env file.

##### 

##### Executed the Backfill: Ran the unconstrained script locally, successfully extracting, transforming, and loading 25,770 historical property records into both database environments.

##### 

#### **Phase 2: Version Control \& Cloud Automation**

##### 

##### Optimized for Incremental Loads: Modified the script's while loop to enforce a strict 5-page ceiling (while page <= 5:), converting the heavy historical scraper into a lightweight daily delta scraper.

##### 

##### Drafted the CI/CD Pipeline: Created the .github/workflows/daily\_scraper.yml file, configuring an Ubuntu server environment, Python dependency installations, and a scheduled cron trigger.

##### 

##### Secured Cloud Credentials: Migrated the 7 local .env variables (SNOWFLAKE\_USER, NEON\_DB\_URL, etc.) into encrypted GitHub Repository Secrets.

##### 

##### Committed the Codebase: Initialized Git, staged the Python scripts and workflow directory, and pushed the master branch to the remote GitHub repository.

##### 

##### Validated the Deployment: Manually triggered the workflow\_dispatch event in GitHub Actions, actively monitoring the server logs until the scrape-and-load job executed flawlessly in under three minutes.

