import re
import logging

import ollama

from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

from .prompts import SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class SQLGenerator:
    """
    Generates read-only SQL using the local
    Ollama Qwen model.
    """

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL,
    ):
        self.model = model

        self.client = ollama.Client(
            host=base_url
        )

        logger.info(
            "SQLGenerator initialized model=%s",
            self.model,
        )

    def generate(self, question: str) -> str:
        """
        Generate SQL from a natural-language question.

        The generated SQL is NOT executed here.
        It must pass the SQL security validator
        before reaching Snowflake.
        """

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        logger.info(
            "Generating SQL with Ollama model=%s",
            self.model,
        )

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question.strip(),
                },
            ],
            options={
                "temperature": 0,
            },
        )

        sql = response["message"]["content"].strip()

        # -------------------------------------------------
        # Remove Markdown SQL fences
        # -------------------------------------------------

        sql = re.sub(
            r"^```(?:sql)?\s*",
            "",
            sql,
            flags=re.IGNORECASE,
        )

        sql = re.sub(
            r"\s*```$",
            "",
            sql,
        )

        # -------------------------------------------------
        # Fix common missing spaces
        # -------------------------------------------------

        sql = re.sub(
            r"\bFROM(?=\S)",
            "FROM ",
            sql,
            flags=re.IGNORECASE,
        )

        sql = re.sub(
            r"\bWHERE(?=\S)",
            "WHERE ",
            sql,
            flags=re.IGNORECASE,
        )

        sql = re.sub(
            r"\bGROUP\s+BY(?=\S)",
            "GROUP BY ",
            sql,
            flags=re.IGNORECASE,
        )

        sql = re.sub(
            r"\bORDER\s+BY(?=\S)",
            "ORDER BY ",
            sql,
            flags=re.IGNORECASE,
        )

        sql = sql.strip()

        logger.info(
            "SQL generated successfully"
        )

        return sql