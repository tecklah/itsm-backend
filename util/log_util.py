from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
import traceback

def print_trace(messages):
    for i, m in enumerate(messages):
        if isinstance(m, HumanMessage):
            print("===== Human =====")
            print(m.content)
        elif isinstance(m, AIMessage):
            print("===== AI =====")
            if m.tool_calls:
                print("Tool Calls:")
                for tc in m.tool_calls:
                    print(f"  tool name: {tc['name']}")
                    print(f"  subagent_type: {tc['args'].get('subagent_type')}")
                    print("  subagent prompt/description:")
                    print(f"    {tc['args'].get('description')}")
        elif isinstance(m, ToolMessage):
            print("===== Tool =====")
            print(f"tool name: {m.name}")
            print("output:")
            print(m.content)

def print_message(message, db_connection=None):
    if isinstance(message, HumanMessage):
        print("===== Human =====")
        print(message.content)
        _log_to_db(db_connection, "Human", message.content)

    elif isinstance(message, AIMessage):
        print("===== AI =====")
        if message.tool_calls:
            print("Tool Calls:")
            log_lines = []
            for tc in message.tool_calls:
                name = tc.get("name")
                args = tc.get("args")
                print(f"  tool name: {name}")
                print(f"  args: {args}")
                log_lines.append(f"tool name: {name}, args: {args}")
            _log_to_db(db_connection, "AI", "\n".join(log_lines))
        else:
            print(message.content)
            _log_to_db(db_connection, "AI", message.content)

    elif isinstance(message, ToolMessage):
        print("===== Tool =====")
        print(f"tool name: {message.name}")
        print("output:")
        print(message.content)
        _log_to_db(db_connection, "Tool", f"{message.name}: {message.content}")
    else:
        print("===== Unknown Message Type =====")
        print(message)

def _log_to_db(db_connection, message_type, msg):
    if db_connection is None:
        print("DB connection not available, skipping log.")
        return
    try:
        cur = db_connection.cursor()
        try:
            cur.execute(
                "INSERT INTO agent_log (message_type, message) VALUES (%s, %s)",
                (message_type, str(msg)[:2000]),
            )
        finally:
            cur.close()
        db_connection.commit()
    except Exception as e:
        print("Failed to log message to database:", e)
        traceback.print_exc()
        pass