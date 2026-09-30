from ._base import make_crud_router
from ..models.mapping import ProcessClauseMap
from ..schemas.mapping import ProcessClauseMapCreate, ProcessClauseMapUpdate, ProcessClauseMapOut

router = make_crud_router(
    prefix="/process-clause-maps",
    tag="process-clause-maps",
    model=ProcessClauseMap,
    create_schema=ProcessClauseMapCreate,
    update_schema=ProcessClauseMapUpdate,
    out_schema=ProcessClauseMapOut,
    soft_delete_field=None,
)
