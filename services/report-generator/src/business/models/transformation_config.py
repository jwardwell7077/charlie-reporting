"""Transformation Configuration Domain Model
Represents configuration options for data transformations
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DateFormat(Enum):
    """Supported date formats for transformation"""
    ISO_8601 = "%Y-%m-%d"
    US_FORMAT = "%m/%d/%Y"
    EU_FORMAT = "%d/%m/%Y"
    TIMESTAMP = "%Y-%m-%d %H:%M:%S"


class TextCase(Enum):
    """Text case transformation options"""
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"
    CAPITALIZE = "capitalize"
    NONE = "none"


class NumericFormat(Enum):
    """Numeric formatting options"""
    INTEGER = "integer"
    DECIMAL_2 = "decimal_2"
    DECIMAL_4 = "decimal_4"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"


@dataclass


class TransformationRule:
    """Represents a single transformation rule to apply to data
    """
    rule_type: str
    target_columns: list[str]
    parameters: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    is_active: bool = True

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a transformation parameter value"""
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value: Any):
        """Set a transformation parameter"""
        self.parameters[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary representation"""
        return {
            "rule_type": self.rule_type,
            "target_columns": self.target_columns,
            "parameters": self.parameters,
            "description": self.description,
            "is_active": self.is_active
        }


@dataclass


class TransformationConfig:
    """Configuration for CSV data transformations
    """
    # Date transformation settings
    date_format: str = DateFormat.ISO_8601.value
    auto_detect_dates: bool = True
    date_columns: list[str] = field(default_factory=list)

    # Numeric transformation settings
    numeric_precision: int = 2
    numeric_format: str = NumericFormat.DECIMAL_2.value
    auto_detect_numeric: bool = True
    numeric_columns: list[str] = field(default_factory=list)

    # Text transformation settings
    text_case: str = TextCase.NONE.value
    trim_whitespace: bool = True
    text_columns: list[str] = field(default_factory=list)

    # Data cleaning settings
    remove_duplicates: bool = False
    duplicate_subset_columns: list[str] = field(default_factory=list)
    handle_missing_values: bool = True
    missing_value_strategy: str = "skip"  # skip, fill, remove
    fill_value: Any | None = None

    # Column mapping and renaming
    column_mappings: dict[str, str] = field(default_factory=dict)
    columns_to_drop: list[str] = field(default_factory=list)

    # Validation settings
    required_columns: list[str] = field(default_factory=list)
    max_rows: int | None = None
    min_rows: int | None = None

    # Custom transformation rules
    custom_rules: list[TransformationRule] = field(default_factory=list)

    def add_custom_rule(self, rule: TransformationRule):
        """Add a custom transformation rule"""
        self.custom_rules.append(rule)

    def remove_custom_rule(self, rule_type: str, target_columns: list[str]) -> bool:
        """Remove a custom transformation rule"""
        for i, rule in enumerate(self.custom_rules):
            if rule.rule_type == rule_type and rule.target_columns == target_columns:
                del self.custom_rules[i]
                return True
        return False

    def get_active_rules(self) -> list[TransformationRule]:
        """Get only active transformation rules"""
        return [rule for rule in self.custom_rules if rule.is_active]

    def set_date_format(self, date_format: DateFormat):
        """Set the date format using enum"""
        self.dateformat = date_format.value

    def set_text_case(self, text_case: TextCase):
        """Set the text case using enum"""
        self.textcase = text_case.value

    def set_numeric_format(self, numeric_format: NumericFormat):
        """Set the numeric format using enum"""
        self.numericformat = numeric_format.value

    def add_column_mapping(self, old_name: str, new_name: str):
        """Add a column name mapping"""
        self.column_mappings[old_name] = new_name

    def remove_column_mapping(self, old_name: str) -> bool:
        """Remove a column name mapping"""
        if old_name in self.column_mappings:
            del self.column_mappings[old_name]
            return True
        return False

    def add_required_column(self, column_name: str):
        """Add a required column"""
        if column_name not in self.required_columns:
            self.required_columns.append(column_name)

    def remove_required_column(self, column_name: str) -> bool:
        """Remove a required column"""
        if column_name in self.required_columns:
            self.required_columns.remove(column_name)
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            "date_format": self.date_format,
            "auto_detect_dates": self.auto_detect_dates,
            "date_columns": self.date_columns,
            "numeric_precision": self.numeric_precision,
            "numeric_format": self.numeric_format,
            "auto_detect_numeric": self.auto_detect_numeric,
            "numeric_columns": self.numeric_columns,
            "text_case": self.text_case,
            "trim_whitespace": self.trim_whitespace,
            "text_columns": self.text_columns,
            "remove_duplicates": self.remove_duplicates,
            "duplicate_subset_columns": self.duplicate_subset_columns,
            "handle_missing_values": self.handle_missing_values,
            "missing_value_strategy": self.missing_value_strategy,
            "fill_value": self.fill_value,
            "column_mappings": self.column_mappings,
            "columns_to_drop": self.columns_to_drop,
            "required_columns": self.required_columns,
            "max_rows": self.max_rows,
            "min_rows": self.min_rows,
            "custom_rules": [rule.to_dict() for rule in self.custom_rules]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'TransformationConfig':
        """Create configuration from dictionary"""
        # Extract custom rules and convert them back to objects
        customrules_data = data.pop('custom_rules', [])
        customrules = []

        for rule_data in custom_rules_data:
            rule = TransformationRule(
                rule_type=rule_data['rule_type'],
                target_columns=rule_data['target_columns'],
                parameters=rule_data.get('parameters', {}),
                description=rule_data.get('description'),
                is_active=rule_data.get('is_active', True)
            )
            custom_rules.append(rule)

        # Create config instance
        config = cls(**data)
        config.customrules = custom_rules

        return config

    @classmethod
    def default_config(cls) -> 'TransformationConfig':
        """Create a default transformation configuration"""
        return cls(
            date_format=DateFormat.ISO_8601.value,
            auto_detect_dates=True,
            numeric_precision=2,
            auto_detect_numeric=True,
            text_case=TextCase.NONE.value,
            trim_whitespace=True,
            remove_duplicates=False,
            handle_missing_values=True,
            missing_value_strategy="skip"
        )


@dataclass


class TransformationResult:
    """Result of applying transformations to data
    """
    success: bool
    transformed_data: Any | None = None  # Could be DataFrame or other data structure
    applied_rules: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    error_message: str | None = None
    processing_time_seconds: float | None = None

    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)

    def add_error(self, error: str):
        """Add an error message and mark as failed"""
        self.errors.append(error)
        self.success = False

    def add_applied_rule(self, rule_description: str):
        """Add a description of an applied rule"""
        self.applied_rules.append(rule_description)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary representation"""
        result = {
            "success": self.success,
            "applied_rules": self.applied_rules,
            "warnings": self.warnings,
            "errors": self.errors,
            "error_message": self.error_message,
            "processing_time_seconds": self.processing_time_seconds
        }

        # Don't include the actual data in the dictionary to avoid serialization issues
        if self.transformed_data is not None:
            result["has_data"] = True
            result["data_type"] = type(self.transformed_data).__name__
        else:
            result["has_data"] = False

        return result
