from app.models.schema import AskRequest, CurrentResource, NextStepsQuery, QuizQuery, SearchQuery
from app.services import knowledge_base, rag_pipeline


def test_bundled_dataset_is_loaded():
    kb = knowledge_base.get_knowledge_base()

    assert len(kb.documents) > 2500
    assert kb.of_type("species")
    assert kb.of_type("hornbill")


def test_search_ranks_the_obvious_match_first():
    results = rag_pipeline.search_resources(
        SearchQuery(query="great indian bustard", limit=5)
    ).results

    assert results[0].title == "Ardeotis nigriceps (Great Indian Bustard)"
    assert results[0].bnhs_url.startswith("https://collections.bnhs.org/")
    assert 0 < results[0].similarity_score <= 1


def test_search_handles_plurals_and_common_class_names():
    titles = [
        r.title
        for r in rag_pipeline.search_resources(SearchQuery(query="vultures", limit=10)).results
    ]

    assert any("Vulture" in title for title in titles)


def test_search_with_no_meaningful_terms_returns_nothing():
    assert rag_pipeline.search_resources(SearchQuery(query="the and of", limit=5)).results == []


def test_archive_quiz_produces_valid_questions_without_an_llm():
    quiz = rag_pipeline.get_quiz(QuizQuery(topic="vultures", num_questions=5))

    assert len(quiz.questions) == 5
    for question in quiz.questions:
        assert len(question.options) == 4
        assert len(set(question.options)) == 4
        assert 0 <= question.correct_answer < 4
        assert question.explanation


def test_archive_quiz_is_deterministic_for_a_seed():
    first = rag_pipeline.build_archive_quiz("tigers", 3, seed="fixed")
    second = rag_pipeline.build_archive_quiz("tigers", 3, seed="fixed")

    assert [q.question for q in first.questions] == [q.question for q in second.questions]


def test_next_steps_fallback_returns_four_linked_actions():
    response = rag_pipeline.get_next_steps(
        NextStepsQuery(current_resource=CurrentResource(title="vulture conservation"))
    )

    assert len(response.actions) == 4
    assert all(action.direct_link for action in response.actions)


def test_ask_falls_back_to_archive_answer_with_sources():
    response = rag_pipeline.ask(AskRequest(question="Tell me about the Great Indian Bustard"))

    assert response.generated_by == "archive"
    assert "Great Indian Bustard" in response.answer
    assert response.sources and response.sources[0].url


def test_llm_links_are_restricted_to_known_destinations():
    allowed = {"https://collections.bnhs.org/s/specimen/item/1"}

    assert (
        rag_pipeline._clean_link("https://www.bnhs.org/explore-communities", "Contribute", allowed)
        == "/explore-communities"
    )
    assert (
        rag_pipeline._clean_link("https://collections.bnhs.org/s/specimen/item/1", "Learn", allowed)
        in allowed
    )
    assert (
        rag_pipeline._clean_link("https://made-up.example/page", "Advocate", allowed)
        == "https://www.bnhs.org/membership-form"
    )
    assert rag_pipeline._clean_link(None, "Take a quiz", allowed) == "/chatbot"
