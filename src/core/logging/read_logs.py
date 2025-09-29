import re
import pandas as pd
from datetime import datetime

pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

def parse_logs_grouped(log_file):
    log_pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| INFO \| .* \| \[(?P<event>start|fisnish)\](?P<agents>(?:\[[^\]]+\])+)"
    )

    events = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = log_pattern.search(line)
            if match:
                ts = datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S")
                event = match.group("event")
                agents = match.group("agents").replace("][", ".").strip("[]")
                events.append((ts, event, agents))

    active = {}
    records = []

    for ts, event, agents in events:
        key = agents
        if event == "start":
            active[key] = ts
        elif event == "fisnish":
            if key in active:
                duration = (ts - active[key]).total_seconds()
                records.append({
                    "agent_full": key,
                    "start": active[key],
                    "finish": ts,
                    "duration_sec": duration
                })
                del active[key]

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df[["agent", "subagent"]] = df["agent_full"].str.split(".", n=1, expand=True)
    df["subagent"] = df["subagent"].fillna("")

    agent_order = ["router", "route_request", "product", "orders",
                   "filter_check", "filter_condition", "fuzz_filter",
                   "query_generation", "query_validation", "execute_sql", "final_response"]
    df["agent_rank"] = df["agent"].apply(lambda x: agent_order.index(x) if x in agent_order else 9999)

    subagent_order = [
        "", "sq_node", "solve_subquestion", "agent_subquestion",
        "column_node", "solve_column_selection", "agent_column_selection"
    ]
    df["sub_rank"] = df["subagent"].apply(lambda x: subagent_order.index(x) if x in subagent_order else 9999)

    df = df.sort_values(by=["agent_rank", "start", "sub_rank"]).reset_index(drop=True)

    # 🔹 mostrar solo la hora en start y finish
    df["start"] = df["start"].dt.strftime("%H:%M:%S")
    df["finish"] = df["finish"].dt.strftime("%H:%M:%S")

    df = df[["agent", "subagent", "start", "finish", "duration_sec"]]

    return df

# Ejemplo de uso
log_file = r"D:\Datos\IA\FIUBA\MIA\PF\AIGE\logs\aige.log"
df = parse_logs_grouped(log_file)
print(df.to_string(index=False, justify="left"))
