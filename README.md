# Development Setup
Run the following to spin up a development environment
```bash
./startDev.sh
```

# Running the dev bot
Within the development environment created above, run
```bash
python run.py
```

# Tests
Within the development environment created above, run
```bash
pytest --cov --cov-report=html:coverage
```