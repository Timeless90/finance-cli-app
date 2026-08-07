from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app


def test_action_api_registers_simulates_prioritizes_reviews_and_tracks_benefits() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/api/v1/actions/register",
            json={
                "action_id": "A-100",
                "title": "Accelerate collections",
                "owner": "Treasury",
                "due_period": 2,
                "cost": "50",
                "confidence": "0.8",
                "status": "planned",
                "impacts": [
                    {
                        "period": 2,
                        "metric": "cash",
                        "amount": "500",
                        "impact_key": "collections:q2:cash",
                    },
                    {
                        "period": 2,
                        "metric": "covenant",
                        "amount": "0.2",
                        "impact_key": "collections:q2:leverage",
                        "covenant_id": "leverage",
                    },
                ],
            },
        )
        assert created.status_code == 200
        assert created.json()["action"]["action_id"] == "A-100"

        simulation = client.post(
            "/api/v1/actions/simulate",
            json={"action_ids": ["A-100"]},
        )
        assert simulation.status_code == 200
        assert simulation.json()["result"]["expected_cash_effect"] == "400.0"
        assert simulation.json()["result"]["covenant_effects"] == [["leverage", "0.16"]]

        priorities = client.post(
            "/api/v1/actions/portfolio/prioritize",
            json={"action_ids": ["A-100"]},
        )
        assert priorities.status_code == 200
        assert priorities.json()["priorities"][0]["action_id"] == "A-100"

        review = client.post(
            "/api/v1/actions/A-100/review",
            json={"current_period": 3},
        )
        assert review.status_code == 200
        assert review.json()["review"]["escalation"] == "warning"

        benefits = client.post(
            "/api/v1/actions/benefits/track",
            json={
                "observations": [
                    {
                        "action_id": "A-100",
                        "metric": "cash",
                        "period": 2,
                        "planned_amount": "400",
                        "realized_amount": "360",
                    }
                ]
            },
        )
        assert benefits.status_code == 200
        assert benefits.json()["results"][0]["variance"] == "-40"
        assert benefits.json()["results"][0]["realization_ratio"] == "0.9"
