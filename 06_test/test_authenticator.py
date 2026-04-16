import pytest
from authenticator import Authenticator

# register()メソッドで、ユーザーが正しく登録されるか
def test_register_success():
    auth = Authenticator()
    auth.register("test-user", "test-password")
    
    # 正しく登録されているか確認
    assert auth.users["test-user"] == "test-password"


# register()メソッドで、既に存在するユーザー名で登録を試みた場合に、エラーメッセージが出力されるか
def test_register_duplicate_user():
    auth = Authenticator()
    auth.register("test-user", "test-password")
    
    # 同じユーザーを再登録 → エラー確認
    # as eとしてエラーを表現できて、そのメッセージにアクセスできるらしい
    with pytest.raises(ValueError) as e:
        auth.register("test-user", "test-password")
    
    assert str(e.value) == "エラー: ユーザーは既に存在します。"


# login()メソッドで、正しいユーザー名とパスワードでログインできるか
def test_login_success():
    auth = Authenticator()
    auth.register("test-user", "test-password")
    
    result = auth.login("test-user", "test-password")
    
    assert result == "ログイン成功"


# login()メソッドで、誤ったパスワードでエラーが出るか
def test_login_wrong_password():
    auth = Authenticator()
    auth.register("test-user", "test-password")
    
    # as eとしてエラーを表現できて、そのメッセージにアクセスできるらしい
    with pytest.raises(ValueError) as e:
        auth.login("test-user", "wrong-password")
    
    assert str(e.value) == "エラー: ユーザー名またはパスワードが正しくありません。"