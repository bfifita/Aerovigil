# AeroVigil

**Predictive Fatigue Risk Analytics for Aviation Safety**

---

## AeroVigil Dashboard

Below is a preview of the AeroVigil prototype interface and fatigue risk visualization.

![AeroVigil Dashboard](aerovigil_1.png)

![Fatigue Chart](aerovigil_2.png)

AeroVigil is a prototype aviation safety tool designed to estimate **crew fatigue risk** using key operational factors such as duty hours, flight segments, time zone changes, rest periods, and circadian disruption.

This project was built as an early proof-of-concept for a larger vision: helping airlines and aviation safety teams identify fatigue risk **before flights operate**.

---

# 1. Live Demo

👉 **AeroVigil App**  
https://aerovigil-demo.streamlit.app

---

# 2. Overview

Fatigue remains one of the most critical human factors issues in aviation safety. AeroVigil explores how operational inputs from crew scheduling and duty periods can be converted into a clear **fatigue risk score**.

This prototype allows users to experiment with different operational scenarios and instantly see how fatigue risk changes.

---

# 3. Features

- Calculates a **fatigue risk score** from 0–100
- Uses operational inputs such as:
  - Duty hours
  - Flight segments
  - Time zone changes
  - Rest hours before duty
  - Circadian disruption
- Displays a fatigue **classification level**
  - LOW
  - MODERATE
  - HIGH
- Provides a **mitigation recommendation**
- Includes a **scenario comparison chart**
- Includes a **4-day fatigue trend / timeline predictor**
- Built with an interactive **Streamlit dashboard**

---

# 4. How It Works

The fatigue calculator assigns weighted values to operational risk factors:

- Longer duty periods increase fatigue risk
- More flight segments increase workload
- Crossing time zones increases disruption
- Greater circadian disruption increases fatigue likelihood
- More rest before duty lowers fatigue risk

The total is converted into a capped score from **0–100**, making it easier to understand risk severity.

### Workflow

Flight Schedule Inputs  
↓  
Fatigue Prediction Algorithm  
↓  
Fatigue Risk Score  
↓  
Risk Classification & Mitigation Guidance  
↓  
Safety Dashboard Visualization

---

# 5. Example Use Cases

AeroVigil can be used as a prototype concept for:

- Comparing duty schedules
- Demonstrating fatigue risk visually
- Exploring human factors research ideas
- Presenting an aviation safety analytics concept
- Building future predictive safety tools for airline operations

---

# 6. Future Development Roadmap

Planned future improvements may include:

- Real airline schedule data integration
- Predictive crew fatigue dashboards
- AI-based fatigue forecasting
- Risk alerts for schedulers and safety departments
- FRMS compliance reporting tools
- Multi-crew schedule analysis
- Exportable fatigue risk reports
- Airline operational scenario modeling

---

# 7. Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Matplotlib**

---

# 8. Project Structure

```bash
AeroVigil/
│
├── app.py
│   Streamlit dashboard interface
│
├── fatigue_calculator.py
│   Core fatigue risk scoring algorithm
│
├── requirements.txt
│   Python dependencies required to run the project
│
├── README.md
│   Project documentation
│
├── aerovigil_1.png
│   Dashboard screenshot


</> Markdown


# 9. Installation

Clone the repository:

```bash
git clone https://github.com/bfifita/AeroVigil.git
cd AeroVigil

pip install -r requirements.txt

streamlit run app.py

10. Vision
AeroVigil is more than a calculator — it represents the beginning of a broader aviation safety concept focused on predictive fatigue analytics.
The long-term vision is to build tools that help aviation organizations move from reacting to fatigue events to predicting and preventing fatigue risk before it impacts safety.
Future versions of AeroVigil could support airline Safety Management Systems (SMS) and Fatigue Risk Management Systems (FRMS) through predictive analytics and operational risk visualization.
11. Author
Bosslady Fifita
Founder — AeroVigil
MS Aeronautics | Aviation Human Factors & Safety
Research Focus:
Aviation Human Factors
Fatigue Risk Management
Aviation Safety Systems
Predictive Safety Analytics
12. Disclaimer
AeroVigil is a prototype created for educational, research, and demonstration purposes only.
This project is not intended to replace certified aviation fatigue management systems, regulatory compliance tools, or operational decision-making systems used by airlines or aviation authorities.
License
This project is licensed under the MIT License – see the LICENSE file for details.
The fatigue scoring model used in this prototype is a simplified demonstration and should not be used for operational aviation safety decisions.
License
This project is licensed under the MIT License – see the LICENSE file for details.
The fatigue scoring model used in this prototype is a simplified demonstration and should not be used for operational aviation safety decisions.
└── aerovigil_2.png
    Fatigue risk visualization screenshot
