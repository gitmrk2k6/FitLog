import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

settings = get_settings()


def _ensure_test_database() -> None:
    """テスト用 DB (fitlog_test) が無ければ作成する。"""
    admin_url = settings.database_url  # 既定の fitlog DB に接続して CREATE DATABASE
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    db_name = settings.test_database_url.rsplit("/", 1)[-1]
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": db_name}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    engine.dispose()


@pytest.fixture(scope="session")
def engine():
    _ensure_test_database()
    eng = create_engine(settings.test_database_url, pool_pre_ping=True)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    """外側トランザクション + SAVEPOINT でテストごとに完全ロールバック。"""
    connection = engine.connect()
    trans = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess: Session, transaction) -> None:
        if transaction.nested and not transaction._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    trans.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def common_exercises(db_session):
    """共通種目マスタ（テストDBはマイグレーションを通さないため明示投入）。"""
    from app.models.exercise import Exercise

    rows = [
        Exercise(name="ベンチプレス", category="chest"),
        Exercise(name="スクワット", category="legs"),
        Exercise(name="ランニング", category="cardio"),
    ]
    db_session.add_all(rows)
    db_session.commit()
    return rows


def _auth(client, username: str, email: str) -> dict[str, str]:
    client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": "pass1234"},
    )
    token = client.post(
        "/api/auth/login", json={"email": email, "password": "pass1234"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client):
    """登録+ログイン済みユーザーの Authorization ヘッダ。"""
    return _auth(client, "owner", "owner@example.com")


@pytest.fixture
def other_headers(client):
    """別ユーザー（本人限定チェック用）。"""
    return _auth(client, "intruder", "intruder@example.com")
