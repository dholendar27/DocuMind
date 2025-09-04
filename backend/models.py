from app import db
from uuid import uuid4


class Files(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    file_name = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    uploaded = db.Column(db.Boolean, default=False)
    processed = db.Column(db.Boolean, default=False)
    chunked = db.Column(db.Boolean, default=False)
    filepath = db.Column(db.String(300))
    extracted_filepath = db.Column(db.String(300))

    def to_dict(self):
        return {
        "id": self.id,
        "file_name": self.file_name,
        "file_type": self.file_type,
        "uploaded": self.uploaded,
        "processed": self.processed,
        "chunked": self.chunked,
        "filepath": self.filepath,
        "extracted_filepath": self.extracted_filepath,
    }
