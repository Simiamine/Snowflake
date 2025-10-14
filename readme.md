# dbt Bootcamp: Zero to Hero – Airbnb Project

This repository is dedicated to following the Udemy course **"The Complete dbt (Data Build Tool) Bootcamp: Zero to Hero"**. The main objective is to master dbt professionally by building a comprehensive, real-world, hands-on dbt project based on Airbnb data, covering both theory and practice.

## Course Objectives

- **Professional dbt Usage:** Learn to use the dbt platform through a complete Airbnb project.
- **Environment Setup:** Configure development environments on Mac & Windows, connect to Snowflake and BI tools, set up dbt profiles, and extend IDEs with dbt tools.
- **Core dbt Concepts:** Master Models, Materializations, Sources, Seeds, Snapshots, Packages, Hooks, Exposures, Analyses, and complex SQL queries.
- **Project Structure & Best Practices:** Understand dbt project structure, tips, tricks, advanced techniques, and extend dbt with custom/third-party macros.
- **Testing:** Implement singular and generic dbt tests, use additional arguments and config values, and customize built-in tests.
- **Documentation:** Document models and pipelines, customize dbt docs, and analyze dependencies between transformation steps.
- **Modern Data Stack:** Learn how dbt fits into the modern data stack, stages of the Data-Maturity Model, and robust Data Architectures.
- **ETL/ELT & Analytics Engineering:** Master ETL/ELT procedures, data transformations, Slowly Changing Dimensions, CTEs, and analytics engineering.
- **Data Storage Concepts:** Understand Data Warehouses, Data Lakes, Data Lakehouses, and their use cases; handle data collection, wrangling, and integrations.
- **Advanced Testing:** Explore dbt-expectations for advanced testing, inspired by Great Expectations.
- **Certification Preparation:** Test your knowledge with certification questions.
- **Industry Insights:** Listen to real-world use-cases from professionals.
- **Orchestration Best Practices:** Learn hands-on dbt orchestration best practices.

---

## Project Structure

```
.
├── models/
│   ├── staging/
│   ├── marts/
│   └── ...
├── seeds/
├── snapshots/
├── macros/
├── tests/
├── analyses/
├── docs/
├── dbt_project.yml
└── README.md
```

- **models/**: Contains SQL models for staging and marts.
- **seeds/**: CSV files for seed data.
- **snapshots/**: Snapshot definitions for slowly changing dimensions.
- **macros/**: Custom and third-party macros.
- **tests/**: Singular and generic tests.
- **analyses/**: Analytical queries and reports.
- **docs/**: Documentation files.
- **dbt_project.yml**: Main dbt project configuration.

---

## Installation & Setup

### Prerequisites

- Python 3.7+
- dbt (latest version)
- Snowflake account
- Git

### Steps

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/dbt-airbnb-project.git
    cd dbt-airbnb-project
    ```

2. **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dbt**
    ```bash
    pip install dbt-snowflake
    ```

4. **Configure dbt Profile**
    - Edit `~/.dbt/profiles.yml` with your Snowflake credentials.

5. **Install Dependencies**
    ```bash
    dbt deps
    ```

6. **Run dbt**
    ```bash
    dbt run
    dbt test
    dbt docs generate
    dbt docs serve
    ```

---

## Usage

- **Development:** Use the `models/` directory to build and test transformations.
- **Testing:** Add tests in the `tests/` directory and run `dbt test`.
- **Documentation:** Generate and serve docs with `dbt docs generate` and `dbt docs serve`.
- **Orchestration:** Integrate with orchestration tools as per course instructions.

---

## Contributing

Feel free to fork the repository, open issues, or submit pull requests for improvements or fixes.

---

## License

This project is for educational purposes following the Udemy course. Please refer to the course and dbt documentation for further details.

---

## References

- [dbt Documentation](https://docs.getdbt.com/)
- [Udemy Course](https://www.udemy.com/course/the-complete-dbt-bootcamp-zero-to-hero/)
- [Snowflake Documentation](https://docs.snowflake.com/)
