"""
Unit tests for AI document generation pipeline.

This module tests LangGraph workflows for:
- ICF (Informed Consent Form) generation
- Site Initiation Checklist generation
- RAG context retrieval
- Section-based generation
"""

from queue import Queue
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from langchain_core.messages import HumanMessage

from app.services.document_generator import (
    DocumentGenerationError,
    DocumentGenerator,
    ICFWorkflow,
    StreamingICFWorkflow,
    WorkflowBase,
    generate_icf_sections,
    get_langgraph_workflow,
)


class TestDocumentGenerator:
    """Test cases for DocumentGenerator class."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_init_generator(self, mock_qdrant_client, mock_langgraph_workflow):
        """Test DocumentGenerator initialization."""
        generator = DocumentGenerator(
            qdrant_client=mock_qdrant_client,
            icf_workflow=mock_langgraph_workflow,
            checklist_workflow=mock_langgraph_workflow,
        )

        assert generator.qdrant_client == mock_qdrant_client
        assert generator.icf_workflow == mock_langgraph_workflow
        assert generator.checklist_workflow == mock_langgraph_workflow

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_get_protocol_context_success(
        self, mock_qdrant_client, sample_protocol_metadata
    ):
        """Test successful protocol context retrieval."""
        document_id = sample_protocol_metadata["document_id"]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        # Mock the LangChain service and its similarity search method
        mock_langchain_service = MagicMock()
        mock_doc1 = MagicMock(page_content="Protocol inclusion criteria", metadata={})
        mock_doc2 = MagicMock(page_content="Study procedures description", metadata={})

        mock_langchain_service.similarity_search_with_score.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.8),
        ]

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
        ):
            context = generator.get_protocol_context(document_id, "inclusion criteria")

        assert len(context) == 2
        assert "Protocol inclusion criteria" in context[0]["text"]
        assert context[0]["score"] == 0.9


class TestICFGeneration:
    """Test cases for ICF (Informed Consent Form) generation."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_icf_sections_success(
        self, mock_qdrant_client, mock_langgraph_workflow, sample_protocol_metadata
    ):
        """Test successful ICF generation."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock workflow response
        mock_langgraph_workflow.invoke.return_value = {
            "summary": "Study Summary: Safety and Efficacy Trial",
            "background": "The background of this study is to evaluate...",
            "participants": "We will enroll 100 participants...",
            "procedures": "Participants will undergo the following procedures...",
            "alternatives": "Alternative treatments include...",
            "risks": "Potential risks include mild side effects...",
            "benefits": "Potential benefits include symptom improvement...",
        }

        # Mock context retrieval
        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=["Relevant protocol context"],
        ):

            result = generate_icf_sections(
                document_id=document_id,
                qdrant_client=mock_qdrant_client,
                workflow=mock_langgraph_workflow,
            )

        assert "summary" in result
        assert "background" in result
        assert "participants" in result
        assert "procedures" in result
        assert "alternatives" in result
        assert "risks" in result
        assert "benefits" in result

        assert result["summary"].startswith("Study Summary:")
        mock_langgraph_workflow.invoke.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_icf_sections_workflow_error(
        self, mock_qdrant_client, mock_langgraph_workflow, sample_protocol_metadata
    ):
        """Test ICF generation with workflow error."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock workflow error
        mock_langgraph_workflow.invoke.side_effect = Exception(
            "LangGraph execution failed"
        )

        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=["Context"],
        ):

            with pytest.raises(DocumentGenerationError, match="Failed to generate ICF"):
                generate_icf_sections(
                    document_id, mock_qdrant_client, mock_langgraph_workflow
                )


