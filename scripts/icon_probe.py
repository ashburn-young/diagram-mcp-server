from __future__ import annotations

import json

from infrastructure_diagram_mcp_server.diagrams_tools import list_diagram_icons


def show(provider: str, service: str, wanted: list[str]) -> None:
    resp = list_diagram_icons(provider, service).model_dump()
    icons = resp["providers"].get(provider, {}).get(service, [])
    found = [w for w in wanted if w in icons]
    print(f"{provider}.{service}: total={len(icons)} found={found}")


def main() -> None:
    show(
        "azure",
        "integration",
        [
            "APIManagement",
            "EventHubs",
            "ServiceBus",
            "LogicApps",
            "DataFactories",
            "DataFactory",
            "AzureDataFactory",
        ],
    )
    show(
        "azure",
        "analytics",
        [
            "Databricks",
            "SynapseAnalytics",
            "StreamAnalyticsJobs",
            "AnalysisServices",
            "PowerBi",
            "PowerBI",
        ],
    )
    show(
        "azure",
        "storage",
        [
            "DataLakeStorage",
            "StorageAccounts",
            "BlobStorage",
            "DataLakeStorageGen2",
            "Storage",
        ],
    )
    show("azure", "identity", ["ActiveDirectory", "AzureActiveDirectory"])
    show(
        "azure",
        "security",
        ["KeyVaults", "SecurityCenter", "AzureSecurityCenter", "MicrosoftDefender"],
    )
    show(
        "azure",
        "network",
        [
            "VirtualNetworks",
            "PrivateEndpoints",
            "VPNGateways",
            "ApplicationGateway",
            "LoadBalancers",
        ],
    )
    show(
        "azure",
        "general",
        [
            "Monitor",
            "LogAnalyticsWorkspaces",
            "ResourceGroups",
            "ManagementGroups",
            "User",
            "Subscriptions",
            "Tags",
            "Policy",
        ],
    )
    show(
        "azure",
        "ml",
        [
            "MachineLearningServiceWorkspaces",
            "MachineLearningService",
            "MachineLearning",
        ],
    )
    show("aws", "storage", ["S3"])
    show("aws", "analytics", ["Redshift"])
    show("onprem", "compute", ["Server"])
    show("onprem", "iot", ["IotDevice"])

    # Optional: dump available Azure services for manual mapping
    azure = list_diagram_icons("azure", None).model_dump()["providers"].get("azure", {})
    print("azure services:", json.dumps(sorted(azure.keys()), indent=2))


if __name__ == "__main__":
    main()
