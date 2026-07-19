export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}

export class ApiError extends Error {
  code: string;
  status: number;
  details?: Record<string, unknown> | null;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.name = "ApiError";
    this.status = status;
    this.code = body.code;
    this.details = body.details;
  }
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
