# Warehouse API

A FastAPI application that exposes a GET API endpoint to query a PostgreSQL warehouse.

## Features

- Query PostgreSQL tables with schema and table name parameters
- Optional district filtering
- Pagination support
- Bearer token authentication
- Configurable pagination column

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your PostgreSQL credentials and API token:
   ```
   # Database Configuration
   DB_HOST=your_host
   DB_PORT=your_port
   DB_NAME=your_warehouse_db
   DB_USER=your_username
   DB_PASSWORD=your_password

   # API Configuration
   PAGINATION_COLUMN=id
   API_TOKEN=your_secret_token
   ```

## Running the API

Start the API server:

```bash
python main.py
```

This will start the server at http://localhost:8000.

Alternatively, you can use uvicorn directly:

```bash
uvicorn main:app --reload
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### GET /api/data

Get paginated data from a PostgreSQL table with optional district filtering.

#### Query Parameters

- `schema_name` (required): PostgreSQL schema name
- `table_name` (required): Table name
- `district` (optional): District filter value
- `page` (optional, default: 1): Page number (1-based)
- `page_size` (optional, default: 100): Number of items per page (max: 1000)

#### Authentication

This endpoint requires Bearer token authentication. Include the following header in your request:

```
Authorization: Bearer your_api_token
```

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/data?schema_name=public&table_name=users&page=1&page_size=10" \
     -H "Authorization: Bearer your_api_token"
```

#### Example Response

```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "district": "North"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "district": "South"
    }
  ],
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "nullable": false
    },
    {
      "name": "name",
      "type": "character varying",
      "nullable": true
    },
    {
      "name": "district",
      "type": "character varying",
      "nullable": true
    }
  ],
  "pagination": {
    "total_items": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

### GET /health

Health check endpoint.

#### Example Request

```bash
curl -X GET "http://localhost:8000/health"
```

#### Example Response

```json
{
  "status": "ok"
}
```

## Configuration

### Pagination Column

By default, the API uses the `id` column for pagination. You can change this by setting the `PAGINATION_COLUMN` environment variable in the `.env` file.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 401 Unauthorized: Invalid or missing authentication token
- 404 Not Found: Table or columns not found
- 500 Internal Server Error: Database connection issues or other errors
