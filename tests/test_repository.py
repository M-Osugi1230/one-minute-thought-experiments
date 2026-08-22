from thought_pipeline.repository import ProjectRepository


def test_all_repository_configuration_is_valid() -> None:
    repository = ProjectRepository()
    experiments = repository.validate_all()

    assert [experiment.id for experiment in experiments] == ["001"]
    assert experiments[0].slug == "trolley_problem"
    assert repository.video().canvas.width == 1080


def test_prompt_contains_fact_pack_and_brand_rules() -> None:
    from thought_pipeline.core import Pipeline

    prompt = Pipeline(ProjectRepository()).prompt("1")

    assert "トロッコ問題" in prompt.user
    assert "思考実験名から始めない" in prompt.user
    assert "Fact Pack" in prompt.user
