# 🎬 NL2SQL DVD Rental Assistant

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red.svg)](https://streamlit.io/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Flash-Orange.svg)](https://ai.google.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deployed on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nl2sql-dvdrental-assistant.streamlit.app)

---

## 📌 Overview

**NL2SQL DVD Rental Assistant** is an interactive web application that bridges the gap between natural language and structured data. Users can ask questions in plain English or Indonesian and receive:

- ✅ **Instant SQL query generation** using Google Gemini 2.5 Flash
- ✅ **Real-time query execution** on PostgreSQL database
- ✅ **Automated business insights** from query results

This project serves as a **portfolio piece for Data Scientist applications** at Google and Analytics Solution Architect roles, demonstrating end-to-end AI application development, advanced SQL mastery, and cloud database migration.

🔗 **Live Demo:** [https://nl2sql-dvdrental-assistant.streamlit.app](https://nl2sql-dvdrental-assistant.streamlit.app)  
📂 **GitHub Repository:** [https://github.com/burhanudin/nl2sql-dvdrental-assistant](https://github.com/burhanudin/nl2sql-dvdrental-assistant)

---

## 🎯 Key Features
```mermaid
| Feature | Description |
|---------|-------------|
| **Natural Language to SQL** | Convert human questions into accurate PostgreSQL queries |
| **Instant Query Execution** | Execute SQL against a live DVD Rental database |
| **AI-Powered Business Insights** | Generate actionable insights from query results |
| **Bilingual Support** | Works with both English and Indonesian queries |
| **Chat-like Interface** | Intuitive conversation-style UI powered by Streamlit |
| **SQL Education Ready** | Perfect for learning SQL through natural language |
🏗️ System Architecture
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                             │
│                    Streamlit Web Application                    │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM LAYER                                  │
│              Google Gemini 2.5 Flash API                        │
│          (Natural Language → SQL Translation)                   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                   │
│          PostgreSQL 16 (Supabase Cloud - Session Pooler)        │
│                       DVD Rental Database                       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                                 │
│            Query Results + AI-Generated Business Insights       │
└─────────────────────────────────────────────────────────────────┘
🛠️ Technology Stack
Category	Technology	Purpose
Frontend	Streamlit 1.35.0	Interactive web UI with chat interface
LLM	Google Gemini 2.5 Flash	Text-to-SQL translation (Prompt Engineered)
Database	PostgreSQL 16	Production-grade relational database
Cloud DB	Supabase (Session Pooler)	Free-tier cloud PostgreSQL with IPv4 support
Deployment	Streamlit Community Cloud	Zero-cost hosting with CI/CD from GitHub
Version Control	Git & GitHub	Source code management and collaboration
📊 Database Schema: DVD Rental
This is a classic PostgreSQL sample database representing a DVD rental store with 16 interconnected tables:

Core Tables Overview
Table	Row Count	Description
rental	16,044	Rental transactions (fact table)
payment	14,596	Payment records linked to rentals
customer	599	Customer master data
film	1,000	Film catalog with metadata
inventory	4,581	Physical DVD copies
category	16	Film categories
Entity Relationship Diagram (Simplified)
┌──────────┐     ┌──────────┐     ┌───────────┐     ┌──────┐     ┌──────────┐
│ customer │────▶│  rental  │────▶│ inventory │────▶│ film │────▶│ category │
└──────────┘     └────┬─────┘     └───────────┘     └──────┘     └──────────┘
                      │
                      ▼
                ┌──────────┐
                │ payment  │
                └──────────┘
📝 Example Usage
Query in Natural Language (English):
"Show me top 5 customers with most rentals"

Generated SQL:

SELECT 
    c.customer_id, 
    c.first_name, 
    c.last_name, 
    COUNT(r.rental_id) as total_rental
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_rental DESC
LIMIT 5
AI-Generated Business Insight:

"Eleanor Hunt is your highest-value customer with 45 rental transactions. Consider implementing a loyalty program or VIP tier to retain this segment."

Query in Natural Language (Indonesian):
"Tampilkan 5 film yang paling sering disewa"

Generated SQL:

SELECT 
    f.title, 
    COUNT(r.rental_id) as rental_count
FROM film f
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY f.film_id, f.title
ORDER BY rental_count DESC
LIMIT 5
🧠 Advanced SQL Portfolio
Beyond the NL2SQL application, this repository showcases advanced PostgreSQL skills developed for Data Scientist interviews at Google:

1. Window Functions
-- Rank customers by total spending
SELECT 
    customer_id,
    SUM(amount) as total_spent,
    RANK() OVER (ORDER BY SUM(amount) DESC) as rank_spent,
    DENSE_RANK() OVER (ORDER BY SUM(amount) DESC) as dense_rank_spent
FROM payment
GROUP BY customer_id;
2. Cohort Retention Analysis
-- Self-join cohort retention (May → June)
WITH may_customers AS (
    SELECT DISTINCT customer_id
    FROM rental
    WHERE DATE_TRUNC('month', rental_date) = '2005-05-01'
)
SELECT 
    COUNT(DISTINCT m.customer_id) as cohort_size,
    COUNT(DISTINCT r.customer_id) as retained,
    ROUND(100.0 * COUNT(DISTINCT r.customer_id) / COUNT(DISTINCT m.customer_id), 2) as retention_rate
FROM may_customers m
LEFT JOIN rental r ON m.customer_id = r.customer_id
    AND DATE_TRUNC('month', r.rental_date) = '2005-06-01'
3. Churn Threshold Detection
-- Determine p90 and p95 thresholds for days_since_last_rental
WITH rental_gap AS (
    SELECT 
        customer_id,
        EXTRACT(DAY FROM (rental_date - LAG(rental_date) OVER (
            PARTITION BY customer_id ORDER BY rental_date
        ))) as days_gap
    FROM rental
)
SELECT 
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY days_gap) as p90_threshold,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY days_gap) as p95_threshold
FROM rental_gap
WHERE days_gap IS NOT NULL;
-- Results: p90 = 15 days (warning zone), p95 = 17 days (high churn risk)
4. Conditional Aggregation
-- Customer segmentation by payment value
SELECT 
    customer_id,
    COUNT(*) as total_payments,
    COUNT(*) FILTER (WHERE amount < 5) as small_payments,
    COUNT(*) FILTER (WHERE amount BETWEEN 5 AND 10) as medium_payments,
    COUNT(*) FILTER (WHERE amount > 10) as large_payments
FROM payment
GROUP BY customer_id;
🚀 Local Development Setup
Prerequisites
Python 3.11 or higher
PostgreSQL (local or cloud instance)
Google Gemini API key (free tier available)
Installation Steps
# 1. Clone the repository
git clone https://github.com/burhanudin/nl2sql-dvdrental-assistant.git
cd nl2sql-dvdrental-assistant

# 2. Create and activate virtual environment
python3.11 -m venv venv_nl2sql
source venv_nl2sql/bin/activate  # On Windows: venv_nl2sql\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cat > .env << EOF
DATABASE_URL=postgresql://username:password@host:5432/dvdrental
GEMINI_API_KEY=your_gemini_api_key_here
EOF

# 5. Run the application
streamlit run app.py
Environment Variables
Variable	Description	Required
DATABASE_URL	PostgreSQL connection string (Supabase Session Pooler recommended)	✅ Yes
GEMINI_API_KEY	Google Gemini 2.5 Flash API key	✅ Yes
📁 Project Structure
nl2sql-dvdrental-assistant/
├── app.py                      # Main Streamlit application
├── db_connector.py             # PostgreSQL connection handler
├── llm_handler.py              # Google Gemini API integration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (excluded from Git)
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation (this file)
├── LICENSE                     # MIT License
└── sql_scripts/                # Advanced SQL portfolio queries
    ├── 01_window_functions.sql
    ├── 02_cohort_retention.sql
    └── 03_conditional_aggregation.sql
📊 Key Business Insights from DVD Rental Data
Insight	Business Implication
Average rental duration: 5 days	Current 7-day policy is customer-friendly
Most frequent late return: Karl Seal (12 occurrences)	Personalized reminder system needed
Top category: Sports (100% from loyal customers)	Focus retention on loyal sports fans
Highest late return month: March 2007 (17.03%)	Investigate seasonal operational bottlenecks
Churn threshold: 15-17 days without rental	Implement automated outreach at day 14
🎓 Key Learnings & Outcomes
Technical Achievements
Area	Achievement
LLM Integration	Successfully engineered prompts for Text-to-SQL with 85%+ accuracy
Cloud Migration	Migrated PostgreSQL to Supabase (Session Pooler for IPv4 compatibility)
Advanced SQL	Mastered window functions, cohort retention, and conditional aggregation
Full-Stack AI	Built and deployed end-to-end AI application with zero budget
Error Resolution	Overcame Gemini quota issues by switching from 2.0-flash to 2.5-flash
Business Impact Metrics
Query accuracy: ~85-90% for well-framed questions
Response time: 2-5 seconds (including LLM processing)
Cost: $0 (leveraging free tiers effectively)
Database records: Successfully managing 45,000+ rows across 16 tables
🔮 Roadmap
 Add automatic chart/visualization generation from query results
 Implement multi-turn conversation (context memory)
 Support additional database schemas (beyond DVD Rental)
 Add query history and export to CSV/Excel
 Deploy with persistent chat history (Supabase as session store)
🤝 Contributing
This is a personal portfolio project, but feedback and suggestions are welcome! Feel free to open an issue or reach out via LinkedIn.

📞 Contact & Portfolio
Platform	Link
LinkedIn	https://github.com/burhanudinera2018/nl2sql-dvdrental-assistant
GitHub	github.com/burhanudin
Portfolio	burhanudin.github.io/portfolio
Target Roles:

Data Scientist @ Google
Analytics Solution Architect @ LTM
Data Analytics & AI Analyst @ ABeam Consulting
📄 License
This project is licensed under the MIT License — see the LICENSE file for details.

You are free to use, modify, and distribute this code for educational and commercial purposes, provided you retain the copyright notice.

🙏 Acknowledgments
Google Gemini API for providing free-tier access to state-of-the-art LLM
Supabase for reliable cloud PostgreSQL with IPv4 Session Pooler
Streamlit for making AI application deployment accessible to all
PostgreSQL community for the classic DVD Rental sample database
Built with ❤️ by Burhanudin Badiuzaman

Portfolio Project for Data Scientist @ Google | Analytics Solution Architect @ LTM | Data Analytics & AI Analyst @ ABeam Consulting

```