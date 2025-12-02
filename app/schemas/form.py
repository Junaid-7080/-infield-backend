"""
Pydantic schemas for Form and FormField models.
"""
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class FieldType(str, Enum):
    """Field types matching the database enum"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    DATE = "date"
    TIME = "time"
    TABLE = "table"
    SIGNATURE = "signature"
    SECTION = "section"


# Configuration models for complex field types

class TableColumn(BaseModel):
    """Configuration for a single table column"""
    id: str = Field(..., description="Unique column identifier")
    label: str = Field(..., max_length=200, description="Column display label")
    type: str = Field(..., description="Column field type (text, number, date, select, checkbox, etc.)")
    placeholder: Optional[str] = Field(None, max_length=200)
    required: bool = False
    options: Optional[List[str]] = Field(None, description="Options for select/radio columns")
    width: Optional[str] = Field(None, description="Column width (e.g., '150px', '20%')")
    defaultValue: Optional[str] = Field(None, alias="defaultValue")

    class Config:
        populate_by_name = True


class TableFieldConfig(BaseModel):
    """Configuration for table field type"""
    columns: List[TableColumn] = Field(..., min_length=1, description="Table column definitions")
    minRows: Optional[int] = Field(None, ge=0, alias="minRows", description="Minimum number of rows")
    maxRows: Optional[int] = Field(None, ge=1, alias="maxRows", description="Maximum number of rows")
    addButtonText: Optional[str] = Field(None, alias="addButtonText", description="Custom text for add button")
    removeButtonText: Optional[str] = Field(None, alias="removeButtonText")
    showRowNumbers: bool = Field(True, alias="showRowNumbers", description="Show row numbers")

    class Config:
        populate_by_name = True


class SignatureFieldConfig(BaseModel):
    """Configuration for signature field type"""
    width: int = Field(400, ge=200, le=800, description="Canvas width in pixels")
    height: int = Field(200, ge=100, le=400, description="Canvas height in pixels")
    penColor: str = Field("#000000", alias="penColor", pattern=r"^#[0-9A-Fa-f]{6}$", description="Pen color (hex)")
    backgroundColor: str = Field("#ffffff", alias="backgroundColor", pattern=r"^#[0-9A-Fa-f]{6}$", description="Background color (hex)")

    class Config:
        populate_by_name = True


class SectionFieldConfig(BaseModel):
    """Configuration for section field type"""
    collapsible: bool = Field(True, description="Whether section can be collapsed")
    defaultExpanded: bool = Field(True, alias="defaultExpanded", description="Whether section is expanded by default")

    class Config:
        populate_by_name = True


# FormField Schemas
class FormFieldBase(BaseModel):
    """Base schema for form fields"""
    field_type: FieldType
    label: str = Field(..., max_length=200)
    placeholder: Optional[str] = Field(None, max_length=200)
    help_text: Optional[str] = None
    required: bool = False
    options: Optional[List[str]] = None
    order: int = 0
    validation_rules: Optional[dict] = None
    field_config: Optional[dict] = None

    @field_validator('field_config')
    @classmethod
    def validate_field_config(cls, v, info):
        """Validate field_config structure matches field_type"""
        if v is None:
            return v

        field_type = info.data.get('field_type')

        if field_type == FieldType.TABLE:
            try:
                TableFieldConfig(**v)
            except ValidationError as e:
                raise ValueError(f"Invalid table field configuration: {e}")

        elif field_type == FieldType.SIGNATURE:
            try:
                SignatureFieldConfig(**v)
            except ValidationError as e:
                raise ValueError(f"Invalid signature field configuration: {e}")

        elif field_type == FieldType.SECTION:
            try:
                SectionFieldConfig(**v)
            except ValidationError as e:
                raise ValueError(f"Invalid section field configuration: {e}")

        return v


class FormFieldCreate(FormFieldBase):
    """Schema for creating a form field"""
    pass


class FormFieldUpdate(BaseModel):
    """Schema for updating a form field"""
    field_type: Optional[FieldType] = None
    label: Optional[str] = Field(None, max_length=200)
    placeholder: Optional[str] = Field(None, max_length=200)
    help_text: Optional[str] = None
    required: Optional[bool] = None
    options: Optional[List[str]] = None
    order: Optional[int] = None
    validation_rules: Optional[dict] = None
    field_config: Optional[dict] = None


class FormFieldResponse(FormFieldBase):
    """Schema for form field response"""
    id: int
    form_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Form Schemas
class FormBase(BaseModel):
    """Base schema for forms"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    header: Optional[dict] = None


class FormCreate(FormBase):
    """Schema for creating a form"""
    fields: List[FormFieldCreate] = Field(default_factory=list)
    is_published: bool = False
    allow_multiple_submissions: bool = True
    requires_approval: bool = False


class FormUpdate(BaseModel):
    """Schema for updating a form"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    header: Optional[dict] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    allow_multiple_submissions: Optional[bool] = None
    requires_approval: Optional[bool] = None


class FormResponse(FormBase):
    """Schema for form response"""
    id: int
    tenant_id: int
    created_by: Optional[int]
    is_active: bool
    is_published: bool
    version: int
    allow_multiple_submissions: bool
    requires_approval: bool
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    fields: List[FormFieldResponse] = []

    class Config:
        from_attributes = True


class FormListResponse(BaseModel):
    """Schema for paginated form list"""
    items: List[FormResponse]
    total: int
    skip: int
    limit: int


class FormPublishRequest(BaseModel):
    """Schema for publishing a form"""
    is_published: bool = True


# Helper function for field_config validation

def validate_field_config_structure(field_type: FieldType, config: dict) -> bool:
    """
    Helper function to validate field_config matches field_type.
    Returns True if valid, raises ValidationError if invalid.

    Args:
        field_type: The type of field (table, signature, section)
        config: The configuration dictionary to validate

    Returns:
        True if valid

    Raises:
        ValueError: If config doesn't match field_type requirements
    """
    if config is None:
        return True

    try:
        if field_type == FieldType.TABLE:
            TableFieldConfig(**config)
        elif field_type == FieldType.SIGNATURE:
            SignatureFieldConfig(**config)
        elif field_type == FieldType.SECTION:
            SectionFieldConfig(**config)
        return True
    except ValidationError as e:
        raise ValueError(f"Invalid {field_type.value} field configuration: {str(e)}")
