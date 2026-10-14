class MovieDataError(Exception):
    def __init__(self, status_code: int = 502):
        self.status_code = status_code
        self.detail = (
            "Movie data request timed out" if status_code == 504
            else "Movie data is temporarily unavailable"
        )
        super().__init__(self.detail)
