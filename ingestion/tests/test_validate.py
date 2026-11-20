from datetime import date

import yaml

import ing_synthetic as syn
from legal_ingestion.sources import load_sources


def _setup(tmp_path, mutate=None, *, create_file=True):
    legal = tmp_path / "legal"
    legal.mkdir()
    rel = syn.write_source(legal, "TDOC", "ru", "2024-01-01") if create_file else "raw/TDOC_ru_2024-01-01.html"
    doc = syn.document_entry("TDOC", [syn.version_entry("TDOC", "ru", "2024-01-01", rel)])
    if mutate:
        mutate(doc)
    path = syn.write_sources_yaml(legal, [doc])
    return legal, path


def test_valid(tmp_path):
    legal, path = _setup(tmp_path)
    sources, errors = load_sources(path, legal)
    assert errors == [] and sources is not None
    assert sources.documents[0].versions[0].effective_from == date(2024, 1, 1)


def test_missing_file(tmp_path):
    legal, path = _setup(tmp_path, create_file=False)
    _, errors = load_sources(path, legal)
    assert any("не найден" in e and "TDOC_ru_2024-01-01.html" in e for e in errors)


def test_bad_filename_language_and_date(tmp_path):
    def mutate(doc):
        v = doc["versions"][0]
        v["language"] = "uz-Latn"  # файл назван _ru_
        v["effective_from"] = date(2025, 5, 5)

    legal, path = _setup(tmp_path, mutate)
    _, errors = load_sources(path, legal)
    text = "\n".join(errors)
    assert "язык 'ru' не совпадает" in text
    assert "дата 2024-01-01 не совпадает" in text


def test_filename_pattern(tmp_path):
    def mutate(doc):
        (tmp_path / "legal" / "raw" / "random.html").write_text("<p>x</p>", encoding="utf-8")
        doc["versions"][0]["file"] = "raw/random.html"

    legal, path = _setup(tmp_path, mutate)
    _, errors = load_sources(path, legal)
    assert any("не соответствует" in e for e in errors)


def test_required_fields_types_and_enums(tmp_path):
    def mutate(doc):
        doc["document_type"] = "treaty"
        del doc["source_url"]
        doc["versions"][0]["language"] = "de"
        doc["versions"][0]["effective_from"] = "<дата с lex.uz>"
        doc["title"] = {}

    legal, path = _setup(tmp_path, mutate)
    sources, errors = load_sources(path, legal)
    assert sources is None
    text = "\n".join(errors)
    assert "documents[0].document_type" in text
    assert "documents[0].source_url" in text and "Field required" in text
    assert "documents[0].versions[0].language" in text
    assert "documents[0].versions[0].effective_from" in text
    assert "documents[0].title" in text


def test_broken_yaml_and_missing_sources(tmp_path):
    p = tmp_path / "sources.yaml"
    p.write_text("documents: [unclosed", encoding="utf-8")
    assert "некорректный YAML" in load_sources(p, tmp_path)[1][0]
    assert "не найден" in load_sources(tmp_path / "nope.yaml", tmp_path)[1][0]
    p.write_text(yaml.safe_dump(["x"]), encoding="utf-8")
    assert "словарь" in load_sources(p, tmp_path)[1][0]


def test_duplicate_key(tmp_path):
    legal, path = _setup(tmp_path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["documents"].append(data["documents"][0])
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    _, errors = load_sources(path, legal)
    assert any("повторяющийся document_key" in e for e in errors)