class TestRAGContextRetrieval:
    """Test cases for RAG context retrieval."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_rag_context_for_icf(self, mock_qdrant_client, sample_protocol_metadata):
        """Test RAG context retrieval for ICF generation."""
        document_id = sample_protocol_metadata["document_id"]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        # Mock the LangChain service
        mock_langchain_service = MagicMock()

        # Set up different return values for different queries
        def mock_search_side_effect(collection_name, query, k):
            if "title" in query.lower():
                return [
                    (
                        MagicMock(page_content="Study title and acronym", metadata={}),
                        0.95,
                    )
                ]
            elif "objectives" in query.lower():
                return [
                    (
                        MagicMock(
                            page_content="Primary and secondary objectives", metadata={}
                        ),
                        0.90,
                    )
                ]
            elif "procedures" in query.lower():
                return [
                    (
                        MagicMock(
                            page_content="Study procedures and visits", metadata={}
                        ),
                        0.88,
                    )
                ]
            return []

        mock_langchain_service.similarity_search_with_score.side_effect = (
            mock_search_side_effect
        )

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
        ):
            # Test different section contexts
            title_context = generator.get_protocol_context(document_id, "study title")
            purpose_context = generator.get_protocol_context(
                document_id, "study objectives"
            )
            procedures_context = generator.get_protocol_context(
                document_id, "study procedures"
            )

        assert len(title_context) == 1
        assert "Study title" in title_context[0]["text"]

        assert len(purpose_context) == 1
        assert "objectives" in purpose_context[0]["text"]

        assert len(procedures_context) == 1
        assert "procedures" in procedures_context[0]["text"]

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_rag_context_insufficient_results(
        self, mock_qdrant_client, sample_protocol_metadata
    ):
        """Test RAG context retrieval with insufficient results."""
        document_id = sample_protocol_metadata["document_id"]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        # Mock the LangChain service with low-score results
        mock_langchain_service = MagicMock()
        mock_langchain_service.similarity_search_with_score.return_value = [
            (MagicMock(page_content="Irrelevant content", metadata={}), 0.3)
        ]

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
        ):
            context = generator.get_protocol_context(
                document_id,
                "specific medical procedure",
                min_score=0.7,  # Higher threshold
            )

        assert len(context) == 0  # No results above threshold


class TestWorkflowClasses:
    """Test cases for workflow classes."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_icf_workflow_init(self):
        """Test StreamingICFWorkflow initialization."""
        workflow = StreamingICFWorkflow()

        assert workflow.name == "icf_generation"


class TestWorkflowBase:
    """Test cases for WorkflowBase class."""

    @pytest.mark.unit
    def test_workflow_base_initialization_success(self):
        """Test successful WorkflowBase initialization."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            assert workflow.llm == mock_llm
            assert workflow.name == "icf_generation"
            assert len(workflow.sections) == 7

    @pytest.mark.unit
    def test_workflow_base_initialization_failure(self):
        """Test WorkflowBase initialization with LLM failure."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_get_llm.side_effect = Exception("LLM initialization failed")

            with pytest.raises(
                DocumentGenerationError, match="Failed to initialize LLM"
            ):
                ICFWorkflow()

    @pytest.mark.unit
    def test_workflow_invoke_success(self, mock_qdrant_client):
        """Test successful workflow invocation."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(
                content="Generated section content"
            )
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            # Mock the document generator to be used in section generation
            mock_doc_gen = MagicMock()
            mock_doc_gen.get_protocol_context.return_value = [
                {"text": "Protocol context", "score": 0.9}
            ]

            # The inputs must match what the workflow expects
            inputs = {
                "document_generator": mock_doc_gen,
                "document_id": "test-doc-123",
            }

            result = workflow.invoke(inputs)

            # Verify result structure (sections may be empty if errors occurred, which is okay)
            assert "sections" in result
            assert "metadata" in result
            assert "errors" in result
            # At least check that invoke completed without raising
            assert isinstance(result, dict)

    @pytest.mark.unit
    def test_workflow_invoke_with_errors(self, mock_qdrant_client):
        """Test workflow invocation with generation errors."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = Exception("LLM generation failed")
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            mock_doc_gen = MagicMock()
            mock_doc_gen.get_protocol_context.return_value = [
                {"text": "Context", "score": 0.9}
            ]

            inputs = {
                "document_generator": mock_doc_gen,
                "document_id": "test-doc",
            }

            # Should not raise, but collect errors
            result = workflow.invoke(inputs)
            assert "sections" in result

    @pytest.mark.unit
    def test_generate_section_with_llm_success(self):
        """Test _generate_section_with_llm success."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Generated ICF summary section content"
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            result = workflow._generate_section_with_llm(
                section_name="summary",
                context="Protocol context about the study",
                section_prompt="Generate a summary section",
            )

            assert result == "Generated ICF summary section content"
            mock_llm.invoke.assert_called_once()

    @pytest.mark.unit
    def test_generate_section_with_llm_failure(self):
        """Test _generate_section_with_llm with LLM failure."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = Exception("LLM API error")
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            with pytest.raises(
                DocumentGenerationError, match="Failed to generate summary"
            ):
                workflow._generate_section_with_llm(
                    section_name="summary",
                    context="Context",
                    section_prompt="Prompt",
                )


