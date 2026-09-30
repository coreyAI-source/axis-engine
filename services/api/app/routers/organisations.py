from ._base import make_crud_router
from ..models.org import Organisation
from ..schemas.org import OrganisationCreate, OrganisationUpdate, OrganisationOut

router = make_crud_router(
    prefix="/organisations",
    tag="organisations",
    model=Organisation,
    create_schema=OrganisationCreate,
    update_schema=OrganisationUpdate,
    out_schema=OrganisationOut,
)
