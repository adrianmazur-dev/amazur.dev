from litestar.dto import DataclassDTO, DTOConfig

from modules.health.domain.health import HealthStatus


class HealthStatusDTO(DataclassDTO[HealthStatus]):
    config = DTOConfig(include={"checks"})
