from ._base import make_crud_router
from ..models.org import Site
from ..schemas.org import SiteCreate, SiteUpdate, SiteOut

router = make_crud_router(
    prefix="/sites",
    tag="sites",
    model=Site,
    create_schema=SiteCreate,
    update_schema=SiteUpdate,
    out_schema=SiteOut,
)
