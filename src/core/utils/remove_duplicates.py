def remove_duplicates(f, valid_keys=None):
    """
    Elimina duplicados de los outputs de los agentes.
    f: dict con {agent_out: {...}}
    valid_keys: lista de keys de agentes a considerar (opcional)
    """
    s = set()
    final = []
    for k, v in f.items():
        if valid_keys is None or k in valid_keys:
            for item in v.get('column_extract', []):
                key = tuple(item)
                if key not in s:
                    final.append(item)
                    s.add(key)
    return final