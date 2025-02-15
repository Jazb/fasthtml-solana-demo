 # tests/conftest.py
  import pytest
  from fasthtml.testclient import TestClient
  from main import app

  @pytest.fixture
  def client():
      return TestClient(app)

  # static/app.js
  document.addEventListener('htmx:beforeRequest', (e) => {
      e.detail.elt.classList.add('loading');
  });

  document.addEventListener('htmx:afterRequest', (e) => {
      e.detail.elt.classList.remove('loading');
  });
