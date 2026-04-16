"""ad group criterion label server module."""

from src.services.ad_group.ad_group_criterion_label_service import (
    register_ad_group_criterion_label_tools,
)
from src.servers import create_server

ad_group_criterion_label_server = create_server(register_ad_group_criterion_label_tools)
