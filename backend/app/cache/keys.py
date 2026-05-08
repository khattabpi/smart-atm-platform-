"""Centralized cache key naming — prevents typos and collisions."""


class CacheKeys:
    # ATMs
    @staticmethod
    def atm_detail(atm_id: int) -> str:
        return f"atm:detail:{atm_id}"

    @staticmethod
    def atms_nearby(lat: float, lng: float, radius: float, working_only: bool, currency: str | None) -> str:
        return f"atms:nearby:{lat:.4f}:{lng:.4f}:{radius}:{int(working_only)}:{currency or 'all'}"

    # Profile
    @staticmethod
    def user_profile(user_id: int) -> str:
        return f"user:profile:{user_id}"

    # Recommendations
    @staticmethod
    def recommendation(user_id: int, lat: float, lng: float) -> str:
        return f"reco:{user_id}:{lat:.3f}:{lng:.3f}"

    # Rate limiting
    @staticmethod
    def rate_limit(identifier: str, bucket: str) -> str:
        return f"rl:{bucket}:{identifier}"

    # Patterns for invalidation
    ATMS_NEARBY_PATTERN = "atms:nearby:*"
    USER_PROFILE_PATTERN = "user:profile:*"