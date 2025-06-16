from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from database import (
    get_db_engine,
    get_table_columns,
    check_table_exists,
    query_table_data,
)
from models import TableDataResponse, ColumnInfo, PaginationMetadata, ErrorResponse

# Initialize FastAPI app
app = FastAPI(
    title="Warehouse API",
    description="API for querying PostgreSQL warehouse data",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify the Bearer token.

    Args:
        credentials: Bearer token credentials

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is invalid
    """
    if credentials.credentials != config.api.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


@app.get(
    "/api/data",
    response_model=TableDataResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_table_data(
    schema_name: str = Query(..., description="PostgreSQL schema name"),
    table_name: str = Query(..., description="Table name"),
    district: Optional[str] = Query(None, description="Optional district filter"),
    page: int = Query(1, description="Page number (1-based)", ge=1),
    page_size: int = Query(100, description="Number of items per page", ge=1, le=1000),
    authenticated: bool = Depends(verify_token),
):
    """
    Get paginated data from a PostgreSQL table with optional district filtering.

    Args:
        schema_name: PostgreSQL schema name
        table_name: Table name
        district: Optional district filter
        page: Page number (1-based)
        page_size: Number of items per page
        authenticated: Authentication dependency

    Returns:
        TableDataResponse with data, columns, and pagination metadata

    Raises:
        HTTPException: If table doesn't exist or other errors occur
    """
    try:
        engine = get_db_engine()

        # Check if table exists
        if not check_table_exists(engine, schema_name, table_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{schema_name}.{table_name}' not found",
            )

        # Get column information
        columns = get_table_columns(engine, schema_name, table_name)
        if not columns:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No columns found for table '{schema_name}.{table_name}'",
            )

        # Query table data with pagination and optional district filter
        rows, total_count = query_table_data(
            engine,
            schema_name,
            table_name,
            columns,
            district_filter=district,
            page=page,
            page_size=page_size,
        )

        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size

        # Create response
        return TableDataResponse(
            data=rows,
            columns=[ColumnInfo(**col) for col in columns],
            pagination=PaginationMetadata(
                total_items=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
