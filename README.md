# 🏢 IT Park Company Scoring Tool

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI-412991.svg)](https://openai.com/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

**AI-powered vendor screening and company evaluation tool**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Origin Story](#-origin-story)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Data Collection & Compliance](#-data-collection--compliance)
- [Export Formats](#-export-formats)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🎯 About

**IT Park Company Scoring** is a desktop application that transforms subjective vendor screening into a consistent, evidence-based evaluation process. By leveraging AI and public web data, it provides comprehensive company scorecards to support informed business decisions.

### What It Does ✅

- 🔍 **Automated Data Collection** - Gathers public information from company websites, review platforms, job boards, and news sources
- 📊 **AI-Powered Scoring** - Evaluates companies using a structured rubric with coverage and confidence metrics
- 📄 **Multi-Format Reports** - Exports detailed scorecards as PDF, CSV, and Excel files
- 🎯 **Customizable Criteria** - Select evaluation criteria by category to match your needs
- 💾 **Local Caching** - Stores public pages locally for transparency and auditability
- 🚫 **Smart Filtering** - Automatically disqualifies companies with insufficient public information or no English support

### What It Doesn't Do ❌

- ❌ **No Unauthorized Scraping** - Respects site policies; doesn't access LinkedIn, Apollo, or other restricted platforms
- ❌ **No Data Storage** - API keys are held in memory only and cleared on exit
- ❌ **No Private Data** - Only uses publicly available information

---

## 🌟 Origin Story

This tool emerged from a real-world need identified during my internship with the IT Park regional project management department. We were manually evaluating international businesses for outsourcing opportunities through subjective browsing of various platforms—a process that was:

- ⏰ **Time-consuming** and inconsistent
- 🎲 **Subjective** with varying quality
- 📉 **Difficult to compare** across evaluators

I built this application to replace that manual process with a **systematic, reproducible, and data-driven approach**.

> **🎉 Currently in Active Use**: The tool is actively deployed in the IT Park regional project management department for vendor screening operations.

---

## ✨ Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| 🔄 **Flexible Criteria Selection** | Choose evaluation criteria by category to customize your assessment |
| 📈 **Float-Based Scoring** | Precise numerical scores with coverage and confidence indicators |
| 🤖 **AI-Powered Analysis** | Leverages OpenAI's language models for intelligent evaluation |
| 📦 **Multiple Export Formats** | Generate reports in PDF, CSV, and Excel formats |
| 🗄️ **SQLite Caching** | Local database for storing and auditing collected data |
| 🌐 **Public Data Only** | Respects robots.txt and website terms of service |
| 🖥️ **Desktop Interface** | User-friendly GUI built with PySide6 |
| 🔒 **Privacy-First** | No API key storage; all credentials held in memory only |

### 📊 Scoring System

- **Coverage Metrics**: Measures how much relevant data was available
- **Confidence Scores**: Indicates reliability of the assessment
- **Structured Rubric**: Consistent evaluation framework across all companies
- **Automatic Disqualification**: Filters out companies with insufficient data

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) Python 3.10+ |
| **GUI Framework** | ![Qt](https://img.shields.io/badge/Qt-41CD52?style=flat&logo=qt&logoColor=white) PySide6 |
| **Web Scraping** | Requests • BeautifulSoup4 • lxml |
| **AI/LLM** | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white) OpenAI API |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) SQLite |
| **Export** | ReportLab (PDF) • pandas (Excel/CSV) |

</div>

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Option 1: Development Setup (Recommended for Contributors)

```bash
# Clone the repository
git clone https://github.com/yourusername/itpark-scoring.git
cd itpark-scoring

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install in development mode
pip install -e .

# Run the application
python -m itpark_scoring.app
```

### Option 2: Windows Executable

