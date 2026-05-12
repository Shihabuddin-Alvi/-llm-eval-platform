from core.graders import exact_match, contains_match, regex_match

def test_exact_match_pass():
    result = exact_match("Paris", "paris")
    assert result["passed"] == True
    assert result["score"] == 1.0

def test_exact_match_fail():
    result = exact_match("London", "paris")
    assert result["passed"] == False
    assert result["score"] == 0.0

def test_contains_match_pass():
    result = contains_match("The capital is Paris", "paris")
    assert result["passed"] == True
    assert result["score"] == 1.0

def test_contains_match_fail():
    result = contains_match("The capital is London", "paris")
    assert result["passed"] == False
    assert result["score"] == 0.0

def test_regex_match_pass():
    result = regex_match("The answer is 42", r"\d+")
    assert result["passed"] == True
    assert result["score"] == 1.0

def test_regex_match_fail():
    result = regex_match("The answer is yes", r"\d+")
    assert result["passed"] == False
    assert result["score"] == 0.0
