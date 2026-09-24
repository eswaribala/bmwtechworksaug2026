import asyncio
import json
import logging

import ollama

from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

from bmw_analyst.security.sql_validator import (
    validate_sql,
)

from bmw_analyst.security.logging_config import (
    logger,
)

from bmw_analyst.mcp_client.client import (
    MCPClient,
)

from .prompts import (
    NARRATIVE_PROMPT,
)

from .router import (
    IntentRouter,
)

from .sql_generator import (
    SQLGenerator,
)


class BMWAnalystAgent:
    """
    BMW Natural Language Analyst.

    LLM:
        Ollama / Qwen 2.5 7B

    Database:
        Snowflake

    Database access:
        MCP

    Security:
        SQL validation before execution
    """

    def __init__(self):

        self.sql_generator = SQLGenerator()

        self.mcp_client = MCPClient()

        self.intent_router = IntentRouter()

        self.client = ollama.Client(
            host=OLLAMA_BASE_URL
        )

        self.model = OLLAMA_MODEL

        logger.info(
            "BMWAnalystAgent initialized "
            "with Ollama model=%s",
            self.model,
        )

    # -------------------------------------------------
    # Narrative Generation
    # -------------------------------------------------

    def generate_narrative(
        self,
        question: str,
        sql: str,
        data: list[dict],
    ) -> str:
        """
        Generate a natural-language answer
        from the user's question and Snowflake result.
        """

        logger.info(
            "Generating narrative response"
        )

        prompt = f"""
User question:
{question}

SQL:
{sql}

Query result:
{json.dumps(data, default=str)}

{NARRATIVE_PROMPT}
"""

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0.2,
            },
        )

        answer = (
            response["message"]["content"]
            .strip()
        )

        logger.info(
            "Narrative response generated successfully"
        )

        return answer

    # -------------------------------------------------
    # Main Question Flow
    # -------------------------------------------------

    def ask(
        self,
        question: str,
    ) -> dict:
        """
        Complete BMW analyst flow:

        Question
            ↓
        Intent Router
            ↓
        Qwen SQL Generation
            ↓
        SQL Validation
            ↓
        MCP
            ↓
        Snowflake
            ↓
        Qwen Narrative
        """

        # -------------------------------------------------
        # Validate question
        # -------------------------------------------------

        if not question or not question.strip():

            logger.warning(
                "Empty question received"
            )

            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        logger.info(
            "Analyst question received length=%s",
            len(question),
        )

        # -------------------------------------------------
        # Detect intent
        # -------------------------------------------------

        intent = self.intent_router.route(
            question
        )

        logger.info(
            "Intent detected intent=%s",
            intent.value,
        )

        # -------------------------------------------------
        # Generate SQL using Qwen
        # -------------------------------------------------

        sql = self.sql_generator.generate(
            question
        )

        logger.info(
            "SQL generated successfully"
        )

        # -------------------------------------------------
        # Security validation
        # -------------------------------------------------

        if not validate_sql(sql):

            logger.warning(
                "Generated SQL failed security validation"
            )

            raise ValueError(
                "Generated SQL failed security validation."
            )

        logger.info(
            "Generated SQL passed security validation"
        )

        # -------------------------------------------------
        # Execute through MCP
        # -------------------------------------------------

        tool_response = asyncio.run(
            self.mcp_client.execute_approved_query(
                sql
            )
        )

        if not tool_response.success:

            logger.error(
                "MCP query execution failed error=%s",
                tool_response.error,
            )

            raise ValueError(
                tool_response.error
                or "MCP query execution failed."
            )

        data = tool_response.data

        logger.info(
            "MCP query completed rows_returned=%s",
            len(data),
        )

        # -------------------------------------------------
        # Generate natural-language answer
        # -------------------------------------------------

        answer = self.generate_narrative(
            question=question,
            sql=sql,
            data=data,
        )

        logger.info(
            "Analyst request completed successfully"
        )

        # -------------------------------------------------
        # Return API response
        # -------------------------------------------------

        return {
            "question": question,
            "intent": intent.value,
            "sql": sql,
            "data": data,
            "answer": answer,
        }