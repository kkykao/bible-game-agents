# Bible Learning Game - AI Agents Backend

An immersive, theologically grounded Christian learning experience powered by CrewAI and Claude.

## Features

- **KJV 1611 Literalist Theology** - All content grounded in historical-grammatical interpretation
- **16 Biblical Character Agents** - Jesus, David, Solomon, Moses, Joshua, and 11 others
- **Multi-Agent System** - Orchestrator, Quest Master, Character Agents, Learning Personalizer
- **Traditional Chinese Localization** - Full support for Hong Kong/Taiwan audiences
- **Strong's Concordance Integration** - Deep linguistic analysis of original Greek/Hebrew
- **Dynamic Quest Generation** - Procedurally generated quests aligned with biblical narratives
- **Live Character Dialogue** - Interact with biblical figures with authentic theology

## Quick Start

### 1. Clone Repository
\\\ash
git clone https://github.com/yourusername/bible-game-agents.git
cd bible-game-agents
\\\

### 2. Create Virtual Environment
\\\ash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\Activate.ps1  # Windows PowerShell
\\\

### 3. Install Dependencies
\\\ash
pip install -r requirements.txt
\\\

### 4. Configure Environment
\\\ash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
\\\

### 5. Download Bible Data
\\\ash
bash scripts/download_bible_data.sh
\\\

### 6. Initialize Database
\\\ash
python scripts/init_database.py
python scripts/seed_data.py
\\\

### 7. Run Backend
\\\ash
python src/main.py
# Server starts on http://localhost:8000
\\\

### 8. Run Frontend (new terminal)
\\\ash
cd frontend
npm install
npm run dev
# App opens on http://localhost:5173
\\\

## Characters

- Jesus Christ - The Risen Lord
- Enoch - Translator to Heaven
- Noah - Preacher of Righteousness
- Abraham - Father of the Faithful
- Isaac - The Promised Son
- Jacob/Israel - Prince with God
- Joseph - From Slave to Ruler
- Moses - Deliverer and Lawgiver
- Joshua - Captain of the Lord's Army
- Matthew - Apostle and Tax Collector
- Mark - Apostle of Action
- Luke - Physician and Historian
- John - Beloved Disciple
- David - King and Psalmist
- Solomon - The Wise King

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Character Theology](docs/CHARACTER_THEOLOGY.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT License - See LICENSE file

## Acknowledgments

- CrewAI: https://github.com/crewAIInc/crewAI
- Bible Data: https://github.com/scrollmapper/bible_databases
- Anthropic Claude: https://www.anthropic.com/
