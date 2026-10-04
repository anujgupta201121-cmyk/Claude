-- =====================================================================
-- LOOKVEST  |  LLM consensus tracking schema (Snowflake)
-- Load data/lookvest_question_bank.csv, log every LLM answer, and read
-- the consensus answer per question per day.
-- (Databricks: the same DDL works as Delta tables - swap VARIANT for STRING/
--  MAP and QUALIFY is supported on DBR 12+.)
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS LOOKVEST.CONSENSUS;
USE SCHEMA LOOKVEST.CONSENSUS;

-- 1. Question bank -----------------------------------------------------
CREATE OR REPLACE TABLE QUESTION_BANK (
    QUESTION_ID           STRING,
    QUESTION              STRING,
    CATEGORY              STRING,
    SUBCATEGORY           STRING,
    FAMILY                STRING,
    PRIORITY              FLOAT,
    REQUIRED              BOOLEAN,
    ANSWER_ENTITY         STRING,
    PRIMARY_ANSWER_FIELD  STRING,
    ANSWER_FIELDS         STRING,     -- pipe-delimited extraction fields
    MONETIZATION          STRING,
    REFRESH_CADENCE       STRING,     -- weekly | monthly | quarterly | yearly
    GEO_SCOPE             STRING,
    MARKET                STRING,
    MARKET_RANK           INTEGER,
    MARKET_TIER           STRING,
    COUNTRY_CODE          STRING,
    CONTINENT             STRING,
    AGE_GROUP             STRING,
    GENDER                STRING,
    RECIPIENT             STRING,
    OCCASION              STRING,
    BUDGET                STRING,
    USE_CASE              STRING,
    PRODUCT_CATEGORY      STRING,
    BRAND                 STRING,
    QUESTION_HASH         STRING      -- stable join key across rebuilds
);

CREATE OR REPLACE FILE FORMAT LV_CSV TYPE = CSV SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"' EMPTY_FIELD_AS_NULL = TRUE;
CREATE STAGE IF NOT EXISTS LV_STAGE FILE_FORMAT = LV_CSV;
-- PUT file://data/lookvest_question_bank.csv @LV_STAGE AUTO_COMPRESS=TRUE;
-- COPY INTO QUESTION_BANK FROM @LV_STAGE/lookvest_question_bank.csv.gz;

-- 2. Raw LLM answers ---------------------------------------------------
CREATE TABLE IF NOT EXISTS LLM_RESPONSES (
    RUN_ID          STRING,
    RUN_TS          TIMESTAMP_NTZ,
    QUESTION_HASH   STRING,
    PROVIDER        STRING,           -- anthropic | openai | google | perplexity | meta ...
    MODEL           STRING,
    SURFACE         STRING,           -- api | consumer_app | search_overview
    WEB_SEARCH      BOOLEAN,
    PROMPT_LOCALE   STRING,
    RAW_ANSWER      STRING,
    CITATIONS       VARIANT           -- list of {url, domain}
);

-- 3. Structured extraction (one row per entity mentioned, ranked) ------
CREATE TABLE IF NOT EXISTS LLM_ANSWER_ENTITIES (
    RUN_ID          STRING,
    QUESTION_HASH   STRING,
    PROVIDER        STRING,
    MODEL           STRING,
    MENTION_RANK    INTEGER,          -- 1 = first / top recommendation
    PRIMARY_VALUE   STRING,           -- normalised hotel_name / product_name / title ...
    FIELDS          VARIANT,          -- every field in QUESTION_BANK.ANSWER_FIELDS
    PURCHASE_DOMAIN STRING,           -- booking / retailer / streamer domain cited
    EXTRACTED_TS    TIMESTAMP_NTZ
);

-- 4. Consensus: which answer most models give, per question per day -----
CREATE OR REPLACE VIEW V_CONSENSUS_DAILY AS
WITH top_pick AS (
    SELECT e.QUESTION_HASH, DATE_TRUNC('day', r.RUN_TS) AS RUN_DATE,
           e.PROVIDER, e.MODEL, e.PRIMARY_VALUE, e.PURCHASE_DOMAIN
    FROM LLM_ANSWER_ENTITIES e
    JOIN LLM_RESPONSES r USING (RUN_ID, QUESTION_HASH, PROVIDER, MODEL)
    WHERE e.MENTION_RANK = 1
),
votes AS (
    SELECT QUESTION_HASH, RUN_DATE, PRIMARY_VALUE,
           COUNT(DISTINCT MODEL)                              AS MODELS_AGREEING,
           MODE(PURCHASE_DOMAIN)                              AS TOP_PURCHASE_DOMAIN,
           ARRAY_AGG(DISTINCT MODEL)                          AS MODELS
    FROM top_pick GROUP BY 1, 2, 3
),
totals AS (
    SELECT QUESTION_HASH, RUN_DATE, COUNT(DISTINCT MODEL) AS MODELS_ASKED
    FROM top_pick GROUP BY 1, 2
)
SELECT q.QUESTION_ID, q.QUESTION, q.CATEGORY, q.MARKET, v.RUN_DATE,
       v.PRIMARY_VALUE                                   AS CONSENSUS_ANSWER,
       v.TOP_PURCHASE_DOMAIN,
       v.MODELS_AGREEING, t.MODELS_ASKED,
       ROUND(v.MODELS_AGREEING / t.MODELS_ASKED, 3)      AS CONSENSUS_SHARE,
       v.MODELS
FROM votes v
JOIN totals t USING (QUESTION_HASH, RUN_DATE)
JOIN QUESTION_BANK q USING (QUESTION_HASH)
QUALIFY ROW_NUMBER() OVER (PARTITION BY v.QUESTION_HASH, v.RUN_DATE
                           ORDER BY v.MODELS_AGREEING DESC, v.PRIMARY_VALUE) = 1;

-- 5. Share of voice: how often a brand / business is recommended -------
CREATE OR REPLACE VIEW V_SHARE_OF_VOICE AS
SELECT q.CATEGORY, q.SUBCATEGORY, q.MARKET, e.PRIMARY_VALUE AS ENTITY,
       DATE_TRUNC('week', e.EXTRACTED_TS)                         AS WEEK,
       COUNT(*)                                                   AS MENTIONS,
       COUNT_IF(e.MENTION_RANK = 1)                               AS TOP_PICKS,
       RATIO_TO_REPORT(COUNT(*)) OVER (PARTITION BY q.CATEGORY, q.SUBCATEGORY,
                                       q.MARKET, DATE_TRUNC('week', e.EXTRACTED_TS)) AS SHARE_OF_VOICE
FROM LLM_ANSWER_ENTITIES e
JOIN QUESTION_BANK q USING (QUESTION_HASH)
GROUP BY 1, 2, 3, 4, 5;
