from ._base import make_crud_router
from ..models.org import Role
from ..schemas.org import RoleCreate, RoleOut

router = make_crud_router(
    prefix="/roles",
    tag="roles",
    model=Role,
    create_schema=RoleCreate,
    update_schema=RoleCreate,
    out_schema=RoleOut,
    soft_delete_field=None,
)
