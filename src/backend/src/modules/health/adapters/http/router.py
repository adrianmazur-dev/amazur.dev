from litestar import Router, get
from litestar.di import NamedDependency, Provide

from modules.health.adapters.http.dto import HealthStatusDTO
from modules.health.application.use_cases.check_health import CheckHealth
from modules.health.domain.health import HealthStatus


@get(path="/", status_code=200, return_dto=HealthStatusDTO)
async def readiness(check_health: NamedDependency[CheckHealth]) -> HealthStatus:
    return await check_health.execute()


def create_router(check_health: CheckHealth) -> Router:
    def provide_check_health() -> CheckHealth:
        return check_health

    return Router(
        path="/health",
        tags=["health"],
        route_handlers=[readiness],
        response_headers={"Cache-Control": "no-store"},
        dependencies={
            "check_health": Provide(
                provide_check_health,
                sync_to_thread=False,
            ),
        },
    )
