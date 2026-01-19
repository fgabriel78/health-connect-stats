from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    client_id: str = Field(..., description="Fitbit Client ID")
    client_secret: str = Field(..., description="Fitbit Client Secret")
    redirect_uri: str = Field("http://localhost:8080", description="Redirect URI for OAuth")
    token_file: Path = Field(default=Path("token.json"), description="Path to store/read token file")
    
    class Config:
        env_file = ".env"
        json_file = "config.json"

    @classmethod
    def load(cls, config_path: str = "config.json") -> "Settings":
        # Pydantic Settings doesn't natively support loading from JSON in this exact way 
        # without extra libraries or custom logic, but for simplicity we will strictly 
        # read the file if it exists and pass it as kwargs, or rely on env vars.
        # This wrapper helps mimic the previous behavior while adding validation.
        import json
        
        config_data = {}
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        
        return cls(**config_data)

settings = Settings.load()
