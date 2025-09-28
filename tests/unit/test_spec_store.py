from time import perf_counter
from src.services.spec_store import SpecStore


def setup_module(module):
    # reset state for isolation
    SpecStore.state.requests.clear()
    SpecStore.state.boards.clear()
    SpecStore.state.board_by_request.clear()
    SpecStore.state.concepts_by_board.clear()


def test_create_and_get_request():
    item = SpecStore.create_request({
        "projectId": "p1",
        "title": "t",
        "description": "d",
        "tags": [],
        "references": []
    })
    rid = item["id"]
    got = SpecStore.get_request(rid)
    assert got and got["id"] == rid


def test_pagination_perf_under_threshold():
    # seed many items
    for i in range(0, 300):
        SpecStore.create_request({
            "projectId": f"p{i%3}",
            "title": f"t{i}",
            "description": "d",
        })
    start = perf_counter()
    items, next_cursor = SpecStore.list_requests(project_id=None, status=None, limit=200, cursor=None)
    elapsed_ms = (perf_counter() - start) * 1000
    assert len(items) <= 200
    # threshold ~500ms per requirement
    assert elapsed_ms < 500
