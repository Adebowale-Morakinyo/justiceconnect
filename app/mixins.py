from datetime import datetime
from sqlalchemy import event


class ReferenceGenerationMixin:
    """Mixin to auto-generate a reference after insert using the row's ID"""

    reference_prefix = "REF"  # Override in subclass if needed

    @classmethod
    def __declare_last__(cls):
        """Hook after model is fully declared."""

        @event.listens_for(cls, "after_insert")
        def _generate_reference(mapper, connection, target):
            if not target.reference:
                ref = f"{target.reference_prefix}-{datetime.now().strftime('%Y%m%d')}-{target.id:04d}"
                connection.execute(
                    cls.__table__.update()
                    .where(cls.id == target.id)
                    .values(reference=ref)
                )

    __abstract__ = True
