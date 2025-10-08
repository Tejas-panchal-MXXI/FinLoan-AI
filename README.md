# FinLoan AI

AI-powered loan approval system with 86% accuracy built using Django and Machine Learning.

## Features

- **🤖 AI Predictions**: 86% accurate loan approval using machine learning
- **⚡ Instant Results**: Get approval/rejection decisions in seconds  
- **📊 Analytics Dashboard**: Real-time ML model performance and statistics
- **📱 3-Step Application**: Easy loan application process
- **👨‍💼 Admin Panel**: Complete loan and user management
- **📈 Multiple Models**: Logistic Regression, SVM, Random Forest
- **🎨 Modern UI**: Professional finance-themed responsive design
- **🔍 Detailed Analysis**: See which factors influenced the decision

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Steps

1. **Clone the repository**
git clone https://github.com/yourusername/FinLoan-AI.git
cd FinLoan-AI

2. **Create virtual environment**
python -m venv venv

Activate virtual environment
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate


3. **Install dependencies**
pip install -r requirements.txt


4. **Setup database**
python manage.py migrate


5. **Run the application**
python manage.py runserver


6. **Access the application**
- **Main App**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin

## Usage

1. **Home Page**: View application features and ML model accuracy
2. **Apply**: Complete the 3-step loan application form
3. **Results**: Get instant AI-powered approval/rejection decision
4. **Analytics**: View detailed ML model performance metrics
5. **Dashboard**: View and manage all loan applications

## Machine Learning Details

### Model Performance
- **Logistic Regression**: 86% accuracy (Primary model)
- **Support Vector Machine**: 84% accuracy
- **Random Forest**: 82% accuracy

### Decision Factors (Importance)
- **Credit History**: 35.2%
- **Total Income**: 18.1%
- **Loan-Income Ratio**: 14.9%
- **Education Level**: 12.2%
- **Property Area**: 8.5%
- **Employment Status, Age, Gender**: Remaining factors

## Technology Stack

- **Backend**: Django 4.2+, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: scikit-learn, pandas, numpy ,jupyter notebook
- **Database**: SQLite (development)

## Project Structure

FinLoan-AI/
├── finloan_ai/ # Django project settings
├── loan_predictor/ # Main application
├── templates/ # HTML templates
├── static/ # CSS, JS
├── data/ # ML training datasets
└── requirements.txt # Python dependencies