1. Download `itpark-scoring.exe` from the [Releases](https://github.com/yourusername/itpark-scoring/releases) page
2. Double-click the executable to launch
3. No installation required!

### Option 3: macOS

```bash
# Install the package
pip install itpark-scoring

# Run the application
python -m itpark_scoring.app
```

---

## 💡 Usage

### Quick Start

1. **Launch the Application**
   ```bash
   python -m itpark_scoring.app
   ```

2. **Enter API Key**
   - Paste your OpenAI API key in the designated field
   - The key is stored in memory only and cleared on exit

3. **Configure Evaluation**
   - Select the criteria categories you want to evaluate
   - Customize the scoring parameters if needed

4. **Run Analysis**
   - Enter the company name
   - Click "Analyze" to start the evaluation
   - Wait for the data collection and AI analysis to complete

5. **Export Results**
   - Choose your preferred format (PDF, CSV, Excel)
   - Save the report to your desired location

### Example Workflow

```
Company Name: "Acme Corporation"
Selected Criteria: ✓ Financial Stability
                   ✓ Technical Capability
                   ✓ Client Reviews
                   
→ Data Collection (30-60 seconds)
→ AI Analysis (15-30 seconds)
→ Report Generated ✓

Output: acme_corporation_scorecard.pdf
```

---

## ⚙️ Configuration

### API Key Setup

The application requires an OpenAI API key to function:

1. Obtain an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Enter the key in the application's configuration panel
3. The key is validated before use

**Security Notes:**
- 🔒 API keys are **never stored** on disk
- 💾 Keys are held in memory only during the session
- 🗑️ Keys are automatically cleared when the application closes

### Scoring Criteria

You can customize which criteria are included in the evaluation:

- **Company Profile**: Basic information, industry, size
- **Financial Stability**: Revenue, funding, growth indicators
- **Technical Capability**: Technology stack, certifications, expertise
- **Client Reviews**: Ratings, testimonials, case studies
- **Market Presence**: News mentions, social media, thought leadership
- **Team Quality**: Job postings, employee reviews, team size

---

## 🌐 Data Collection & Compliance

### Data Sources

The tool collects information from:

- ✅ Company websites (public pages)
- ✅ Review platforms (Clutch, G2, etc.)
- ✅ Job boards (public listings)
- ✅ News sites and press releases
- ✅ Search engine results

### Compliance & Ethics

| Aspect | Our Approach |
|--------|-------------|
| **robots.txt** | Fully respected; disallowed pages are skipped |
| **Rate Limiting** | Implemented to avoid overwhelming servers |
| **Terms of Service** | Users should review target sites' ToS |
| **Data Privacy** | Only public information is collected |
| **Attribution** | Source URLs are preserved in reports |

### Excluded Sources

The following platforms are **NOT** accessed due to their terms of service:

- ❌ LinkedIn (requires authorization)
- ❌ Apollo.io (subscription service)
- ❌ Private databases or paywalled content
- ❌ Any site that explicitly prohibits automated access

> **💡 Tip**: For data from restricted sources, consider manual input or approved API integrations.

---

## 📤 Export Formats

### PDF Reports

- Professional formatting with headers and footers
- Charts and visualizations
- Detailed scoring breakdowns
- Source citations

### CSV Exports

- Structured data for analysis
- Compatible with Excel and Google Sheets
- Easy to import into databases

### Excel Workbooks

- Multiple sheets for different sections
- Formatted tables and conditional formatting
- Ready for presentation

---

## 🗺️ Roadmap

### Planned Features

- [ ] 🔌 **API Integration** - Add approved data sources via official APIs
- [ ] 🌍 **Regional Weighting** - Preset scoring weights for different markets
- [ ] ⚖️ **Side-by-Side Comparison** - Compare multiple companies simultaneously
- [ ] 📊 **Historical Tracking** - Track company scores over time
- [ ] 🎨 **Custom Templates** - User-defined report templates
- [ ] 🔔 **Notification System** - Alerts for scoring changes
- [ ] 📱 **Web Dashboard** - Browser-based interface option
- [ ] 🤝 **Team Collaboration** - Shared evaluations and comments


---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs** - Submit detailed issue reports
- 💡 **Suggest Features** - Share ideas for improvements
- 📝 **Improve Documentation** - Help make our docs better
- 🔧 **Submit Pull Requests** - Contribute code improvements

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 IT Park Company Scoring

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---


### FAQ

**Q: Do I need to pay for the OpenAI API?**  
A: Yes, you'll need an OpenAI API account. Pricing varies based on usage.

**Q: Can I use this for commercial purposes?**  
A: Yes! The MIT license allows commercial use.

**Q: How long does an analysis take?**  
A: Typically 1-2 minutes per company, depending on data availability.

**Q: Is my data secure?**  
A: Yes. API keys are not stored, and all data remains local.

---

## ⚠️ Disclaimer

This tool provides **decision support** based on publicly available information. Always validate critical business decisions with:

- ✅ Human review and expertise
- ✅ Direct company contact
- ✅ Legal and financial advisors
- ✅ Multiple data sources

The scores and assessments are meant to **augment**, not replace, professional judgment.

---

## 🙏 Acknowledgments

- **IT Park Regional Project Management Department** - For the opportunity and real-world testing
- **OpenAI** - For providing the AI capabilities
- **Open Source Community** - For the amazing libraries and tools

---
