from litestar.dto import DataclassDTO

from modules.linkedin.domain.profile import Certification, Education, Experience, LinkedInProfile


class LinkedInProfileDTO(DataclassDTO[LinkedInProfile]):
    pass


class ExperienceDTO(DataclassDTO[Experience]):
    pass


class EducationDTO(DataclassDTO[Education]):
    pass


class CertificationDTO(DataclassDTO[Certification]):
    pass