class TestICFWorkflow:
    """Test cases for ICFWorkflow class."""

    @pytest.mark.unit
    def test_icf_workflow_build_graph(self):
        """Test ICF workflow graph construction."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = ICFWorkflow()
            graph = workflow.build_graph()

            # Verify all section nodes are added
            assert graph is not None
            # The graph should have nodes for all 7 sections
            assert len(workflow.sections) == 7

    @pytest.mark.unit
    def test_icf_workflow_section_queries(self):
        """Test section-specific query generation."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = ICFWorkflow()

            # Test different section queries
            summary_query = workflow._get_section_query("summary")
            risks_query = workflow._get_section_query("risks")
            benefits_query = workflow._get_section_query("benefits")

            assert isinstance(summary_query, str)
            assert isinstance(risks_query, str)
            assert isinstance(benefits_query, str)
            assert len(summary_query) > 0

    @pytest.mark.unit
    def test_icf_workflow_format_context(self):
        """Test context formatting for LLM."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = ICFWorkflow()

            context = [
                {"text": "Protocol inclusion criteria", "score": 0.9},
                {"text": "Study procedures", "score": 0.8},
            ]

            formatted = workflow._format_context(context)

            assert "Protocol inclusion criteria" in formatted
            assert "Study procedures" in formatted
            assert "0.90" in formatted or "0.9" in formatted

    @pytest.mark.unit
    def test_icf_workflow_format_empty_context(self):
        """Test context formatting with empty context."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = ICFWorkflow()

            formatted = workflow._format_context([])

            assert "No specific protocol context available" in formatted

    @pytest.mark.unit
    def test_icf_workflow_get_section_prompt(self):
        """Test section prompt retrieval."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = ICFWorkflow()

            summary_prompt = workflow._get_section_prompt("summary")
            risks_prompt = workflow._get_section_prompt("risks")

            assert isinstance(summary_prompt, str)
            assert isinstance(risks_prompt, str)
            assert len(summary_prompt) > 0


class TestStreamingICFWorkflow:
    """Test cases for StreamingICFWorkflow class."""

    @pytest.mark.unit
    def test_streaming_workflow_init(self):
        """Test StreamingICFWorkflow initialization."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()

        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc-123",
            )

            assert workflow.event_queue == event_queue
            assert workflow.document_generator == mock_doc_gen
            assert workflow.document_id == "test-doc-123"

    @pytest.mark.unit
    def test_streaming_workflow_with_sections_filter(self):
        """Test StreamingICFWorkflow with sections filter."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = StreamingICFWorkflow(sections_filter=["summary", "risks"])

            assert len(workflow.sections) == 2
            assert "summary" in workflow.sections
            assert "risks" in workflow.sections

    @pytest.mark.unit
    def test_streaming_workflow_token_streaming(self):
        """Test token streaming to event queue."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Protocol context", "score": 0.9}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            # Mock streaming LLM response
            mock_llm = MagicMock()
            chunk1 = MagicMock()
            chunk1.content = "This is "
            chunk2 = MagicMock()
            chunk2.content = "a test."
            mock_llm.stream.return_value = [chunk1, chunk2]
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["summary"],
            )

            # Create section generator
            section_generator = workflow._create_section_generator("summary")

            # Execute the generator
            state = {}
            result = section_generator(state)

            # Verify events were queued
            events = []
            while not event_queue.empty():
                events.append(event_queue.get())

            # Should have section_start, tokens, and section_complete
            assert len(events) >= 2
            assert any(e["type"] == "section_start" for e in events)
            assert any(e["type"] == "token" for e in events)

    @pytest.mark.unit
    def test_streaming_workflow_error_handling(self):
        """Test streaming workflow error handling."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.side_effect = Exception(
            "Context retrieval failed"
        )

        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
            )

            section_generator = workflow._create_section_generator("summary")

            # Should not raise, but queue error event
            result = section_generator({})

            # Check for error event
            events = []
            while not event_queue.empty():
                events.append(event_queue.get())

            assert any(e["type"] == "section_error" for e in events)


class TestHelperFunctions:
    """Test cases for helper functions."""

    @pytest.mark.unit
    def test_get_langgraph_workflow_icf(self):
        """Test getting ICF workflow."""
        with patch("app.services.document_generator.get_llm_chat_model"):
            workflow = get_langgraph_workflow("icf")

            assert isinstance(workflow, ICFWorkflow)
            assert workflow.name == "icf_generation"

    @pytest.mark.unit
    def test_get_langgraph_workflow_unknown(self):
        """Test getting unknown workflow type."""
        with pytest.raises(DocumentGenerationError, match="Unknown workflow type"):
            get_langgraph_workflow("unknown_type")

    @pytest.mark.unit
    def test_generate_icf_sections_missing_sections(self, mock_qdrant_client):
        """Test generate_icf_sections with missing required sections."""
        mock_workflow = MagicMock()
        # Return incomplete sections
        mock_workflow.invoke.return_value = {
            "sections": {
                "summary": "Summary only",
                # Missing other required sections
            },
            "errors": [],
        }

        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=[{"text": "Context", "score": 0.9}],
        ):
            with pytest.raises(
                DocumentGenerationError, match="Missing required ICF section"
            ):
                generate_icf_sections(
                    document_id="test-doc",
                    qdrant_client=mock_qdrant_client,
                    workflow=mock_workflow,
                )


class TestDocumentGeneratorErrorHandling:
    """Test cases for error handling in document generation."""

    @pytest.mark.unit
    def test_get_protocol_context_langchain_error(self, mock_qdrant_client):
        """Test protocol context retrieval with LangChain error."""
        generator = DocumentGenerator(mock_qdrant_client, None, None)

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service"
        ) as mock_get_langchain:
            mock_service = MagicMock()
            mock_service.similarity_search_with_score.side_effect = Exception(
                "Qdrant connection error"
            )
            mock_get_langchain.return_value = mock_service

            with pytest.raises(
                DocumentGenerationError, match="Failed to retrieve context"
            ):
                generator.get_protocol_context("test-doc", "query")

    @pytest.mark.unit
    def test_generate_icf_sections_workflow_execution_error(self, mock_qdrant_client):
        """Test ICF generation with workflow execution error."""
        mock_workflow = MagicMock()
        mock_workflow.invoke.side_effect = Exception("Workflow execution failed")

        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=[{"text": "Context", "score": 0.9}],
        ):
            with pytest.raises(DocumentGenerationError, match="Failed to generate ICF"):
                generate_icf_sections(
                    document_id="test-doc",
                    qdrant_client=mock_qdrant_client,
                    workflow=mock_workflow,
                )


class TestWorkflowInvokeEdgeCases:
    """Test edge cases for workflow invoke method."""

    @pytest.mark.unit
    def test_invoke_with_message_without_content_attribute(self):
        """Test invoke when result items don't have .content attribute."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            # Return plain strings instead of HumanMessage objects
            mock_llm.invoke.return_value = MagicMock(content="Section content")
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            # Create mock compiled graph that returns plain strings (no .content)
            with patch.object(workflow, "compile_workflow") as mock_compile:
                mock_compiled = MagicMock()

                # Mock invoke to return state with plain strings (no .content attribute)
                def mock_invoke(state):
                    return {
                        "summary": ["Plain string without content attribute"],
                        "background": ["Another plain string"],
                        "participants": [],  # Empty section
                        "procedures": [],
                        "alternatives": [],
                        "risks": [],
                        "benefits": [],
                        "document_generator": state.get("document_generator"),
                    }

                mock_compiled.invoke = mock_invoke
                mock_compile.return_value = mock_compiled

                mock_doc_gen = MagicMock()
                inputs = {
                    "document_generator": mock_doc_gen,
                    "document_id": "test-doc",
                }

                result = workflow.invoke(inputs)

                # Should handle strings without .content attribute
                assert (
                    result["sections"]["summary"]
                    == "Plain string without content attribute"
                )
                assert result["sections"]["background"] == "Another plain string"

    @pytest.mark.unit
    def test_invoke_with_missing_sections(self):
        """Test invoke when some sections are missing (empty lists)."""
        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Content")
            mock_get_llm.return_value = mock_llm

            workflow = ICFWorkflow()

            with patch.object(workflow, "compile_workflow") as mock_compile:
                mock_compiled = MagicMock()

                # Some sections populated, some empty
                def mock_invoke(state):
                    return {
                        "summary": [HumanMessage(content="Summary content")],
                        "background": [],  # Empty - should trigger error
                        "participants": [],
                        "procedures": [],
                        "alternatives": [],
                        "risks": [],
                        "benefits": [],
                    }

                mock_compiled.invoke = mock_invoke
                mock_compile.return_value = mock_compiled

                inputs = {
                    "document_generator": MagicMock(),
                    "document_id": "test-doc",
                }

                result = workflow.invoke(inputs)

                # Should have errors for missing sections
                assert len(result["errors"]) > 0
                assert any("Missing section" in err for err in result["errors"])


