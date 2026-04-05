"""
Documents API - Upload and parse documents
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from uuid import uuid4
from datetime import datetime

from services import get_document_parser, get_audit_logger, get_tenant_manager

router = APIRouter()


# In-memory storage (use database in production)
documents_store = {}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Form(default="tenant_demo"),
    document_type: str = Form(default="brd")
):
    """
    Upload a document for parsing.

    Supported types: PDF, TXT, DOCX
    Document types: brd, sow, api_spec
    """
    # Validate tenant
    tenant_manager = get_tenant_manager()
    if not tenant_manager.validate_tenant(tenant_id):
        raise HTTPException(
            status_code=403, detail="Invalid or inactive tenant")

    # Parse document
    parser = get_document_parser()

    try:
        content = await file.read()
        raw_text, metadata = await parser.parse(
            content,
            file.filename,
            file.content_type
        )

        # Generate document ID
        doc_id = str(uuid4())

        # Store document
        document = {
            "id": doc_id,
            "tenant_id": tenant_id,
            "name": file.filename,
            "document_type": document_type,
            "raw_text": raw_text,
            "metadata": metadata,
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat()
        }
        documents_store[doc_id] = document

        # Audit log
        audit = get_audit_logger()
        audit.log(
            tenant_id=tenant_id,
            action="upload",
            resource_type="document",
            resource_id=doc_id,
            actor="api_user",
            details={"filename": file.filename, "type": document_type}
        )

        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "metadata": metadata,
            "preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Document parsing failed: {str(e)}")


@router.get("/documents/{document_id}")
async def get_document(document_id: str, tenant_id: str = "tenant_demo"):
    """Get document by ID."""
    document = documents_store.get(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return document


@router.get("/documents")
async def list_documents(tenant_id: str = "tenant_demo"):
    """List all documents for a tenant."""
    docs = [
        {
            "id": doc["id"],
            "name": doc["name"],
            "document_type": doc["document_type"],
            "status": doc["status"],
            "created_at": doc["created_at"]
        }
        for doc in documents_store.values()
        if doc["tenant_id"] == tenant_id
    ]
    return {"documents": docs, "count": len(docs)}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, tenant_id: str = "tenant_demo"):
    """Delete a document."""
    document = documents_store.get(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    del documents_store[document_id]

    # Audit log
    audit = get_audit_logger()
    audit.log(
        tenant_id=tenant_id,
        action="delete",
        resource_type="document",
        resource_id=document_id,
        actor="api_user"
    )

    return {"success": True, "message": "Document deleted"}
