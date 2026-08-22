from thought_pipeline.models import GeneratedPackage
from thought_pipeline.providers import OfflineGoldenProvider
from thought_pipeline.quality import validate_generated_package
from thought_pipeline.repository import ProjectRepository


def _golden() -> tuple[ProjectRepository, GeneratedPackage]:
    repository = ProjectRepository()
    package = OfflineGoldenProvider(repository.root).generate(
        "001", object()  # The offline provider intentionally ignores the prompt.
    )
    return repository, package


def test_golden_sample_passes_editorial_validation() -> None:
    repository, package = _golden()
    report = validate_generated_package(
        package,
        repository.experiment("001"),
        repository.brand(),
    )

    assert report.is_valid
    assert package.planned_duration_seconds == 50.0


def test_duration_outside_range_fails() -> None:
    repository, package = _golden()
    scenes = list(package.scenes)
    scenes[0] = scenes[0].model_copy(update={"duration_seconds": 15.0})
    too_long = package.model_copy(update={"scenes": scenes})

    report = validate_generated_package(
        too_long,
        repository.experiment("001"),
        repository.brand(),
    )

    assert "duration_out_of_range" in {issue.code for issue in report.errors}


def test_title_in_hook_fails() -> None:
    repository, package = _golden()
    hooks = list(package.hook_options)
    hooks[0] = hooks[0].model_copy(
        update={"narration": "トロッコ問題で、あなたはどうしますか？"}
    )
    invalid = package.model_copy(update={"hook_options": hooks})

    report = validate_generated_package(
        invalid,
        repository.experiment("001"),
        repository.brand(),
    )

    assert "title_in_hook" in {issue.code for issue in report.errors}
