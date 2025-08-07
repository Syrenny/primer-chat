from pydantic import BaseModel, ConfigDict


class ApiChunksResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    xyxy: list[float, float, float, float]
    start_line: int
    end_line: int
    page: int
    filename: str
