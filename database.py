from typing import Dict, List, Optional, Tuple, Any
import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from config import config


def get_db_engine() -> Engine:
    """Create and return a SQLAlchemy engine instance."""
    return sa.create_engine(config.get_db_url())


def get_table_columns(
    engine: Engine, schema_name: str, table_name: str
) -> List[Dict[str, Any]]:
    """
    Get column information for a specific table from information_schema.

    Args:
        engine: SQLAlchemy engine
        schema_name: Schema name
        table_name: Table name

    Returns:
        List of column information dictionaries
    """
    query = sa.text(
        """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = :schema_name AND table_name = :table_name
        ORDER BY ordinal_position
        """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(
                query, {"schema_name": schema_name, "table_name": table_name}
            )
            columns = [
                {
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2] == "YES",
                }
                for row in result
            ]
            return columns
    except SQLAlchemyError as e:
        raise ValueError(f"Error fetching column information: {str(e)}")


def check_table_exists(engine: Engine, schema_name: str, table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        engine: SQLAlchemy engine
        schema_name: Schema name
        table_name: Table name

    Returns:
        True if the table exists, False otherwise
    """
    query = sa.text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = :schema_name AND table_name = :table_name
        )
        """
    )

    try:
        with engine.connect() as conn:
            result = conn.execute(
                query, {"schema_name": schema_name, "table_name": table_name}
            )
            return result.scalar()
    except SQLAlchemyError as e:
        raise ValueError(f"Error checking table existence: {str(e)}")


def query_table_data(
    engine: Engine,
    schema_name: str,
    table_name: str,
    columns: List[Dict[str, Any]],
    district_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Query data from a table with pagination and optional district filter.

    Args:
        engine: SQLAlchemy engine
        schema_name: Schema name
        table_name: Table name
        columns: List of column information dictionaries
        district_filter: Optional district filter value
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        Tuple of (list of row dictionaries, total count)
    """
    # Check if district column exists
    column_names = [col["name"] for col in columns]
    has_district = "district" in column_names

    # Get pagination column
    pagination_column = config.db.pagination_column
    if pagination_column not in column_names:
        raise ValueError(
            f"Pagination column '{pagination_column}' not found in table columns"
        )

    # Build the base query
    base_query = f'SELECT * FROM "{schema_name}"."{table_name}"'
    count_query = f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"'

    # Add district filter if provided and column exists
    where_clause = ""
    params = {}
    if district_filter and has_district:
        where_clause = " WHERE district = :district"
        params["district"] = district_filter

    # Add pagination
    offset = (page - 1) * page_size
    pagination = f" ORDER BY {pagination_column} LIMIT :limit OFFSET :offset"
    params.update({"limit": page_size, "offset": offset})

    # Complete queries
    data_query = base_query + where_clause + pagination
    count_query = count_query + where_clause

    try:
        with engine.connect() as conn:
            # Get total count
            count_result = conn.execute(sa.text(count_query), params)
            total_count = count_result.scalar()

            # Get paginated data
            result = conn.execute(sa.text(data_query), params)
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(result.keys()):
                    row_dict[col] = row[i]
                rows.append(row_dict)

            return rows, total_count
    except SQLAlchemyError as e:
        raise ValueError(f"Error querying table data: {str(e)}")
