class SupportsIdentity:
    def identity(self, pipeline_id: str, highlight: str) -> int:
        return f"{pipeline_id}_{highlight}".__hash__()
