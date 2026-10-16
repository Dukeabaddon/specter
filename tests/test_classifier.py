import pytest
from src.classifier.suspension import SuspensionClassifier

def test_walang_pasok_basic():
    text = "WALANG PASOK: Sa utos ni Mayor Joy Belmonte, suspendido ang klase sa lahat ng antas bukas dahil sa Bagyong Enteng."
    res = SuspensionClassifier.classify(text)
    assert res["is_suspension"] is True
    assert res["confidence"] >= 0.8
    assert "all_levels" in res["levels"]
    assert "typhoon" in res["reasons"]

def test_heat_index_suspension():
    text = "ADVISORY: Dahil sa matinding init at heat index, kanselado ang face-to-face classes sa pre-school at elementary."
    res = SuspensionClassifier.classify(text)
    assert res["is_suspension"] is True
    assert "heat_index" in res["reasons"]
    assert "pre_school_to_shs" in res["levels"]

def test_non_suspension_post():
    text = "Libreng bakuna para sa mga alagang aso at pusa, gaganapin sa QC Hall ngayong Biyernes."
    res = SuspensionClassifier.classify(text)
    assert res["is_suspension"] is False
    assert res["confidence"] == 0.0

def test_empty_text():
    res = SuspensionClassifier.classify("")
    assert res["is_suspension"] is False
