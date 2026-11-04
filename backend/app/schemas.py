from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ResumeResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    size_bytes: int
    created_at: str

class JobPreferenceUpdate(BaseModel):
    target_roles: list[str] = Field(default_factory=list, max_length=20)
    locations: list[str] = Field(default_factory=list, max_length=20)
    skills: list[str] = Field(default_factory=list, max_length=50)
    min_experience_years: int | None = Field(default=None, ge=0, le=60)
    max_experience_years: int | None = Field(default=None, ge=0, le=60)
    min_salary: int | None = Field(default=None, ge=0)
    max_salary: int | None = Field(default=None, ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    work_mode: str = Field(default="any", pattern="^(any|remote|hybrid|onsite)$")

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.min_experience_years is not None and self.max_experience_years is not None and self.min_experience_years > self.max_experience_years:
            raise ValueError("Minimum experience cannot exceed maximum experience")
        if self.min_salary is not None and self.max_salary is not None and self.min_salary > self.max_salary:
            raise ValueError("Minimum salary cannot exceed maximum salary")
        return self

class JobPreferenceResponse(JobPreferenceUpdate):
    model_config = ConfigDict(from_attributes=True)
