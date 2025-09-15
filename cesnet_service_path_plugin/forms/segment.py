import logging
from circuits.models import Circuit, Provider
from dcim.models import Location, Site
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields
from utilities.forms.widgets.datetime import DatePicker

from cesnet_service_path_plugin.models import Segment
from cesnet_service_path_plugin.models.custom_choices import StatusChoices
from cesnet_service_path_plugin.utils import process_path_data, determine_file_format_from_extension
from cesnet_service_path_plugin.models.segment_types import SegmentTypeChoices, SEGMENT_TYPE_SCHEMAS


class SegmentForm(NetBoxModelForm):
    comments = CommentField(required=False, label="Comments", help_text="Comments")
    status = forms.ChoiceField(required=True, choices=StatusChoices, initial=None)
    provider_segment_contract = forms.CharField(
        label=" Contract", required=False, help_text="Provider Segment Contract"
    )
    provider_segment_id = forms.CharField(label=" ID", required=False, help_text="Provider Segment ID")
    provider_segment_name = forms.CharField(label="Name", required=False, help_text="Provider Segment Name")
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=True,
        label=_("Provider"),
        selector=True,
    )
    install_date = forms.DateField(widget=DatePicker(), required=False)
    termination_date = forms.DateField(widget=DatePicker(), required=False)

    site_a = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label=_("Site A"),
        selector=True,
    )
    location_a = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            "site_id": "$site_a",
        },
        label=_("Location A"),
    )
    site_b = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label=_("Site B"),
        selector=True,
    )
    location_b = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            "site_id": "$site_b",
        },
        label=_("Location B"),
    )

    # GIS Fields
    path_file = forms.FileField(
        required=False,
        label=_("Path Geometry File"),
        help_text="Upload a file containing the path geometry. Supported formats: GeoJSON (.geojson, .json), KML (.kml), KMZ (.kmz)",
        widget=forms.FileInput(attrs={"accept": ".geojson,.json,.kml,.kmz"}),
    )

    path_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label=_("Path Notes"),
        help_text="Additional notes about the path geometry",
    )

    segment_type = forms.ChoiceField(
        choices=SegmentTypeChoices,
        initial=SegmentTypeChoices.DARK_FIBER,
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "onchange": "updateTypeSpecificFields(this.value)"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add dynamic fields for type-specific data
        self.add_type_specific_fields()

        # If editing existing segment with path data, show some info
        if self.instance.pk and self.instance.path_geometry:
            help_text = f"Current path: {self.instance.path_source_format or 'Unknown format'}"
            if self.instance.path_length_km:
                help_text += f" ({self.instance.path_length_km} km)"
            help_text += ". Upload a new file to replace the current path."
            self.fields["path_file"].help_text = help_text

        # Pre-populate type-specific fields if editing existing object
        if self.instance.pk and self.instance.type_specific_data:
            self.populate_type_specific_fields()

        # DEBUG
        vals = (*[f"type_{field}" for schema in SEGMENT_TYPE_SCHEMAS.values() for field in schema.keys()],)
        logging.debug(f"DEBUG: SegmentForm __init__ fields: {vals}")
        for key, val in self.instance.type_specific_data.items():
            logging.debug(f"DEBUG: SegmentForm __init__ type_specific_data: {key} = {val}")

    def add_type_specific_fields(self):
        """Dynamically add fields for all segment types"""
        for segment_type, schema in SEGMENT_TYPE_SCHEMAS.items():
            for field_name, field_config in schema.items():
                form_field_name = f"type_{field_name}"

                # Create appropriate form field based on schema
                if field_config["type"] == "decimal":
                    field = forms.DecimalField(
                        label=field_config["label"],
                        required=False,
                        min_value=field_config.get("min_value"),
                        max_value=field_config.get("max_value"),
                        max_digits=field_config.get("max_digits", 8),
                        decimal_places=field_config.get("decimal_places", 2),
                        help_text=field_config.get("help_text", ""),
                        widget=forms.NumberInput(
                            attrs={"class": "form-control", "data-type-field": segment_type, "step": "any"}
                        ),
                    )
                elif field_config["type"] == "integer":
                    field = forms.IntegerField(
                        label=field_config["label"],
                        required=False,
                        min_value=field_config.get("min_value"),
                        max_value=field_config.get("max_value"),
                        help_text=field_config.get("help_text", ""),
                        widget=forms.NumberInput(attrs={"class": "form-control", "data-type-field": segment_type}),
                    )
                elif field_config["type"] == "choice":
                    choices = [("", "--------")] + [(c, c) for c in field_config.get("choices", [])]
                    field = forms.ChoiceField(
                        label=field_config["label"],
                        required=False,
                        choices=choices,
                        help_text=field_config.get("help_text", ""),
                        widget=forms.Select(attrs={"class": "form-select", "data-type-field": segment_type}),
                    )
                else:  # string
                    field = forms.CharField(
                        label=field_config["label"],
                        required=False,
                        max_length=field_config.get("max_length", 255),
                        help_text=field_config.get("help_text", ""),
                        widget=forms.TextInput(attrs={"class": "form-control", "data-type-field": segment_type}),
                    )

                self.fields[form_field_name] = field

    def populate_type_specific_fields(self):
        """Populate type-specific fields with existing data"""
        type_data = self.instance.type_specific_data or {}
        for field_name, value in type_data.items():
            form_field_name = f"type_{field_name}"
            if form_field_name in self.fields:
                self.fields[form_field_name].initial = value

    def _validate_dates(self, install_date, termination_date):
        """
        WARN: Workaround InlineFields does not display ValidationError messages in the field.
        It has to be raise as popup.

        Validate that install_date is not later than termination_date.
        """
        if install_date and termination_date:
            if install_date > termination_date:
                self.add_error(
                    field=None,  # 'install_date', 'termination_date', # CANNOT BE DEFINED
                    error=[
                        _("Install date cannot be later than termination date."),
                        _("Termination date cannot be earlier than install date."),
                    ],
                )

    def _process_path_file(self, uploaded_file):
        """Process uploaded path file using GeoPandas and return MultiLineString geometry"""
        if not uploaded_file:
            return None, None

        try:
            # Determine format from file extension
            file_format = determine_file_format_from_extension(uploaded_file.name)

            # Process the file using GeoPandas
            multilinestring = process_path_data(uploaded_file, file_format)

            return multilinestring, file_format

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error processing file '{uploaded_file.name}': {str(e)}")

    def clean(self):
        super().clean()

        install_date = self.cleaned_data.get("install_date")
        termination_date = self.cleaned_data.get("termination_date")

        self._validate_dates(install_date, termination_date)

        # Process path file if uploaded
        path_file = self.cleaned_data.get("path_file")
        if path_file:
            try:
                path_geometry, file_format = self._process_path_file(path_file)
                self.cleaned_data["processed_path_geometry"] = path_geometry
                self.cleaned_data["detected_format"] = file_format
            except ValidationError as e:
                self.add_error("path_file", e)

        segment_type = self.cleaned_data.get("segment_type")

        if segment_type:
            # Collect type-specific data from form
            type_specific_data = {}
            schema = SEGMENT_TYPE_SCHEMAS.get(segment_type, {})

            for field_name, field_config in schema.items():
                form_field_name = f"type_{field_name}"
                value = self.cleaned_data.get(form_field_name)

                # Only include non-empty values
                if value is not None and value != "":
                    type_specific_data[field_name] = value
                elif field_config.get("required", False):
                    self.add_error(form_field_name, "This field is required for this segment type.")

            self.cleaned_data["type_specific_data"] = type_specific_data

        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle path geometry
        if "processed_path_geometry" in self.cleaned_data:
            instance.path_geometry = self.cleaned_data["processed_path_geometry"]
            instance.path_source_format = self.cleaned_data.get("detected_format")
            instance.path_notes = self.cleaned_data.get("path_notes", "")
        elif not self.cleaned_data.get("path_file"):
            # Only clear path data if no file was uploaded and we're not preserving existing data
            # This allows editing other fields without losing path data
            pass

        # Handle type-specific data
        if "type_specific_data" in self.cleaned_data:
            instance.type_specific_data = self.cleaned_data["type_specific_data"]

        if commit:
            instance.save()
            self.save_m2m()  # This is required to save many-to-many fields like tags

        return instance

    class Meta:
        model = Segment
        fields = [
            "name",
            "segment_type",
            "status",
            "network_label",
            "install_date",
            "termination_date",
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            "site_a",
            "location_a",
            "site_b",
            "location_b",
            "path_file",
            "path_notes",
            "tags",
            "comments",
        ]

    fieldsets = (
        FieldSet(
            "name",
            "segment_type",
            "network_label",
            "status",
            InlineFields("install_date", "termination_date", label="Dates"),
            name="Basic Information",
        ),
        FieldSet(
            "provider",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            name="Provider",
        ),
        FieldSet(
            "site_a",
            "location_a",
            name="Side A",
        ),
        FieldSet(
            "site_b",
            "location_b",
            name="Side B",
        ),
        # Dynamic fieldset for type-specific fields (removed 'classes' parameter)
        FieldSet(
            # Fields will be dynamically shown/hidden via JavaScript
            *[f"type_{field}" for schema in SEGMENT_TYPE_SCHEMAS.values() for field in schema.keys()],
            name="Segment Type Technical Specifications",
        ),
        FieldSet(
            "path_file",
            "path_notes",
            name="Path Geometry",
        ),
        FieldSet(
            "tags",
            # "comments", # Comment Is always rendered! If uncommented, it will be rendered twice
            name="Miscellaneous",
        ),
    )


class SegmentFilterForm(NetBoxModelFilterSetForm):
    model = Segment

    name = forms.CharField(required=False)
    status = forms.MultipleChoiceField(required=False, choices=StatusChoices, initial=None)
    network_label = forms.CharField(required=False)

    tag = TagFilterField(model)

    site_a_id = DynamicModelMultipleChoiceField(queryset=Site.objects.all(), required=False, label=_("Site A"))
    location_a_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            "site_id": "$site_a_id",
        },
        label=_("Location A"),
    )

    site_b_id = DynamicModelMultipleChoiceField(queryset=Site.objects.all(), required=False, label=_("Site B"))
    location_b_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            "site_id": "$site_b_id",
        },
        label=_("Location B"),
    )

    install_date__gte = forms.DateTimeField(required=False, label=("Install Date From"), widget=DatePicker())
    install_date__lte = forms.DateTimeField(required=False, label=("Install Date Till"), widget=DatePicker())
    termination_date__gte = forms.DateTimeField(required=False, label=("Termination Date From"), widget=DatePicker())
    termination_date__lte = forms.DateTimeField(required=False, label=("Termination Date Till"), widget=DatePicker())

    provider_id = DynamicModelMultipleChoiceField(queryset=Provider.objects.all(), required=False, label=_("Provider"))
    provider_segment_id = forms.CharField(required=False, label=_("Provider Segment ID"))
    provider_segment_name = forms.CharField(required=False, label=_("Provider Segment Name"))
    provider_segment_contract = forms.CharField(required=False, label=_("Provider Segment Contract"))

    at_any_site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_("At any Site"),
    )

    at_any_location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_("At any Location"),
    )

    circuits = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        required=False,
        label=_("Circuits"),
    )

    # Updated filter for segments with path data
    has_path_data = forms.MultipleChoiceField(
        required=False,
        choices=[
            (True, "Yes"),
            (False, "No"),
        ],
        label=_("Has Path Data"),
        help_text="Filter segments that have path geometry data",
    )

    fieldsets = (
        FieldSet("q", "tag", "filter_id", name="Misc"),
        FieldSet("name", "status", "network_label", "has_path_data", name="Basic"),
        FieldSet(
            "provider_id",
            "provider_segment_id",
            "provider_segment_name",
            "provider_segment_contract",
            name="Provider",
        ),
        FieldSet(
            "install_date__gte",
            "install_date__lte",
            "termination_date__gte",
            "termination_date__lte",
            name="Dates",
        ),
        FieldSet("circuits", "at_any_site", "at_any_location", name="Extra"),
        FieldSet("site_a_id", "location_a_id", name="Side A"),
        FieldSet("site_b_id", "location_b_id", name="Side B"),
    )
