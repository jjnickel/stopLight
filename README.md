# AI Vision Stoplight Control System

An intelligent traffic light system using AI-based computer vision to analyze traffic flow and dynamically adjust light timing.

## Features

- AI vision detection of vehicles and pedestrians
- Real-time traffic flow analysis
- Dynamic light timing adjustment
- SQLite database for traffic pattern logging
- Inter-intersection communication
- Admin dashboard with monitoring and control

## Project Structure

```
stoplight/
├── ai_vision/           # AI vision module
├── traffic_analyzer/    # Traffic analysis logic
├── signal_controller/   # Traffic light control
├── database/           # Database models and operations
├── communication/      # Inter-intersection communication
├── admin_dashboard/    # Web dashboard
├── tests/             # Test suite
└── config/            # Configuration files
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

5. Start the system:
```bash
python main.py
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Lint code: `flake8`

## License

MIT License 