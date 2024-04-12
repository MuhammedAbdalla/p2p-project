import client


def test_login():
    c1 = client.Client()
    assert c1.__login__("TestBad", "TestPass") == False

    c2 = client.Client("TestGood", "TestPass")
    assert c2.__login__("TestGood", "TestPass") == True

