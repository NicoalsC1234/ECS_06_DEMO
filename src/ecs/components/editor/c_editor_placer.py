class CEditorPlacer:
    def __init__(self, types:list[str]) -> None:
        self.types = types
        self.curr_type_idx = 0