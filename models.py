from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PaginationMetadata(BaseModel):
    """Pagination metadata for API responses."""

    total_items: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class TableQueryParams(BaseModel):
    """Query parameters for table data endpoint."""

    schema_name: str = Field(..., description="PostgreSQL schema name")
    table_name: str = Field(..., description="Table name")
    district: Optional[str] = Field(None, description="Optional district filter")
    page: int = Field(1, description="Page number (1-based)", ge=1)
    page_size: int = Field(100, description="Number of items per page", ge=1, le=1000)


class ColumnInfo(BaseModel):
    """Column information from information_schema."""

    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Data type")
    nullable: bool = Field(..., description="Whether the column is nullable")


class TableDataResponse(BaseModel):
    """Response model for table data endpoint."""

    data: List[Dict[str, Any]] = Field(..., description="Table data rows")
    columns: List[ColumnInfo] = Field(..., description="Column information")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error detail message")
