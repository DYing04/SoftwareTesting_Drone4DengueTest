# WIF3001 Software Testing Group Project - Drone4Dengue Automated UI Testing Suite

This repository contains the automated Software Testing scripts for the **Drone4Dengue** system. The test suite is built using **Python**, **Selenium WebDriver**, and **Pytest**, focusing on validating the frontend User Interface and exception handling mechanisms against the Software Requirements Specification (SRS).

---

## 🚀 Test Coverage

Currently, the automation suite covers the following modules:

- **UC-7: Manage User**
- **UC-9: Manage Weather Data**

> **Note:** Some tests in this repository (e.g., `TP-09-005`, `TP-09-007`, `TP-09-009`) are intentionally designed to fail in order to expose and document known defects such as UI mismatches, silent failures, and missing server-side validations as part of the QA reporting process.

---

## 📋 Prerequisites

Before running the tests, ensure the following are installed on your machine:

- [Python 3.8+](https://www.python.org/downloads/)
- Google Chrome Browser (Latest Version)
- Git

> **Note:** Selenium 4 automatically handles ChromeDriver installation through Selenium Manager, so no manual ChromeDriver installation is required.

---

# 🛠️ Installation & Setup

## 1. Set Up the System Under Test (Drone4Dengue)

Before running the automated tests, the main Drone4Dengue web application must be running locally.

### Clone the main application repository

```bash
git clone https://github.com/adamarbain/drone4dengue.git
```

Follow the setup and startup instructions provided in the main repository README to start the application locally.

---

## 2. Clone This Testing Repository

Once the main application is running, clone this testing repository:

```bash
git clone https://github.com/DYing04/SoftwareTesting_Drone4DengueTest.git
cd SoftwareTesting_Drone4DengueTest
```

---

## 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

### Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

---

## 4. Install Required Dependencies

```bash
pip install -r requirements.txt
```

---

# 📂 Project Structure

```text
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── test_scripts_uc7/           # Test scripts for User Management
│   ├── test_uc7_tp_07_005.py
│   └── ...
├── test_scripts_uc9/           # Test scripts for Weather Data Management
│   ├── test_uc9_tp_09_001.py
│   ├── valid_weather_data.csv  # Required CSV test data
└── └── ...

```

---

# 🧪 How to Run the Tests

## Run Tests for a Specific Use Case

```bash
pytest test_scripts_uc9/
```

---

## Run a Specific Test Procedure

```bash
pytest test_scripts_uc9/test_uc9_tp_09_002.py
```