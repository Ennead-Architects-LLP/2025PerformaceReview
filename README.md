# 2025 Performance Review

[![View Live Report](https://img.shields.io/badge/View%20Live%20Report-Click%20Here-blue)](https://ennead-architects-llp.github.io/2025PerformaceReview/)

A comprehensive employee evaluation system that processes Excel data and generates an interactive HTML report with detailed performance insights, software proficiency tracking, and visual analytics.

## 🚀 Quick Start

**View the Live Report:** [https://ennead-architects-llp.github.io/2025PerformaceReview/](https://ennead-architects-llp.github.io/2025PerformaceReview/)

Or generate your own report locally:

### Prerequisites
- Python 3.7+
- Excel file with employee evaluation data

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/szhang/2025PerformaceReview.git
   cd 2025PerformaceReview
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Usage
3. **Run the application:**
   ```bash
   python employee_self_evaluation_app.py
   ```

4. **View the report:**
   - Open `docs/index.html` in your browser
   - Or serve the `docs/` directory with any web server

## 📊 Features

- **Comprehensive Employee Cards**: Display all employee information including performance ratings, comments, software proficiency, and development goals
- **Interactive Charts**: Visual analytics showing rating distributions, software proficiency levels, and performance trends
- **Profile Images**: Employee photos with fallback to default profile image
- **Responsive Design**: Works on desktop and mobile devices
- **Search & Filter**: Find employees quickly with search functionality
- **Tabbed Interface**: Organized sections for detailed view and summary analytics

## 📁 Project Structure

```
2025PerformaceReview/
├── app/
│   └── modules/
│       ├── html_generator.py    # HTML report generation
│       ├── excel_parser.py      # Excel data processing
│       ├── image_manager.py     # Profile image handling
│       └── ...
├── assets/
│   ├── data/
│   │   ├── Employee Self-Evaluation Data Export From MS Form.xlsx
│   │   └── employee_data.json
│   └── images/                  # Profile images
├── docs/                        # Generated website (GitHub Pages)
│   ├── index.html
│   ├── assets/
│   ├── css/
│   └── js/
├── employee_self_evaluation_app.py  # Application entry point (self-evaluation report generator)
├── evaluator_employee_pdf_maker.py # Batch PDF maker for evaluator-employee pairs
└── requirements.txt
```

## 🔧 Configuration

The application uses the following key configurations:
- **Input Excel**: `assets/data/Employee Self-Evaluation Data Export From MS Form.xlsx`
- **Output Directory**: `docs/` (for GitHub Pages hosting)
- **Default Profile Image**: `assets/images/DEFAULT_PROFILE.jpg`

## 🛠️ Technical Details

- **Backend**: Python with pandas for Excel processing
- **Frontend**: HTML5, CSS3, JavaScript with Chart.js
- **Styling**: Modern responsive design with custom CSS
- **Charts**: Interactive visualizations using Chart.js library

## 📈 Data Processing

The system processes Excel evaluation data and extracts:
- Employee basic information (name, title, role, email)
- Performance ratings (1-5 scale across 5 categories)
- Detailed performance comments and feedback
- Software proficiency ratings (15+ tools)
- Additional evaluation data (strengths, growth areas, culture feedback)

## 🚀 Deployment

The generated HTML files in the `docs/` directory are automatically configured for GitHub Pages deployment. Simply push to your repository and enable GitHub Pages in the repository settings.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary to Ennead Architects. All rights reserved.