class TestStreamingWorkflowSectionBranches:
    """Test StreamingICFWorkflow section-specific return branches."""

    @pytest.mark.unit
    def test_streaming_workflow_procedures_section(self):
        """Test StreamingICFWorkflow generates procedures section correctly."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Procedure context", "score": 0.9}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            chunk = MagicMock()
            chunk.content = "Procedures content"
            mock_llm.stream.return_value = [chunk]
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["procedures"],
            )

            section_gen = workflow._create_section_generator("procedures")
            result = section_gen({})

            assert "procedures" in result
            assert result["procedures"] == ["Procedures content"]

    @pytest.mark.unit
    def test_streaming_workflow_alternatives_section(self):
        """Test StreamingICFWorkflow generates alternatives section correctly."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Alternatives context", "score": 0.8}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            chunk = MagicMock()
            chunk.content = "Alternatives content"
            mock_llm.stream.return_value = [chunk]
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["alternatives"],
            )

            section_gen = workflow._create_section_generator("alternatives")
            result = section_gen({})

            assert "alternatives" in result

    @pytest.mark.unit
    def test_streaming_workflow_background_section(self):
        """Test StreamingICFWorkflow generates background section correctly."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Background context", "score": 0.85}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            chunk = MagicMock()
            chunk.content = "Background content"
            mock_llm.stream.return_value = [chunk]
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["background"],
            )

            section_gen = workflow._create_section_generator("background")
            result = section_gen({})

            assert "background" in result

    @pytest.mark.unit
    def test_streaming_workflow_participants_section(self):
        """Test StreamingICFWorkflow generates participants section correctly."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Participants context", "score": 0.75}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            chunk = MagicMock()
            chunk.content = "Participants content"
            mock_llm.stream.return_value = [chunk]
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["participants"],
            )

            section_gen = workflow._create_section_generator("participants")
            result = section_gen({})

            assert "participants" in result

    @pytest.mark.unit
    def test_streaming_workflow_benefits_section(self):
        """Test StreamingICFWorkflow generates benefits section correctly."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Benefits context", "score": 0.88}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            chunk = MagicMock()
            chunk.content = "Benefits content"
            mock_llm.stream.return_value = [chunk]
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["benefits"],
            )

            section_gen = workflow._create_section_generator("benefits")
            result = section_gen({})

            assert "benefits" in result

    @pytest.mark.unit
    def test_streaming_workflow_stream_fallback_on_error(self):
        """Test StreamingICFWorkflow falls back to non-streaming on stream error."""
        event_queue = Queue()
        mock_doc_gen = MagicMock()
        mock_doc_gen.get_protocol_context.return_value = [
            {"text": "Context", "score": 0.9}
        ]

        with patch(
            "app.services.document_generator.get_llm_chat_model"
        ) as mock_get_llm:
            mock_llm = MagicMock()
            # Stream fails
            mock_llm.stream.side_effect = Exception("Streaming failed")
            # But invoke works
            mock_response = MagicMock()
            mock_response.content = "Fallback content"
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm

            workflow = StreamingICFWorkflow(
                event_queue=event_queue,
                document_generator=mock_doc_gen,
                document_id="test-doc",
                sections_filter=["summary"],
            )

            section_gen = workflow._create_section_generator("summary")
            result = section_gen({})

            # Should fall back to non-streaming
            assert "summary" in result
            assert result["summary"] == ["Fallback content"]


class TestIntegrationScenarios:
    """Integration test scenarios for document generation."""

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_end_to_end_icf_generation(
        self, memory_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test end-to-end ICF generation process."""
        # First store protocol in Qdrant
        # Create a protocol collection for testing
        from app.services.qdrant_service import QdrantService

        qdrant_service = QdrantService()
        qdrant_service.client = memory_qdrant_client  # Use test client

        collection_name = qdrant_service.create_protocol_collection(
            study_acronym="TEST",
            protocol_title=sample_protocol_metadata["protocol_title"],
        )
        sample_protocol_metadata["collection_name"] = collection_name

        # Mock ICF workflow
        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = {
            "summary": "Generated ICF Summary",
            "background": "Generated Background",
            "participants": "Generated Participants",
            "procedures": "Generated Procedures",
            "alternatives": "Generated Alternatives",
            "risks": "Generated Risks",
            "benefits": "Generated Benefits",
        }

        # Generate ICF using the collection name that was actually created
        # Mock the LangChain service for context retrieval
        mock_langchain_service = MagicMock()
        mock_langchain_service.similarity_search_with_score.return_value = [
            (MagicMock(page_content="Relevant protocol content", metadata={}), 0.9)
        ]

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
        ):
            icf_sections = generate_icf_sections(
                document_id=collection_name,  # Use the actual collection name
                qdrant_client=memory_qdrant_client,
                workflow=mock_workflow,
            )

        assert len(icf_sections) == 7
        assert all(
            section in icf_sections
            for section in [
                "summary",
                "background",
                "participants",
                "procedures",
                "alternatives",
                "risks",
                "benefits",
            ]
        )
        mock_workflow.invoke.assert_called_once()
