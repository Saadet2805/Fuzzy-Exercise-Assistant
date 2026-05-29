# Fuzzy Exercise Assistant

## Project Overview

This project was developed as part of the **Fuzzy Sets and Systems II** course at the University of Bern, under the supervision of **Prof. Dr. Edy Portmann** and **MSc. Sandro Suter**.

The Fuzzy Exercise Assistant is a decision support system that generates personalized exercise category recommendations using a **Fuzzy Cognitive Map (FCM)**. The system takes user inputs—Body Mass Index (BMI), self-reported fitness level, muscle gain priority, and weight loss priority—and produces ranked recommendations for four exercise categories:

- **Light Cardio** (walking, swimming, cycling)
- **Strength Training** (resistance exercises, weightlifting)
- **HIIT** (High-Intensity Interval Training)
- **Beginner Programs** (foundational exercise routines)

The system implements the **mKosko inference method** with a **sigmoid transfer function**, iteratively updating node activations until convergence (threshold ε = 0.001). All user interactions are logged to a CSV file for evaluation purposes.

---

## Project Structure
fuzzy-exercise-assistant/
│
├── server.py # Flask backend server
├── fcm_engine.py # FCM inference engine (fcmpy + native fallback)
├── results_logger.py # CSV logging for evaluation data
├── index.html # Frontend web interface
├── app.js # Frontend JavaScript logic
├── styles.css # Frontend styling
├── results.csv # Logged user data (auto-generated)
├── README.md # This file
└── requirements.txt # Python dependencies


---

## System Architecture

The application follows a **three-tier architecture**:

| Layer | Components |
|-------|------------|
| **Frontend** | HTML/CSS/JavaScript interface for user input and result display |
| **Backend** | Flask API server handling HTTP requests and FCM computation |
| **Processing** | FCM inference engine with mKosko + sigmoid |

---

## Prerequisites

- **Python 3.8 or higher** (Python 3.9+ recommended)
- **pip** package manager

---

## Installation

### 1. Clone or Download the Project

Ensure all project files are in the same directory.

### 2. Create a Requirements File

Create a `requirements.txt` file with the following content:

```
flask>=2.0.0
numpy>=1.19.0
pandas>=1.0.0
```
### 3. Install Dependencies

Open a terminal in the project directory and run:
```
pip install -r requirements.txt
```
Or install manually:
```
pip install flask numpy pandas
```
### 4. Optional: Install fcmpy (for exact library match)

The system includes a native fallback implementation that works without `fcmpy`. However, if you wish to use the official `fcmpy` library:
```
pip install fcmpy
```
**Note:** `fcmpy` requires an older version of pandas (1.3.3). If installation fails, the system will automatically fall back to the native implementation with identical mathematical behavior.


## Running the Application

### 1. Start the Flask Server

In the project direcctory, run: 
```
python server.py
```
You should see output similar to:

```txt
Fuzzy Exercise Assistant
FCM engine: built-in (install fcmpy for exact library match) (version 2.3)
Open: http://127.0.0.1:5000
Evaluation log: /path/to/results.csv
Press Ctrl+C to stop.
```
### 2. Access the Web Interface

Open your web browser and navigate to:

```txt
http://127.0.0.1:5000
```

### 3. Using the Assistant

1. Click the "Start" button

2. Enter your first name

3. Calculate your BMI using the provided link, then enter the value

4. Adjust the three sliders (1–10) for:

- Fitness level (1 = Beginner, 10 = Very fit)
- Muscle gain goal priority
- Weight loss goal priority

5. Click "Get my recommendation"

6. View your ranked exercise recommendations with match percentages

### 4. Stopping the Server

Press Ctrl + C in the terminal to stop the Flask server.

## Evaluation Summary

### Key Findings

1. **Strong Usability and Goal Alignment** – The system achieved high scores for usability (4.91) and goal alignment (4.45)

2. **Personalization Requires Enhancement** – Lower scores for personalization (3.64) indicate need for more specific recommendations

3. **Safety Perception Is High** – Safety scores were uniformly high across all BMI categories

4. **Demand for Expanded Inputs and Outputs** – Users requested additional variables (medical conditions, body fat percentage) and more granular outputs

## Future Work
Based on evaluation findings, the following improvements are recommended:

- Add explanation feature providing reasoning for each recommendation

- Expand output categories to include specific exercises and target muscles

- Refine slider scale (0–10 with clearer labels)

- Add medical conditions and body fat percentage as optional inputs

- Embed BMI calculator within the interface

- Integrate multimedia resources (video demonstrations)

- Implement personalized workout planning feature

## Acknowledgements

This project was developed as part of the **Fuzzy Sets and Systems II** course at the **University of Fribourg**.

**Supervisors**:
- Prof. Dr. Edy Portmann
- MSc. Sandro Suter

**Project Team**:
- Mercan Esen
- Saadet Yilmaz

