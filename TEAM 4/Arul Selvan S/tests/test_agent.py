import asyncio

from bmw_analyst.security.sql_validator import validate_sql


def ask(self, question: str) -> dict:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    intent = self.intent_router.route(question)

    sql = self.sql_generator.generate(question)

    if not validate_sql(sql):
        raise ValueError("Generated SQL failed security validation.")

    tool_response = asyncio.run(
        self.mcp_client.execute_approved_query(sql)
    )

    if not tool_response.success:
        raise ValueError(
            tool_response.error
            or "MCP query execution failed."
        )

    data = tool_response.data

    answer = self.generate_narrative(
        question=question,
        sql=sql,
        data=data,
    )

    return {
        "question": question,
        "intent": intent.value,
        "sql": sql,
        "data": data,
        "answer": answer,
    }