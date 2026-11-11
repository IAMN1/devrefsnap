from sqlalchemy.orm import Session

from demo_models import new_engine
from demo_queries import query_report, seed


def test_query_results():
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
            report = query_report(session)
            assert report["adults"] == ["alice"]
            assert report["joined"] == [("alice", "Python"), ("alice", "SQL")]
            assert report["outer"] == [("alice", "Python"), ("alice", "SQL"), ("bob", None)]
            assert report["managers"] == [("bob", "alice")]
            assert report["counts"] == [("alice", 2), ("bob", 0)]
            assert report["cte"] == report["union"] == ["alice", "bob"]
            assert report["commented"] == report["from_subquery"] == report["exists"] == ["alice"]
            assert report["age_group"] == [("alice", "adult"), ("bob", "minor")]
            assert report["groups"] == [(True, 2, 23.5)]
    finally:
        engine.dispose()
