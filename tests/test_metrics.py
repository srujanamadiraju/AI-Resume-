import pytest
from app.models.resume_converter.web_app import overlap_coefficient
import json

def test_overlap_coefficient_same_text():
    text1 = "This is a test sentence"
    text2 = "This is a test sentence"
    result = overlap_coefficient(text1, text2)
    assert result == 1.0

def test_overlap_coefficient_different_text():
    text1 = "This is a test sentence"
    text2 = "This is a completely different sentence"
    result = overlap_coefficient(text1, text2)
    assert 0.0 <= result <= 1.0
    assert result < 1.0

def test_overlap_coefficient_empty_text():
    text1 = ""
    text2 = "This is a test sentence"
    result = overlap_coefficient(text1, text2)
    assert result == 0.0

def test_overlap_coefficient_special_characters():
    text1 = "This is a test! sentence with @#$% special characters"
    text2 = "This is a test sentence with special characters"
    result = overlap_coefficient(text1, text2)
    assert 0.0 <= result <= 1.0

def test_overlap_coefficient_case_insensitive():
    text1 = "THIS IS A TEST SENTENCE"
    text2 = "this is a test sentence"
    result = overlap_coefficient(text1, text2)
    assert result == 1.0

def test_overlap_coefficient_json_input():
    data1 = {"key1": "value1", "key2": "value2"}
    data2 = {"key1": "value1", "key3": "value3"}
    result = overlap_coefficient(json.dumps(data1), json.dumps(data2))
    assert 0.0 <= result <= 1.0 