# Contributing to VanillaEDI

Thank you for considering constributing to VanillaEDI! We welcome bug reports, feature requests, documentation improvements, and pull requests.

---

## Development Workflow
### 1. Local Setup
Clone the respository and set up your virtual environment:

```bash
git clone https://github.com/VanillaStackLabs/vanilla-edi.git
cd vanilla-edi

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
**OR**

For a local containerized deployment:
```bash
docker build -t vanilla-edi .
docker run -p 8000:8000 vanilla-edi
```

---

### 2. Running Tests
VanillaEDI strives for 100% code coverage across al modules. Before submitting a pull request, verify that all unit, integration, and E2E tests pass with full coverage:
```bash
pytest --cov=. --cov-report=term-missing
```

---

### 3. Creating a Pull Request
1. Fork the respository and create your feature branch (`git checkout -b feature/amazing-new-feature`).
2. Write clean, readable code following PEP 8 guidelines.
3. Ensure all tests pass and coverage remains at 100%.
4. Commit your changes (`git commit -m "feat: add support for feature X`).
5. Push to your branch (`git push origin feature/amazing-new-feature`).
6. Open a Pull Request agains the `main` branch.

---

## Code Style & Conventions
* Use **Type Hints** on all function parameters and return types.
* Follow **Pydantic v2** conventions for schema definitions. 
* Keep route handlers inside `routers/` thin by delegating parsing and generation logic to dedicated modules in `parsers/` and `generators/`.
