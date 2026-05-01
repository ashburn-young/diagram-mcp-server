import asyncio
import os

from infrastructure_diagram_mcp_server.diagrams_tools import generate_diagram


DIAGRAM_CODE = r"""
with Diagram(
    "Enterprise Lakehouse (Azure Icons)",
    direction="TB",
    show=False,
):
    with Cluster("Enterprise & External Sources"):
        sap = Server("SAP ECC / S4 / BW")
        pos = Server("POS & Store Systems")
        ecom = Server("ECommerce")
        scm = Server("Supply Chain / Logistics")
        crm = Server("CRM & Marketing")
        iot_events = Users("IoT / RFID / Events")
        partners = Users("3rdParty / Partners")

        with Cluster("AWS Data"):
            aws_s3 = S3("S3")
            aws_redshift = Redshift("Redshift")

    with Cluster("Ingestion & Integration"):
        sap_cdc = DataFactories("SAP ODP / CDC")
        adf = DataFactories("Azure Data Factory\n(Batch / CDC)")
        event_hubs = EventHubs("Event Hubs")
        asa = StreamAnalyticsJobs("Stream Analytics")
        apim = APIManagement("API Management")

    with Cluster("ADLS Gen2 (Storage Only)"):
        landing = DataLakeStorage("Landing Files")
        delta_log = Storage("_delta_log")

    with Cluster("Azure Databricks Lakehouse"):
        uc = Databricks("Unity Catalog\n(Domains = Catalogs)")
        dlt = Databricks("Delta Live Tables\n(Quality, Lineage, Promotion)")

        with Cluster("Bronze"):
            bronze = Storage("Raw Delta Tables")

        with Cluster("Silver"):
            silver = Storage("Validated / Conformed Tables")

        with Cluster("Gold"):
            gold = Storage("Certified Data Products\n(BI + AI Contract)")

    with Cluster("Knowledge, AI / ML & GenAI"):
        feat = Rack("Feature Engineering")
        aml = MachineLearningServiceWorkspaces("Azure Machine Learning")
        aoai = AzureOpenAI("Azure OpenAI\n(RAG, Agents)")
        vec = CosmosDb("Vector Store")

    with Cluster("Consumption & Data Marketplace"):
        pbi = PowerBiEmbedded("Power BI / Embedded")
        fabric = AnalysisServices("Microsoft Fabric\n(ReadOnly Analytics)")
        apps = AppServices("Custom Apps / APIs")
        cop = Users("Copilots & Chatbots")

    with Cluster("Governance & Security"):
        purview = AzurePurviewAccounts("Microsoft Purview")
        entra = AzureActiveDirectory("Entra ID")
        policy = SecurityCenter("Azure Policy / RBAC / ABAC")
        dq = Rack("Data Quality & Contracts")

    with Cluster("Platform Engineering"):
        cicd = Pipelines("CI/CD (Azure DevOps)")
        mon = Monitor("Azure Monitor & Cost Mgmt")
        net = PrivateEndpoint("Private Endpoints / VNETs")

    # Sources -> Ingestion
    sap >> sap_cdc >> adf
    ecom >> adf
    scm >> adf
    partners >> adf
    aws_s3 >> adf
    aws_redshift >> adf

    pos >> event_hubs
    iot_events >> event_hubs

    crm >> apim

    # Ingestion -> Storage
    adf >> landing
    apim >> landing

    event_hubs >> asa
    event_hubs >> landing
    asa >> landing

    # Storage -> Lakehouse
    landing >> bronze >> silver >> gold
    dlt >> [bronze, silver, gold]

    # Gold -> AI + Consumption
    gold >> [feat, aoai, pbi, fabric]
    feat >> aml
    aoai >> vec
    aoai >> cop
    aml >> apps

    # Governance & Ops (dashed influence lines)
    entra >> Edge(style="dashed") >> [uc, aml, pbi]
    purview >> Edge(style="dashed") >> [uc, gold]
    dq >> Edge(style="dashed") >> dlt
    policy >> Edge(style="dashed") >> uc

    mon >> Edge(style="dashed") >> [uc, aoai]
    cicd >> Edge(style="dashed") >> uc
    net >> Edge(style="dashed") >> landing
"""


async def main() -> None:
    result = await generate_diagram(
        code=DIAGRAM_CODE,
        filename="enterprise_lakehouse_azure_icons",
        timeout=90,
        workspace_dir=os.getcwd(),
    )
    print(result.model_dump())
    if result.status != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
